"""
编码任务执行器 - 实现代码生成和Git操作
"""

import logging
import os
import shutil
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class CodingTaskExecutor(TaskExecutor):
    """编码任务执行器，负责代码生成和Git操作"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行编码任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行编码任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化编码任务")
            
            # 获取任务配置
            coding_config = self.task_config.get('coding', {})
            project_path = coding_config.get('project_path')
            branch_name = coding_config.get('branch_name')
            base_branch = coding_config.get('base_branch', 'main')
            coding_prompt = coding_config.get('prompt')
            
            if not all([project_path, branch_name, coding_prompt]):
                raise ValueError("编码任务配置不完整，缺少project_path、branch_name或prompt")
            
            # 更新进度
            self._update_progress(20, "验证项目路径")
            
            # 验证项目路径并创建目录
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                self.logger.info(f"项目路径不存在，正在创建目录: {project_path}")
                project_path_obj.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"项目目录创建成功: {project_path}")
            
            # 确保项目路径是绝对路径
            project_path = str(project_path_obj.absolute())
            
            # 更新进度
            self._update_progress(30, "创建Git分支")
            
            # 创建Git分支
            if not self.git_service.create_branch(project_path, branch_name, base_branch):
                raise RuntimeError(f"创建Git分支失败: {branch_name}")
            
            # 更新进度
            self._update_progress(40, "分析现有代码")
            
            # 检查是否需要进行增量修改
            incremental_mode = coding_config.get('incremental_mode', False)
            target_file = coding_config.get('target_file')
            
            # 检查是否需要进行复杂重构
            complex_refactor_mode = coding_config.get('complex_refactor_mode', False)
            refactor_request = coding_config.get('refactor_request')
            
            existing_code = None
            code_structure = None
            project_analysis = None
            
            if complex_refactor_mode and refactor_request:
                # 复杂重构模式
                self.logger.info(f"启用复杂重构模式: {self.task_id}")
                
                # 分析项目结构
                project_analysis = self.complex_refactor_service.analyze_project_structure(project_path)
                
                # 生成重构计划
                refactor_plan = self.complex_refactor_service.generate_refactor_plan(
                    refactor_request, project_analysis
                )
                
                self.logger.info(f"重构计划生成完成，共 {len(refactor_plan.get('refactor_steps', []))} 个步骤")
                
                # 添加重构计划到元数据
                self._add_metadata('refactor_plan', refactor_plan)
                self._add_metadata('complex_refactor_mode', True)
                
            elif incremental_mode and target_file:
                # 增量修改模式
                existing_code = self.incremental_code_service.read_existing_code(target_file)
                if existing_code:
                    # 分析代码结构
                    language = coding_config.get('language', 'python')
                    code_structure = self.incremental_code_service.analyze_code_structure(existing_code, language)
                    self.logger.info(f"现有代码分析完成: {target_file}, 语言: {language}")
            
            # 更新进度
            self._update_progress(50, "生成代码")
            
            # 调用AI服务生成代码
            if complex_refactor_mode and refactor_request:
                # 复杂重构模式 - 生成重构报告
                refactor_report = self._generate_complex_refactor_report(refactor_plan, project_analysis)
                generated_code = refactor_report
                
            elif incremental_mode and existing_code:
                # 增量修改模式
                modification_request = coding_prompt
                ai_prompt = self.incremental_code_service.generate_incremental_prompt(
                    existing_code, modification_request, code_structure, 
                    coding_config.get('language', 'python')
                )
                generated_code = self.ai_service.generate_code(
                    prompt=ai_prompt,
                    task_type='coding',
                    project_path=project_path,
                    branch_name=branch_name
                )
            else:
                # 完整生成模式
                generated_code = self.ai_service.generate_code(
                    prompt=coding_prompt,
                    task_type='coding',
                    project_path=project_path,
                    branch_name=branch_name
                )
            
            if not generated_code:
                raise RuntimeError("AI服务生成代码失败")
            
            # 更新进度
            self._update_progress(60, "保存生成的代码")
            
            # 保存生成的代码到文件
            if complex_refactor_mode and refactor_request:
                # 复杂重构模式 - 保存重构报告
                output_file = self._save_refactor_report(refactor_plan, project_analysis, project_path, coding_config)
                self.logger.info(f"重构报告保存成功: {output_file}")
                
            elif incremental_mode and existing_code:
                # 增量修改模式 - 应用修改
                change_result = self.incremental_code_service.apply_incremental_changes(
                    existing_code, generated_code, target_file
                )
                if not change_result['success']:
                    raise RuntimeError(f"应用增量修改失败: {change_result.get('error')}")
                
                output_file = target_file
                self.logger.info(f"增量修改应用成功: {target_file}")
                
                # 添加增量修改的元数据
                self._add_metadata('incremental_mode', True)
                self._add_metadata('backup_path', change_result.get('backup_path'))
                self._add_metadata('changes_made', change_result.get('changes_made'))
                self._add_metadata('diff_report', change_result.get('diff_report'))
            else:
                # 完整生成模式 - 保存新文件
                output_file = self._save_generated_code(generated_code, project_path, coding_config)
            
            # 更新进度
            self._update_progress(80, "提交代码变更")
            
            # 提交代码变更
            commit_message = self._generate_commit_message(coding_prompt, coding_config)
            if not self.git_service.commit_changes(project_path, commit_message):
                raise RuntimeError("提交代码变更失败")
            
            # 更新进度
            self._update_progress(90, "推送代码到远程仓库")
            
            # 推送代码到远程仓库
            if not self.git_service.push_changes(project_path, branch_name):
                raise RuntimeError("推送代码到远程仓库失败")
            
            # 更新进度
            self._update_progress(100, "编码任务完成")
            
            # 准备执行结果
            result = {
                'success': True,
                'branch_name': branch_name,
                'output_file': output_file,
                'commit_message': commit_message,
                'generated_code_length': len(generated_code),
                'project_path': project_path,
                'incremental_mode': incremental_mode,
                'target_file': target_file if incremental_mode else None,
                'complex_refactor_mode': complex_refactor_mode,
                'refactor_request': refactor_request if complex_refactor_mode else None
            }
            
            # 添加元数据
            self._add_metadata('branch_created', branch_name)
            self._add_metadata('code_generated', True)
            self._add_metadata('code_committed', True)
            self._add_metadata('code_pushed', True)
            
            self.logger.info(f"编码任务执行成功: {self.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"编码任务执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _save_generated_code(self, code: str, project_path: str, coding_config: Dict[str, Any]) -> str:
        """
        保存生成的代码到文件
        
        Args:
            code: 生成的代码内容
            project_path: 项目路径
            coding_config: 编码配置
            
        Returns:
            保存的文件路径
        """
        try:
            # 获取输出文件配置
            output_file = coding_config.get('output_file')
            if not output_file:
                # 生成默认文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"generated_code_{timestamp}.py"
            
            # 构建完整路径
            if os.path.isabs(output_file):
                output_path = output_file
            else:
                output_path = os.path.join(project_path, output_file)
            
            # 确保目录存在
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(code)
            
            self.logger.info(f"生成的代码已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存生成的代码失败: {e}")
            raise
    
    def _generate_commit_message(self, prompt: str, coding_config: Dict[str, Any]) -> str:
        """
        生成提交信息
        
        Args:
            prompt: 编码提示
            coding_config: 编码配置
            
        Returns:
            提交信息
        """
        try:
            # 检查是否有自定义提交信息模板
            commit_template = coding_config.get('commit_template')
            if commit_template:
                # 使用模板生成提交信息
                return commit_template.format(
                    prompt=prompt[:100],  # 限制长度
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    task_id=self.task_id
                )
            
            # 使用默认格式
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prompt_summary = prompt[:50] + "..." if len(prompt) > 50 else prompt
            
            return f"feat: AI生成代码 - {prompt_summary}\n\nTask: {self.task_id}\nTime: {timestamp}"
            
        except Exception as e:
            self.logger.warning(f"生成提交信息失败: {e}")
            # 返回简单的提交信息
            return f"feat: AI生成代码 - Task {self.task_id}"
    
    def _validate_coding_config(self, coding_config: Dict[str, Any]) -> List[str]:
        """
        验证编码任务配置
        
        Args:
            coding_config: 编码配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['project_path', 'branch_name', 'prompt']
        for field in required_fields:
            if not coding_config.get(field):
                errors.append(f"编码配置缺少必需字段: {field}")
        
        # 检查项目路径
        project_path = coding_config.get('project_path')
        if project_path and not os.path.exists(project_path):
            errors.append(f"项目路径不存在: {project_path}")
        
        # 检查分支名称格式
        branch_name = coding_config.get('branch_name')
        if branch_name:
            # 简单的分支名称验证
            if not branch_name.replace('-', '').replace('_', '').isalnum():
                errors.append(f"分支名称格式无效: {branch_name}")
        
        return errors
    
    def _backup_existing_files(self, project_path: str, backup_dir: str = None) -> str:
        """
        备份现有文件
        
        Args:
            project_path: 项目路径
            backup_dir: 备份目录，如果为None则自动生成
            
        Returns:
            备份目录路径
        """
        try:
            if not backup_dir:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_dir = os.path.join(project_path, f"backup_{timestamp}")
            
            # 创建备份目录
            os.makedirs(backup_dir, exist_ok=True)
            
            # 复制项目文件到备份目录
            for item in os.listdir(project_path):
                src_path = os.path.join(project_path, item)
                dst_path = os.path.join(backup_dir, item)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
                elif os.path.isdir(src_path) and not item.startswith('.'):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            
            self.logger.info(f"项目文件已备份到: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            self.logger.warning(f"备份项目文件失败: {e}")
            return ""
    
    def _restore_from_backup(self, project_path: str, backup_dir: str):
        """
        从备份恢复文件
        
        Args:
            project_path: 项目路径
            backup_dir: 备份目录
        """
        try:
            if not os.path.exists(backup_dir):
                self.logger.warning(f"备份目录不存在: {backup_dir}")
                return
            
            # 清空项目目录（保留.git目录）
            for item in os.listdir(project_path):
                if item == '.git':
                    continue
                
                item_path = os.path.join(project_path, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            
            # 从备份恢复文件
            for item in os.listdir(backup_dir):
                src_path = os.path.join(backup_dir, item)
                dst_path = os.path.join(project_path, item)
                
                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dst_path)
                elif os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
            
            self.logger.info(f"项目文件已从备份恢复: {backup_dir}")
            
        except Exception as e:
            self.logger.error(f"从备份恢复文件失败: {e}")
            raise
    
    def _generate_complex_refactor_report(self, refactor_plan: Dict[str, Any], 
                                        project_analysis: Dict[str, Any]) -> str:
        """
        生成复杂重构报告
        
        Args:
            refactor_plan: 重构计划
            project_analysis: 项目分析结果
            
        Returns:
            重构报告内容
        """
        try:
            report = f"""
# 复杂重构分析报告

## 项目概览
- 项目路径: {project_analysis.get('project_path', 'N/A')}
- 总文件数: {project_analysis.get('total_files', 0)}
- 平均复杂度: {project_analysis.get('complexity_metrics', {}).get('average_complexity', 0):.2f}

## 重构请求
{refactor_plan.get('refactor_request', 'N/A')}

## 重构分析
- 重构类型: {', '.join(refactor_plan.get('refactor_analysis', {}).get('types', []))}
- 重构范围: {refactor_plan.get('refactor_analysis', {}).get('scope', 'N/A')}
- 受影响文件数: {len(refactor_plan.get('affected_files', []))}

## 重构步骤
"""
            
            for step in refactor_plan.get('refactor_steps', []):
                report += f"""
### {step.get('step_id', 'N/A')} - {step.get('description', 'N/A')}
- 类型: {step.get('type', 'N/A')}
- 预估时间: {step.get('estimated_time', 'N/A')}
- 风险等级: {step.get('risk_level', 'N/A')}
- 具体操作:
"""
                for action in step.get('actions', []):
                    report += f"  - {action}\n"
            
            report += f"""
## 风险评估
- 总体风险等级: {refactor_plan.get('risk_assessment', {}).get('risk_level', 'N/A')}
- 风险评分: {refactor_plan.get('risk_assessment', {}).get('total_risk_score', 0)}

### 风险因素
"""
            
            for factor in refactor_plan.get('risk_assessment', {}).get('risk_factors', []):
                report += f"- {factor.get('description', 'N/A')} (风险等级: {factor.get('risk_level', 'N/A')})\n"
            
            report += f"""
## 工作量估算
- 总工时: {refactor_plan.get('estimated_effort', {}).get('total_hours', 0)} 小时
- 预估天数: {refactor_plan.get('estimated_effort', {}).get('estimated_days', 0):.1f} 天

## 测试策略
- 单元测试覆盖率目标: {refactor_plan.get('test_strategy', {}).get('unit_tests', {}).get('coverage_target', 0)}%
- 重点关注: {', '.join(refactor_plan.get('test_strategy', {}).get('unit_tests', {}).get('focus_areas', []))}

## 执行建议
1. 按照重构步骤顺序执行
2. 每步完成后进行充分测试
3. 准备回滚方案
4. 监控执行过程
5. 及时调整计划

## 项目热点分析
"""
            
            for hotspot in project_analysis.get('refactor_hotspots', [])[:10]:  # 只显示前10个
                report += f"- {hotspot.get('file', 'N/A')}: {hotspot.get('type', 'N/A')} (优先级: {hotspot.get('priority', 'N/A')})\n"
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成复杂重构报告失败: {e}")
            return f"重构报告生成失败: {e}"
    
    def _save_refactor_report(self, refactor_plan: Dict[str, Any], 
                            project_analysis: Dict[str, Any],
                            project_path: str, 
                            coding_config: Dict[str, Any]) -> str:
        """
        保存重构报告
        
        Args:
            refactor_plan: 重构计划
            project_analysis: 项目分析结果
            project_path: 项目路径
            coding_config: 编码配置
            
        Returns:
            保存的文件路径
        """
        try:
            # 生成报告内容
            report_content = self._generate_complex_refactor_report(refactor_plan, project_analysis)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"refactor_report_{timestamp}.md"
            
            # 构建完整路径
            if os.path.isabs(report_file):
                output_path = report_file
            else:
                output_path = os.path.join(project_path, report_file)
            
            # 确保目录存在
            output_dir = os.path.dirname(output_path)
            os.makedirs(output_dir, exist_ok=True)
            
            # 写入文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            self.logger.info(f"重构报告已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.error(f"保存重构报告失败: {e}")
            raise
