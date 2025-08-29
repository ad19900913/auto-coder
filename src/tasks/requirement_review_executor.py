"""
需求审查任务执行器 - 实现需求文档与代码实现的一致性分析
"""

import logging
import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class RequirementReviewTaskExecutor(TaskExecutor):
    """需求审查任务执行器，负责需求文档与代码实现的一致性分析"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行需求审查任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行需求审查任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化需求审查任务")
            
            # 获取任务配置
            review_config = self.task_config.get('requirement_review', {})
            requirement_file = review_config.get('requirement_file')
            project_path = review_config.get('project_path')
            branch_name = review_config.get('branch_name', 'main')
            code_package_paths = review_config.get('code_package_paths', [])
            prompt_template = review_config.get('prompt_template')
            
            if not all([requirement_file, project_path]):
                raise ValueError("需求审查任务配置不完整，缺少requirement_file或project_path")
            
            # 更新进度
            self._update_progress(20, "读取需求文档")
            
            # 读取需求文档
            requirement_content = self._read_requirement_file(requirement_file)
            if not requirement_content:
                raise RuntimeError(f"无法读取需求文档: {requirement_file}")
            
            # 更新进度
            self._update_progress(30, "分析代码实现")
            
            # 分析代码实现
            code_analysis = self._analyze_code_implementation(project_path, branch_name, code_package_paths)
            
            # 更新进度
            self._update_progress(50, "AI分析需求与代码一致性")
            
            # 调用AI服务分析需求与代码的一致性
            consistency_analysis = self.ai_service.analyze_requirement_code(
                requirement=requirement_content,
                code=code_analysis,
                prompt_template=prompt_template,
                project_path=project_path,
                branch_name=branch_name
            )
            
            if not consistency_analysis:
                raise RuntimeError("AI服务分析需求与代码一致性失败")
            
            # 更新进度
            self._update_progress(70, "生成审查报告")
            
            # 生成审查报告
            review_report = self._generate_requirement_review_report(
                requirement_content, code_analysis, consistency_analysis, review_config
            )
            
            # 更新进度
            self._update_progress(90, "保存审查报告")
            
            # 保存审查报告
            output_file = self._save_output(
                review_report, 
                'requirement_reviews', 
                f"{self.task_id}_requirement_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            
            # 更新进度
            self._update_progress(100, "需求审查任务完成")
            
            # 准备执行结果
            result = {
                'success': True,
                'requirement_file': requirement_file,
                'project_path': project_path,
                'branch_name': branch_name,
                'output_file': output_file,
                'requirement_length': len(requirement_content),
                'code_files_analyzed': code_analysis.get('file_count', 0),
                'consistency_score': consistency_analysis.get('consistency_score', 0)
            }
            
            # 添加元数据
            self._add_metadata('requirement_reviewed', True)
            self._add_metadata('consistency_score', consistency_analysis.get('consistency_score', 0))
            self._add_metadata('code_files_analyzed', code_analysis.get('file_count', 0))
            
            self.logger.info(f"需求审查任务执行成功: {self.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"需求审查任务执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _read_requirement_file(self, requirement_file: str) -> str:
        """
        读取需求文档
        
        Args:
            requirement_file: 需求文档路径
            
        Returns:
            需求文档内容
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(requirement_file):
                raise FileNotFoundError(f"需求文档不存在: {requirement_file}")
            
            # 根据文件扩展名选择读取方式
            file_ext = os.path.splitext(requirement_file)[1].lower()
            
            if file_ext in ['.md', '.txt']:
                # 读取文本文件
                with open(requirement_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif file_ext in ['.docx', '.doc']:
                # 读取Word文档
                content = self._read_word_document(requirement_file)
            else:
                raise ValueError(f"不支持的需求文档格式: {file_ext}")
            
            self.logger.info(f"需求文档读取成功: {requirement_file}, 长度: {len(content)} 字符")
            return content
            
        except Exception as e:
            self.logger.error(f"读取需求文档失败: {e}")
            raise
    
    def _read_word_document(self, file_path: str) -> str:
        """
        读取Word文档
        
        Args:
            file_path: Word文档路径
            
        Returns:
            文档内容
        """
        try:
            # 这里可以集成python-docx库来读取Word文档
            # 暂时返回简单的提示信息
            self.logger.warning(f"Word文档读取功能暂未实现: {file_path}")
            return f"Word文档内容: {os.path.basename(file_path)}\n\n请手动提供文档内容。"
            
        except Exception as e:
            self.logger.error(f"读取Word文档失败: {e}")
            return f"文档读取失败: {e}"
    
    def _analyze_code_implementation(self, project_path: str, branch_name: str, 
                                   code_package_paths: List[str]) -> Dict[str, Any]:
        """
        分析代码实现
        
        Args:
            project_path: 项目路径
            branch_name: 分支名称
            code_package_paths: 代码包路径列表
            
        Returns:
            代码分析结果
        """
        try:
            code_analysis = {
                'project_path': project_path,
                'branch_name': branch_name,
                'file_count': 0,
                'files': [],
                'structure': {},
                'interfaces': [],
                'data_models': [],
                'dependencies': []
            }
            
            # 如果没有指定代码包路径，分析整个项目
            if not code_package_paths:
                code_package_paths = [project_path]
            
            for package_path in code_package_paths:
                full_path = os.path.join(project_path, package_path) if not os.path.isabs(package_path) else package_path
                
                if not os.path.exists(full_path):
                    self.logger.warning(f"代码包路径不存在: {full_path}")
                    continue
                
                # 分析代码包
                package_analysis = self._analyze_code_package(full_path)
                
                # 合并分析结果
                code_analysis['file_count'] += package_analysis.get('file_count', 0)
                code_analysis['files'].extend(package_analysis.get('files', []))
                code_analysis['interfaces'].extend(package_analysis.get('interfaces', []))
                code_analysis['data_models'].extend(package_analysis.get('data_models', []))
                code_analysis['dependencies'].extend(package_analysis.get('dependencies', []))
                
                # 更新结构信息
                package_name = os.path.basename(package_path)
                code_analysis['structure'][package_name] = package_analysis.get('structure', {})
            
            self.logger.info(f"代码分析完成，共分析 {code_analysis['file_count']} 个文件")
            return code_analysis
            
        except Exception as e:
            self.logger.error(f"分析代码实现失败: {e}")
            return {
                'project_path': project_path,
                'branch_name': branch_name,
                'file_count': 0,
                'files': [],
                'structure': {},
                'interfaces': [],
                'data_models': [],
                'dependencies': [],
                'error': str(e)
            }
    
    def _analyze_code_package(self, package_path: str) -> Dict[str, Any]:
        """
        分析单个代码包
        
        Args:
            package_path: 代码包路径
            
        Returns:
            包分析结果
        """
        try:
            analysis = {
                'file_count': 0,
                'files': [],
                'structure': {},
                'interfaces': [],
                'data_models': [],
                'dependencies': []
            }
            
            # 遍历代码文件
            for root, dirs, files in os.walk(package_path):
                # 跳过隐藏目录和特定目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'target']]
                
                for file in files:
                    if file.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.h')):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, package_path)
                        
                        # 分析文件
                        file_analysis = self._analyze_code_file(file_path, relative_path)
                        
                        if file_analysis:
                            analysis['files'].append(file_analysis)
                            analysis['file_count'] += 1
                            
                            # 提取接口信息
                            if file_analysis.get('interfaces'):
                                analysis['interfaces'].extend(file_analysis['interfaces'])
                            
                            # 提取数据模型信息
                            if file_analysis.get('data_models'):
                                analysis['data_models'].extend(file_analysis['data_models'])
                            
                            # 提取依赖信息
                            if file_analysis.get('dependencies'):
                                analysis['dependencies'].extend(file_analysis['dependencies'])
            
            # 构建结构信息
            analysis['structure'] = self._build_package_structure(package_path)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析代码包失败 {package_path}: {e}")
            return {
                'file_count': 0,
                'files': [],
                'structure': {},
                'interfaces': [],
                'data_models': [],
                'dependencies': [],
                'error': str(e)
            }
    
    def _analyze_code_file(self, file_path: str, relative_path: str) -> Optional[Dict[str, Any]]:
        """
        分析单个代码文件
        
        Args:
            file_path: 文件路径
            relative_path: 相对路径
            
        Returns:
            文件分析结果
        """
        try:
            file_analysis = {
                'path': relative_path,
                'size': os.path.getsize(file_path),
                'interfaces': [],
                'data_models': [],
                'dependencies': [],
                'classes': [],
                'functions': []
            }
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 根据文件类型进行不同的分析
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.py':
                self._analyze_python_file(content, file_analysis)
            elif file_ext == '.java':
                self._analyze_java_file(content, file_analysis)
            elif file_ext in ['.js', '.ts']:
                self._analyze_javascript_file(content, file_analysis)
            elif file_ext in ['.cpp', '.c', '.h']:
                self._analyze_cpp_file(content, file_analysis)
            
            return file_analysis
            
        except Exception as e:
            self.logger.warning(f"分析代码文件失败 {file_path}: {e}")
            return None
    
    def _analyze_python_file(self, content: str, file_analysis: Dict[str, Any]):
        """分析Python文件"""
        try:
            # 提取类定义
            class_pattern = r'class\s+(\w+)(?:\(.*?\))?:'
            classes = re.findall(class_pattern, content)
            file_analysis['classes'] = classes
            
            # 提取函数定义
            function_pattern = r'def\s+(\w+)\s*\('
            functions = re.findall(function_pattern, content)
            file_analysis['functions'] = functions
            
            # 提取接口信息（类方法）
            for class_name in classes:
                # 简单的接口提取逻辑
                if 'def' in content and class_name in content:
                    file_analysis['interfaces'].append(f"{class_name}.method")
            
            # 提取导入依赖
            import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
            imports = re.findall(import_pattern, content)
            file_analysis['dependencies'] = [imp[0] or imp[1] for imp in imports if any(imp)]
            
        except Exception as e:
            self.logger.warning(f"分析Python文件失败: {e}")
    
    def _analyze_java_file(self, content: str, file_analysis: Dict[str, Any]):
        """分析Java文件"""
        try:
            # 提取类定义
            class_pattern = r'(?:public\s+)?class\s+(\w+)'
            classes = re.findall(class_pattern, content)
            file_analysis['classes'] = classes
            
            # 提取方法定义
            method_pattern = r'(?:public|private|protected)?\s*(?:static\s+)?\w+\s+(\w+)\s*\('
            methods = re.findall(method_pattern, content)
            file_analysis['functions'] = methods
            
            # 提取接口信息
            for class_name in classes:
                if 'public' in content and class_name in content:
                    file_analysis['interfaces'].append(f"{class_name}.method")
            
            # 提取导入依赖
            import_pattern = r'import\s+([\w.]+)'
            imports = re.findall(import_pattern, content)
            file_analysis['dependencies'] = imports
            
        except Exception as e:
            self.logger.warning(f"分析Java文件失败: {e}")
    
    def _analyze_javascript_file(self, content: str, file_analysis: Dict[str, Any]):
        """分析JavaScript/TypeScript文件"""
        try:
            # 提取类定义
            class_pattern = r'class\s+(\w+)'
            classes = re.findall(class_pattern, content)
            file_analysis['classes'] = classes
            
            # 提取函数定义
            function_pattern = r'(?:function\s+)?(\w+)\s*[=\(]'
            functions = re.findall(function_pattern, content)
            file_analysis['functions'] = functions
            
            # 提取接口信息
            for class_name in classes:
                if 'export' in content and class_name in content:
                    file_analysis['interfaces'].append(f"{class_name}.method")
            
            # 提取导入依赖
            import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
            imports = re.findall(import_pattern, content)
            file_analysis['dependencies'] = imports
            
        except Exception as e:
            self.logger.warning(f"分析JavaScript文件失败: {e}")
    
    def _analyze_cpp_file(self, content: str, file_analysis: Dict[str, Any]):
        """分析C++文件"""
        try:
            # 提取类定义
            class_pattern = r'class\s+(\w+)'
            classes = re.findall(class_pattern, content)
            file_analysis['classes'] = classes
            
            # 提取函数定义
            function_pattern = r'(?:void|int|string|bool|double|float)\s+(\w+)\s*\('
            functions = re.findall(function_pattern, content)
            file_analysis['functions'] = functions
            
            # 提取接口信息
            for class_name in classes:
                if 'public:' in content and class_name in content:
                    file_analysis['interfaces'].append(f"{class_name}.method")
            
            # 提取包含依赖
            include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
            includes = re.findall(include_pattern, content)
            file_analysis['dependencies'] = includes
            
        except Exception as e:
            self.logger.warning(f"分析C++文件失败: {e}")
    
    def _build_package_structure(self, package_path: str) -> Dict[str, Any]:
        """
        构建包结构信息
        
        Args:
            package_path: 包路径
            
        Returns:
            包结构信息
        """
        try:
            structure = {}
            
            for root, dirs, files in os.walk(package_path):
                # 跳过隐藏目录
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # 计算相对路径
                rel_path = os.path.relpath(root, package_path)
                if rel_path == '.':
                    rel_path = ''
                
                # 统计文件数量
                code_files = [f for f in files if f.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.h'))]
                
                if rel_path not in structure:
                    structure[rel_path] = {
                        'files': code_files,
                        'file_count': len(code_files),
                        'subdirs': []
                    }
                
                # 添加子目录
                for dir_name in dirs:
                    if dir_name not in structure[rel_path]['subdirs']:
                        structure[rel_path]['subdirs'].append(dir_name)
            
            return structure
            
        except Exception as e:
            self.logger.warning(f"构建包结构失败: {e}")
            return {}
    
    def _generate_requirement_review_report(self, requirement_content: str, code_analysis: Dict[str, Any],
                                          consistency_analysis: Dict[str, Any], review_config: Dict[str, Any]) -> str:
        """
        生成需求审查报告
        
        Args:
            requirement_content: 需求文档内容
            code_analysis: 代码分析结果
            consistency_analysis: 一致性分析结果
            review_config: 审查配置
            
        Returns:
            审查报告内容
        """
        try:
            # 生成报告
            report = f"""# 需求与代码实现一致性审查报告

## 基本信息
- **任务ID**: {self.task_id}
- **审查时间**: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
- **项目路径**: {review_config.get('project_path', 'N/A')}
- **分支名称**: {review_config.get('branch_name', 'main')}

## 需求文档分析

### 需求文档信息
- **文档路径**: {review_config.get('requirement_file', 'N/A')}
- **文档长度**: {len(requirement_content)} 字符
- **文档类型**: {os.path.splitext(review_config.get('requirement_file', ''))[1] or '未知'}

### 需求摘要
```
{requirement_content[:500]}{'...' if len(requirement_content) > 500 else ''}
```

## 代码实现分析

### 项目概览
- **项目路径**: {code_analysis.get('project_path', 'N/A')}
- **分支名称**: {code_analysis.get('branch_name', 'N/A')}
- **分析文件数**: {code_analysis.get('file_count', 0)}

### 代码结构
"""
            
            # 添加代码结构信息
            structure = code_analysis.get('structure', {})
            for package_name, package_info in structure.items():
                if package_name:
                    report += f"- **{package_name}**: {package_info.get('file_count', 0)} 个文件"
                    if package_info.get('subdirs'):
                        report += f", 子目录: {', '.join(package_info['subdirs'])}"
                    report += "\n"
                else:
                    report += f"- **根目录**: {package_info.get('file_count', 0)} 个文件\n"
            
            # 添加接口和数据模型信息
            interfaces = code_analysis.get('interfaces', [])
            data_models = code_analysis.get('data_models', [])
            dependencies = code_analysis.get('dependencies', [])
            
            report += f"""
### 代码组件统计
- **接口数量**: {len(interfaces)}
- **数据模型数量**: {len(data_models)}
- **依赖数量**: {len(dependencies)}

### 主要接口
"""
            
            if interfaces:
                for i, interface in enumerate(interfaces[:10], 1):  # 显示前10个
                    report += f"{i}. {interface}\n"
                if len(interfaces) > 10:
                    report += f"... 还有 {len(interfaces) - 10} 个接口\n"
            else:
                report += "未发现明显的接口定义\n"
            
            report += f"""
### 主要依赖
"""
            
            if dependencies:
                for i, dependency in enumerate(dependencies[:10], 1):  # 显示前10个
                    report += f"{i}. {dependency}\n"
                if len(dependencies) > 10:
                    report += f"... 还有 {len(dependencies) - 10} 个依赖\n"
            else:
                report += "未发现明显的依赖关系\n"
            
            # 添加一致性分析结果
            report += f"""

## AI一致性分析结果

### 分析摘要
{consistency_analysis.get('summary', 'AI分析结果为空')}

### 一致性评分
**总体一致性**: {consistency_analysis.get('consistency_score', 0):.1f}/100

### 发现的问题
"""
            
            issues = consistency_analysis.get('issues', [])
            if issues:
                for i, issue in enumerate(issues, 1):
                    report += f"{i}. {issue}\n"
            else:
                report += "未发现明显的一致性问题\n"
            
            # 添加建议
            recommendations = consistency_analysis.get('recommendations', [])
            if recommendations:
                report += f"""
### 改进建议
"""
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
            
            # 添加结论
            consistency_score = consistency_analysis.get('consistency_score', 0)
            report += f"""

## 审查结论

基于以上分析，需求与代码实现的一致性评分为 **{consistency_score:.1f}/100**。

"""
            
            # 根据评分添加结论
            if consistency_score >= 90:
                report += "**结论**: 需求与代码实现高度一致，可以继续开发。"
            elif consistency_score >= 80:
                report += "**结论**: 需求与代码实现基本一致，建议关注发现的问题。"
            elif consistency_score >= 70:
                report += "**结论**: 需求与代码实现部分一致，需要解决主要问题。"
            else:
                report += "**结论**: 需求与代码实现存在较大差异，建议重新梳理需求或调整代码。"
            
            report += f"""

---

*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*任务ID: {self.task_id}*
"""
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成需求审查报告失败: {e}")
            return f"# 需求审查报告生成失败\n\n错误信息: {e}\n\n任务ID: {self.task_id}"
    
    def _validate_requirement_review_config(self, review_config: Dict[str, Any]) -> List[str]:
        """
        验证需求审查任务配置
        
        Args:
            review_config: 审查配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['requirement_file', 'project_path']
        for field in required_fields:
            if not review_config.get(field):
                errors.append(f"需求审查配置缺少必需字段: {field}")
        
        # 检查需求文档文件
        requirement_file = review_config.get('requirement_file')
        if requirement_file and not os.path.exists(requirement_file):
            errors.append(f"需求文档文件不存在: {requirement_file}")
        
        # 检查项目路径
        project_path = review_config.get('project_path')
        if project_path and not os.path.exists(project_path):
            errors.append(f"项目路径不存在: {project_path}")
        
        return errors
