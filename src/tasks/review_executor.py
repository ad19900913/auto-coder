"""
代码审查任务执行器 - 实现代码质量分析和审查报告生成
"""

import logging
import os
import difflib
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..core.task_executor import TaskExecutor


class ReviewTaskExecutor(TaskExecutor):
    """代码审查任务执行器，负责代码质量分析和审查报告生成"""
    
    def _execute_task(self) -> Dict[str, Any]:
        """
        执行代码审查任务
        
        Returns:
            执行结果字典
        """
        try:
            self.logger.info(f"开始执行代码审查任务: {self.task_id}")
            
            # 更新进度
            self._update_progress(10, "初始化代码审查任务")
            
            # 获取任务配置
            review_config = self.task_config.get('review', {})
            project_path = review_config.get('project_path')
            target_branch = review_config.get('target_branch')
            base_branch = review_config.get('base_branch', 'main')
            review_time = review_config.get('review_time')
            code_package_paths = review_config.get('code_package_paths', [])
            
            if not all([project_path, target_branch]):
                raise ValueError("代码审查任务配置不完整，缺少project_path或target_branch")
            
            # 更新进度
            self._update_progress(20, "验证项目路径和分支")
            
            # 验证项目路径
            if not os.path.exists(project_path):
                raise FileNotFoundError(f"项目路径不存在: {project_path}")
            
            # 更新进度
            self._update_progress(30, "获取代码差异")
            
            # 获取代码差异
            diff_content = self.git_service.get_diff(project_path, base_branch, target_branch)
            if not diff_content:
                self.logger.warning(f"未发现代码差异: {base_branch} -> {target_branch}")
                diff_content = "无代码变更"
            
            # 更新进度
            self._update_progress(40, "分析代码质量")
            
            # 分析代码质量
            quality_analysis = self._analyze_code_quality(project_path, target_branch, code_package_paths)
            
            # 更新进度
            self._update_progress(60, "生成审查报告")
            
            # 生成审查报告
            review_report = self._generate_review_report(
                diff_content, quality_analysis, review_config
            )
            
            # 更新进度
            self._update_progress(80, "保存审查报告")
            
            # 保存审查报告
            output_file = self._save_output(
                review_report, 
                'reviews', 
                f"{self.task_id}_code_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            
            # 更新进度
            self._update_progress(100, "代码审查任务完成")
            
            # 准备执行结果
            result = {
                'success': True,
                'target_branch': target_branch,
                'base_branch': base_branch,
                'output_file': output_file,
                'diff_content_length': len(diff_content),
                'quality_score': quality_analysis.get('overall_score', 0),
                'issues_found': len(quality_analysis.get('issues', [])),
                'project_path': project_path
            }
            
            # 添加元数据
            self._add_metadata('review_completed', True)
            self._add_metadata('quality_score', quality_analysis.get('overall_score', 0))
            self._add_metadata('issues_count', len(quality_analysis.get('issues', [])))
            self._add_metadata('review_time', review_time)
            
            self.logger.info(f"代码审查任务执行成功: {self.task_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"代码审查任务执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _analyze_code_quality(self, project_path: str, target_branch: str, 
                             code_package_paths: List[str]) -> Dict[str, Any]:
        """
        分析代码质量
        
        Args:
            project_path: 项目路径
            target_branch: 目标分支
            code_package_paths: 代码包路径列表
            
        Returns:
            代码质量分析结果
        """
        try:
            quality_analysis = {
                'overall_score': 0,
                'issues': [],
                'metrics': {},
                'recommendations': []
            }
            
            # 如果没有指定代码包路径，分析整个项目
            if not code_package_paths:
                code_package_paths = [project_path]
            
            total_files = 0
            total_issues = 0
            total_score = 0
            
            for package_path in code_package_paths:
                full_path = os.path.join(project_path, package_path) if not os.path.isabs(package_path) else package_path
                
                if not os.path.exists(full_path):
                    self.logger.warning(f"代码包路径不存在: {full_path}")
                    continue
                
                # 分析代码包
                package_analysis = self._analyze_package(full_path)
                
                # 合并分析结果
                total_files += package_analysis.get('file_count', 0)
                total_issues += len(package_analysis.get('issues', []))
                total_score += package_analysis.get('score', 0)
                
                quality_analysis['issues'].extend(package_analysis.get('issues', []))
                quality_analysis['metrics'].update(package_analysis.get('metrics', {}))
                quality_analysis['recommendations'].extend(package_analysis.get('recommendations', []))
            
            # 计算总体评分
            if total_files > 0:
                quality_analysis['overall_score'] = total_score / len(code_package_paths)
            
            # 添加总体统计
            quality_analysis['summary'] = {
                'total_files': total_files,
                'total_issues': total_issues,
                'average_score': quality_analysis['overall_score']
            }
            
            return quality_analysis
            
        except Exception as e:
            self.logger.error(f"分析代码质量失败: {e}")
            return {
                'overall_score': 0,
                'issues': [f"代码质量分析失败: {e}"],
                'metrics': {},
                'recommendations': ['请检查项目路径和代码包配置'],
                'summary': {'total_files': 0, 'total_issues': 1, 'average_score': 0}
            }
    
    def _analyze_package(self, package_path: str) -> Dict[str, Any]:
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
                'score': 0,
                'issues': [],
                'metrics': {},
                'recommendations': []
            }
            
            # 统计文件数量
            file_count = 0
            for root, dirs, files in os.walk(package_path):
                # 跳过隐藏目录和特定目录
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'target']]
                
                for file in files:
                    if file.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.h')):
                        file_count += 1
            
            analysis['file_count'] = file_count
            
            # 简单的代码质量检查（这里可以根据需要扩展）
            if file_count > 0:
                # 检查文件大小
                large_files = self._check_file_sizes(package_path)
                if large_files:
                    analysis['issues'].extend(large_files)
                
                # 检查命名规范
                naming_issues = self._check_naming_conventions(package_path)
                if naming_issues:
                    analysis['issues'].extend(naming_issues)
                
                # 计算质量评分（简化版本）
                issue_count = len(analysis['issues'])
                analysis['score'] = max(0, 100 - issue_count * 10)
                
                # 生成建议
                if issue_count > 0:
                    analysis['recommendations'].append("建议修复代码质量问题")
                if analysis['score'] < 70:
                    analysis['recommendations'].append("代码质量需要改进")
                else:
                    analysis['recommendations'].append("代码质量良好")
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析代码包失败 {package_path}: {e}")
            return {
                'file_count': 0,
                'score': 0,
                'issues': [f"分析失败: {e}"],
                'metrics': {},
                'recommendations': ['请检查代码包路径']
            }
    
    def _check_file_sizes(self, package_path: str) -> List[str]:
        """
        检查文件大小
        
        Args:
            package_path: 代码包路径
            
        Returns:
            文件大小问题列表
        """
        issues = []
        max_file_size = 1024 * 1024  # 1MB
        
        try:
            for root, dirs, files in os.walk(package_path):
                for file in files:
                    if file.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.h')):
                        file_path = os.path.join(root, file)
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size > max_file_size:
                                relative_path = os.path.relpath(file_path, package_path)
                                issues.append(f"文件过大: {relative_path} ({file_size / 1024:.1f}KB)")
                        except OSError:
                            continue
            
            return issues
            
        except Exception as e:
            self.logger.warning(f"检查文件大小失败: {e}")
            return []
    
    def _check_naming_conventions(self, package_path: str) -> List[str]:
        """
        检查命名规范
        
        Args:
            package_path: 代码包路径
            
        Returns:
            命名规范问题列表
        """
        issues = []
        
        try:
            for root, dirs, files in os.walk(package_path):
                # 检查目录命名
                for dir_name in dirs:
                    if not dir_name.replace('_', '').replace('-', '').isalnum():
                        relative_path = os.path.relpath(os.path.join(root, dir_name), package_path)
                        issues.append(f"目录命名不规范: {relative_path}")
                
                # 检查文件命名
                for file_name in files:
                    if file_name.endswith(('.py', '.java', '.js', '.ts', '.cpp', '.c', '.h')):
                        # 检查文件名是否包含特殊字符
                        if not file_name.replace('_', '').replace('-', '').replace('.', '').isalnum():
                            relative_path = os.path.relpath(os.path.join(root, file_name), package_path)
                            issues.append(f"文件名不规范: {relative_path}")
            
            return issues
            
        except Exception as e:
            self.logger.warning(f"检查命名规范失败: {e}")
            return []
    
    def _generate_review_report(self, diff_content: str, quality_analysis: Dict[str, Any], 
                               review_config: Dict[str, Any]) -> str:
        """
        生成代码审查报告
        
        Args:
            diff_content: 代码差异内容
            quality_analysis: 代码质量分析结果
            review_config: 审查配置
            
        Returns:
            审查报告内容
        """
        try:
            # 获取审查时间
            review_time = review_config.get('review_time')
            if review_time:
                try:
                    review_datetime = datetime.fromisoformat(review_time)
                    review_time_str = review_datetime.strftime("%Y年%m月%d日 %H:%M:%S")
                except:
                    review_time_str = review_time
            else:
                review_time_str = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            
            # 生成报告
            report = f"""# 代码审查报告

## 基本信息
- **任务ID**: {self.task_id}
- **审查时间**: {review_time_str}
- **项目路径**: {review_config.get('project_path', 'N/A')}
- **目标分支**: {review_config.get('target_branch', 'N/A')}
- **基准分支**: {review_config.get('base_branch', 'main')}

## 代码质量分析

### 总体评分
**质量评分**: {quality_analysis.get('overall_score', 0):.1f}/100

### 统计信息
- **分析文件数**: {quality_analysis.get('summary', {}).get('total_files', 0)}
- **发现问题数**: {quality_analysis.get('summary', {}).get('total_issues', 0)}

### 发现的问题
"""
            
            # 添加问题列表
            issues = quality_analysis.get('issues', [])
            if issues:
                for i, issue in enumerate(issues, 1):
                    report += f"{i}. {issue}\n"
            else:
                report += "未发现明显问题。\n"
            
            # 添加建议
            recommendations = quality_analysis.get('recommendations', [])
            if recommendations:
                report += "\n### 改进建议\n"
                for i, rec in enumerate(recommendations, 1):
                    report += f"{i}. {rec}\n"
            
            # 添加代码差异
            report += f"""

## 代码变更详情

### 差异统计
- **差异内容长度**: {len(diff_content)} 字符

### 详细差异
```
{diff_content}
```

## 审查结论

基于以上分析，代码质量评分为 **{quality_analysis.get('overall_score', 0):.1f}/100**。

"""
            
            # 根据评分添加结论
            score = quality_analysis.get('overall_score', 0)
            if score >= 90:
                report += "**结论**: 代码质量优秀，可以合并。"
            elif score >= 80:
                report += "**结论**: 代码质量良好，建议修复少量问题后合并。"
            elif score >= 70:
                report += "**结论**: 代码质量一般，需要修复一些问题后再考虑合并。"
            else:
                report += "**结论**: 代码质量较差，建议重新审查或重构。"
            
            report += f"""

---
*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*任务ID: {self.task_id}*
"""
            
            return report
            
        except Exception as e:
            self.logger.error(f"生成审查报告失败: {e}")
            return f"# 代码审查报告生成失败\n\n错误信息: {e}\n\n任务ID: {self.task_id}"
    
    def _validate_review_config(self, review_config: Dict[str, Any]) -> List[str]:
        """
        验证代码审查任务配置
        
        Args:
            review_config: 审查配置
            
        Returns:
            验证错误列表
        """
        errors = []
        
        # 检查必需字段
        required_fields = ['project_path', 'target_branch']
        for field in required_fields:
            if not review_config.get(field):
                errors.append(f"代码审查配置缺少必需字段: {field}")
        
        # 检查项目路径
        project_path = review_config.get('project_path')
        if project_path and not os.path.exists(project_path):
            errors.append(f"项目路径不存在: {project_path}")
        
        # 检查分支名称
        target_branch = review_config.get('target_branch')
        if target_branch and not target_branch.replace('-', '').replace('_', '').isalnum():
            errors.append(f"目标分支名称格式无效: {target_branch}")
        
        return errors
