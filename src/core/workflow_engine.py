"""
工作流引擎模块

负责工作流模板的加载、验证、执行和状态管理。
支持工作流继承、步骤执行、人工审批、DoD检查等功能。
"""

import os
import yaml
import json
import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .state_manager import StateManager
from .config_manager import ConfigManager
from ..services.ai_service import AIService
from ..services.git_service import GitService
from ..services.notify_service import NotifyService
from ..services.service_factory import ServiceFactory


class WorkflowMode(Enum):
    """工作流运行模式"""
    MANUAL = "manual"  # 人工审批模式
    AUTOMATED = "automated"  # 自动化模式


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PAUSED = "paused"  # 等待人工审批


@dataclass
class StepResult:
    """步骤执行结果"""
    step_name: str
    status: StepStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    artifacts: List[str] = field(default_factory=list)


@dataclass
class WorkflowContext:
    """工作流执行上下文"""
    task_id: str
    task_type: str
    mode: WorkflowMode
    config: Dict[str, Any]
    state_manager: StateManager
    ai_service: AIService
    git_service: GitService
    notify_service: NotifyService
    working_dir: str
    artifacts_dir: str
    shortcuts_enabled: bool = True
    current_step: Optional[str] = None
    step_results: Dict[str, StepResult] = field(default_factory=dict)
    shared_data: Dict[str, Any] = field(default_factory=dict)


class WorkflowTemplate:
    """工作流模板类"""
    
    def __init__(self, template_path: str):
        self.template_path = template_path
        self.template_data = {}
        self.base_template = None
        self._load_template()
    
    def _load_template(self):
        """加载工作流模板"""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                self.template_data = yaml.safe_load(f)
            
            # 检查是否有基础模板
            if 'extends' in self.template_data:
                base_path = Path(self.template_path).parent.parent / 'base' / f"{self.template_data['extends']}.yaml"
                if base_path.exists():
                    self.base_template = WorkflowTemplate(str(base_path))
                    self._merge_with_base()
        except Exception as e:
            logging.error(f"加载工作流模板失败 {self.template_path}: {e}")
            raise
    
    def _merge_with_base(self):
        """与基础模板合并"""
        if not self.base_template:
            return
        
        base_data = self.base_template.template_data
        
        # 合并全局配置
        if 'global_config' in base_data:
            if 'global_config' not in self.template_data:
                self.template_data['global_config'] = {}
            self.template_data['global_config'].update(base_data['global_config'])
        
        # 合并步骤模板
        if 'step_templates' in base_data:
            if 'step_templates' not in self.template_data:
                self.template_data['step_templates'] = {}
            self.template_data['step_templates'].update(base_data['step_templates'])
        
        # 合并默认步骤
        if 'default_steps' in base_data:
            if 'default_steps' not in self.template_data:
                self.template_data['default_steps'] = []
            self.template_data['default_steps'].extend(base_data['default_steps'])
    
    def get_step_sequence(self) -> List[Dict[str, Any]]:
        """获取步骤序列"""
        return self.template_data.get('steps_sequence', self.template_data.get('default_steps', []))
    
    def get_step_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """获取步骤模板"""
        return self.template_data.get('step_templates', {}).get(template_name)
    
    def get_global_config(self) -> Dict[str, Any]:
        """获取全局配置"""
        return self.template_data.get('global_config', {})
    
    def get_dod_rules(self) -> Dict[str, Any]:
        """获取DoD规则"""
        return self.template_data.get('dod_rules', {})


class WorkflowEngine:
    """工作流引擎"""
    
    def __init__(self, config_manager: ConfigManager, 
                 ai_service: Optional[AIService] = None,
                 git_service: Optional[GitService] = None,
                 notify_service: Optional[NotifyService] = None):
        """
        初始化工作流引擎
        
        Args:
            config_manager: 配置管理器
            ai_service: AI服务实例（可选，如果不提供则自动创建）
            git_service: Git服务实例（可选，如果不提供则自动创建）
            notify_service: 通知服务实例（可选，如果不提供则自动创建）
        """
        self.config_manager = config_manager
        self.workflows_dir = Path("workflows")
        self.prompts_dir = Path("prompts")
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # 创建服务工厂
        self.service_factory = ServiceFactory(config_manager)
        
        # 服务实例 - 使用依赖注入或自动创建
        self.ai_service = ai_service or self.service_factory.create_ai_service()
        self.git_service = git_service or self.service_factory.create_git_service()
        self.notify_service = notify_service or self.service_factory.create_notify_service()
    
    def load_workflow_template(self, task_type: str) -> WorkflowTemplate:
        """加载工作流模板"""
        template_path = self.workflows_dir / task_type / f"{task_type}_workflow.yaml"
        if not template_path.exists():
            raise FileNotFoundError(f"工作流模板不存在: {template_path}")
        
        return WorkflowTemplate(str(template_path))
    
    def create_workflow_context(self, task_id: str, task_type: str, 
                              task_config: Dict[str, Any], 
                              mode: WorkflowMode = WorkflowMode.MANUAL) -> WorkflowContext:
        """创建工作流执行上下文"""
        # 创建状态管理器
        state_manager = StateManager(self.config_manager)
        
        # 创建工作目录
        working_dir = Path(f"workspace/{task_id}")
        working_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts_dir = working_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        
        return WorkflowContext(
            task_id=task_id,
            task_type=task_type,
            mode=mode,
            config=task_config,
            state_manager=state_manager,
            ai_service=self.ai_service,
            git_service=self.git_service,
            notify_service=self.notify_service,
            working_dir=str(working_dir),
            artifacts_dir=str(artifacts_dir)
        )
    
    async def execute_workflow(self, task_id: str, task_type: str, 
                             task_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作流"""
        try:
            # 加载工作流模板
            template = self.load_workflow_template(task_type)
            
            # 确定运行模式
            mode = self._determine_mode(task_config, template)
            
            # 创建执行上下文
            context = self.create_workflow_context(task_id, task_type, task_config, mode)
            
            # 初始化状态
            await self._initialize_workflow_state(context, template)
            
            # 执行步骤序列
            step_sequence = template.get_step_sequence()
            results = {}
            
            for step_config in step_sequence:
                step_name = step_config['name']
                step_result = await self._execute_step(context, template, step_config)
                results[step_name] = step_result
                
                # 检查是否失败
                if step_result.status == StepStatus.FAILED:
                    await self._handle_failure(context, step_name, step_result)
                    break
            
            # 完成工作流
            await self._finalize_workflow(context, results)
            
            return {
                'status': 'completed',
                'results': results,
                'artifacts': self._collect_artifacts(context)
            }
            
        except Exception as e:
            logging.error(f"工作流执行失败 {task_id}: {e}")
            await self._handle_workflow_error(task_id, task_type, e)
            raise
    
    def _determine_mode(self, task_config: Dict[str, Any], 
                       template: WorkflowTemplate) -> WorkflowMode:
        """确定运行模式"""
        # 优先使用任务配置中的模式
        if 'workflow_mode' in task_config:
            return WorkflowMode(task_config['workflow_mode'])
        
        # 使用模板全局配置中的默认模式
        global_config = template.get_global_config()
        default_mode = global_config.get('default_mode', 'manual')
        return WorkflowMode(default_mode)
    
    async def _initialize_workflow_state(self, context: WorkflowContext, 
                                       template: WorkflowTemplate):
        """初始化工作流状态"""
        # 保存工作流配置到状态
        workflow_state = {
            'task_id': context.task_id,
            'task_type': context.task_type,
            'mode': context.mode.value,
            'template_path': template.template_path,
            'start_time': datetime.now().isoformat(),
            'status': 'running',
            'current_step': None,
            'step_results': {},
            'shared_data': {}
        }
        
        await context.state_manager.save_workflow_state(context.task_id, workflow_state)
        
        # 创建工件目录结构
        self._create_artifact_directories(context)
    
    def _create_artifact_directories(self, context: WorkflowContext):
        """创建工件目录结构"""
        artifacts_dir = Path(context.artifacts_dir)
        
        # 创建时间戳目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp_dir = artifacts_dir / timestamp
        timestamp_dir.mkdir(exist_ok=True)
        
        # 更新上下文中的工件目录
        context.artifacts_dir = str(timestamp_dir)
    
    async def _execute_step(self, context: WorkflowContext, 
                          template: WorkflowTemplate, 
                          step_config: Dict[str, Any]) -> StepResult:
        """执行单个步骤"""
        step_name = step_config['name']
        template_name = step_config.get('template', 'ai_call')
        
        logging.info(f"执行步骤: {step_name} (模板: {template_name})")
        
        # 更新当前步骤
        context.current_step = step_name
        await self._update_workflow_state(context)
        
        # 创建步骤结果
        step_result = StepResult(
            step_name=step_name,
            status=StepStatus.RUNNING,
            start_time=datetime.now()
        )
        
        try:
            # 获取步骤模板
            step_template = template.get_step_template(template_name)
            if not step_template:
                raise ValueError(f"步骤模板不存在: {template_name}")
            
            # 执行步骤
            output = await self._execute_step_template(context, step_template, step_config)
            
            # 更新步骤结果
            step_result.status = StepStatus.COMPLETED
            step_result.output = output
            step_result.end_time = datetime.now()
            
            # 保存工件
            await self._save_step_artifacts(context, step_name, output)
            
        except Exception as e:
            step_result.status = StepStatus.FAILED
            step_result.error = str(e)
            step_result.end_time = datetime.now()
            logging.error(f"步骤执行失败 {step_name}: {e}")
        
        # 更新上下文
        context.step_results[step_name] = step_result
        await self._update_workflow_state(context)
        
        return step_result
    
    async def _execute_step_template(self, context: WorkflowContext,
                                   step_template: Dict[str, Any],
                                   step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行步骤模板"""
        step_type = step_template['type']
        
        if step_type == 'ai_service':
            return await self._execute_ai_step(context, step_template, step_config)
        elif step_type == 'git_service':
            return await self._execute_git_step(context, step_template, step_config)
        elif step_type == 'shell':
            return await self._execute_shell_step(context, step_template, step_config)
        elif step_type == 'data_service':
            return await self._execute_data_step(context, step_template, step_config)
        elif step_type == 'file_service':
            return await self._execute_file_step(context, step_template, step_config)
        else:
            raise ValueError(f"不支持的步骤类型: {step_type}")
    
    async def _execute_ai_step(self, context: WorkflowContext,
                             step_template: Dict[str, Any],
                             step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行AI步骤"""
        # 获取提示词模板
        prompt_template = step_config.get('prompt_template')
        if prompt_template:
            prompt_path = self.prompts_dir / context.task_type / f"{prompt_template}.md"
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
            else:
                prompt_content = step_config.get('prompt', '')
        else:
            prompt_content = step_config.get('prompt', '')
        
        # 准备输入数据
        input_data = {
            'task_description': context.config.get('description', ''),
            'task_config': context.config,
            'shared_data': context.shared_data,
            'step_results': {k: v.output for k, v in context.step_results.items()}
        }
        
        # 调用AI服务
        response = await context.ai_service.call_ai(
            prompt=prompt_content,
            input_data=input_data,
            model=step_config.get('model', 'claude'),
            temperature=step_config.get('temperature', 0.7)
        )
        
        return {
            'ai_response': response,
            'input_data': input_data,
            'model_used': step_config.get('model', 'claude')
        }
    
    async def _execute_git_step(self, context: WorkflowContext,
                              step_template: Dict[str, Any],
                              step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行Git步骤"""
        operation = step_config.get('operation', 'fetch')
        
        if operation == 'fetch':
            return await context.git_service.fetch_code(
                repo_url=step_config['repo_url'],
                branch=step_config.get('branch', 'main'),
                local_path=context.working_dir
            )
        elif operation == 'commit':
            return await context.git_service.commit_changes(
                repo_path=context.working_dir,
                message=step_config['message'],
                files=step_config.get('files', [])
            )
        else:
            raise ValueError(f"不支持的Git操作: {operation}")
    
    async def _execute_shell_step(self, context: WorkflowContext,
                                step_template: Dict[str, Any],
                                step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行Shell步骤"""
        command = step_config['command']
        working_dir = step_config.get('working_dir', context.working_dir)
        
        # 检查命令白名单
        if not self._is_command_allowed(command, step_config.get('whitelist', [])):
            raise ValueError(f"命令不在白名单中: {command}")
        
        # 执行命令
        result = await asyncio.get_event_loop().run_in_executor(
            self.executor,
            self._run_shell_command,
            command,
            working_dir
        )
        
        return {
            'command': command,
            'working_dir': working_dir,
            'stdout': result['stdout'],
            'stderr': result['stderr'],
            'return_code': result['return_code']
        }
    
    def _run_shell_command(self, command: str, working_dir: str) -> Dict[str, Any]:
        """运行Shell命令"""
        import subprocess
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': 'Command timeout',
                'return_code': -1
            }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'return_code': -1
            }
    
    def _is_command_allowed(self, command: str, whitelist: List[str]) -> bool:
        """检查命令是否在白名单中"""
        if not whitelist:
            return False
        
        for allowed_cmd in whitelist:
            if command.startswith(allowed_cmd):
                return True
        
        return False
    
    async def _execute_data_step(self, context: WorkflowContext,
                               step_template: Dict[str, Any],
                               step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行数据步骤"""
        data_source = step_config.get('data_source', 'file')
        
        if data_source == 'file':
            file_path = step_config['file_path']
            with open(file_path, 'r', encoding='utf-8') as f:
                data = f.read()
            return {'data': data, 'source': file_path}
        
        elif data_source == 'api':
            # 调用API获取数据
            import requests
            response = requests.get(step_config['api_url'])
            return {'data': response.text, 'source': step_config['api_url']}
        
        else:
            raise ValueError(f"不支持的数据源: {data_source}")
    
    async def _execute_file_step(self, context: WorkflowContext,
                               step_template: Dict[str, Any],
                               step_config: Dict[str, Any]) -> Dict[str, Any]:
        """执行文件步骤"""
        operation = step_config.get('operation', 'export')
        
        if operation == 'export':
            content = step_config['content']
            file_path = Path(context.artifacts_dir) / step_config['filename']
            
            # 确保目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'file_path': str(file_path),
                'size': len(content),
                'operation': 'export'
            }
        
        else:
            raise ValueError(f"不支持的文件操作: {operation}")
    
    async def _save_step_artifacts(self, context: WorkflowContext,
                                 step_name: str,
                                 step_output: Dict[str, Any]):
        """保存步骤工件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifact_dir = Path(context.artifacts_dir) / step_name
        artifact_dir.mkdir(exist_ok=True)
        
        # 保存输出结果
        output_file = artifact_dir / f"output_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(step_output, f, ensure_ascii=False, indent=2)
        
        # 更新步骤结果中的工件列表
        if step_name in context.step_results:
            context.step_results[step_name].artifacts.append(str(output_file))
    
    async def _handle_failure(self, context: WorkflowContext,
                            step_name: str,
                            step_result: StepResult):
        """处理失败状态"""
        logging.error(f"工作流执行失败: {context.task_id} - {step_name}")
        
        # 发送失败通知
        await context.notify_service.send_notification(
            channel='dingtalk',
            message=f"任务 {context.task_id} 在步骤 {step_name} 处失败: {step_result.error}",
            data={
                'task_id': context.task_id,
                'step_name': step_name,
                'error': step_result.error,
                'status': 'failed'
            }
        )
    
    async def _update_workflow_state(self, context: WorkflowContext):
        """更新工作流状态"""
        workflow_state = {
            'task_id': context.task_id,
            'task_type': context.task_type,
            'mode': context.mode.value,
            'current_step': context.current_step,
            'step_results': {
                name: {
                    'status': result.status.value,
                    'start_time': result.start_time.isoformat() if result.start_time else None,
                    'end_time': result.end_time.isoformat() if result.end_time else None,
                    'error': result.error
                }
                for name, result in context.step_results.items()
            },
            'shared_data': context.shared_data,
            'last_updated': datetime.now().isoformat()
        }
        
        await context.state_manager.save_workflow_state(context.task_id, workflow_state)
    
    async def _finalize_workflow(self, context: WorkflowContext, results: Dict[str, StepResult]):
        """完成工作流"""
        # 更新最终状态
        workflow_state = {
            'task_id': context.task_id,
            'task_type': context.task_type,
            'mode': context.mode.value,
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'step_results': {
                name: {
                    'status': result.status.value,
                    'start_time': result.start_time.isoformat() if result.start_time else None,
                    'end_time': result.end_time.isoformat() if result.end_time else None,
                    'error': result.error
                }
                for name, result in results.items()
            },
            'shared_data': context.shared_data
        }
        
        await context.state_manager.save_workflow_state(context.task_id, workflow_state)
        
        # 发送完成通知
        await context.notify_service.send_notification(
            channel='dingtalk',
            message=f"任务 {context.task_id} 已完成",
            data={
                'task_id': context.task_id,
                'status': 'completed',
                'artifacts': self._collect_artifacts(context)
            }
        )
    
    def _collect_artifacts(self, context: WorkflowContext) -> List[str]:
        """收集所有工件"""
        artifacts = []
        for step_result in context.step_results.values():
            artifacts.extend(step_result.artifacts)
        return artifacts
    
    async def _handle_workflow_error(self, task_id: str, task_type: str, error: Exception):
        """处理工作流错误"""
        logging.error(f"工作流执行错误 {task_id}: {error}")
        
        # 发送错误通知
        await self.notify_service.send_notification(
            channel='dingtalk',
            message=f"任务 {task_id} 执行失败: {str(error)}",
            data={
                'task_id': task_id,
                'task_type': task_type,
                'error': str(error),
                'status': 'error'
            }
        )
    
    def get_workflow_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流状态"""
        # 这里应该从状态管理器获取工作流状态
        # 暂时返回None
        return None
    
    def list_workflow_templates(self) -> List[str]:
        """列出可用的工作流模板"""
        templates = []
        for task_dir in self.workflows_dir.iterdir():
            if task_dir.is_dir() and task_dir.name != 'base':
                for yaml_file in task_dir.glob("*_workflow.yaml"):
                    templates.append(yaml_file.stem)
        return templates
