"""
代码重构工具模块
提供代码重构相关的工具函数
"""

import ast
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class RefactorUtils:
    """代码重构工具类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_function_complexity(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        分析函数复杂度
        
        Args:
            file_path: 文件路径
            
        Returns:
            复杂度分析结果
        """
        complexity_issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    lines = self._count_function_lines(node)
                    parameters = len(node.args.args)
                    
                    issue = {
                        'function_name': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'lines': lines,
                        'parameters': parameters,
                        'file': str(file_path)
                    }
                    
                    # 检查复杂度问题
                    if complexity > 10:
                        issue['issue_type'] = 'high_complexity'
                        issue['message'] = f"函数 {node.name} 的圈复杂度为 {complexity}，建议重构"
                        complexity_issues.append(issue)
                    
                    if lines > 50:
                        issue['issue_type'] = 'long_function'
                        issue['message'] = f"函数 {node.name} 有 {lines} 行，建议拆分"
                        complexity_issues.append(issue)
                    
                    if parameters > 5:
                        issue['issue_type'] = 'too_many_parameters'
                        issue['message'] = f"函数 {node.name} 有 {parameters} 个参数，建议使用对象或配置类"
                        complexity_issues.append(issue)
        
        except Exception as e:
            self.logger.error(f"分析文件复杂度失败 {file_path}: {e}")
        
        return complexity_issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """
        计算圈复杂度
        
        Args:
            node: 函数节点
            
        Returns:
            圈复杂度
        """
        complexity = 1  # 基础复杂度
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
        
        return complexity
    
    def _count_function_lines(self, node: ast.FunctionDef) -> int:
        """
        计算函数行数
        
        Args:
            node: 函数节点
            
        Returns:
            函数行数
        """
        if not node.body:
            return 0
        
        start_line = node.lineno
        end_line = node.end_lineno or start_line
        
        return end_line - start_line + 1
    
    def find_duplicate_code(self, file_path: Path, min_lines: int = 5) -> List[Dict[str, Any]]:
        """
        查找重复代码
        
        Args:
            file_path: 文件路径
            min_lines: 最小重复行数
            
        Returns:
            重复代码列表
        """
        duplicates = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 查找重复的代码块
            for i in range(len(lines) - min_lines + 1):
                for j in range(i + min_lines, len(lines) - min_lines + 1):
                    if self._compare_code_blocks(lines, i, j, min_lines):
                        duplicate = {
                            'file': str(file_path),
                            'block1_start': i + 1,
                            'block1_end': i + min_lines,
                            'block2_start': j + 1,
                            'block2_end': j + min_lines,
                            'lines': min_lines,
                            'content': ''.join(lines[i:i + min_lines]).strip()
                        }
                        duplicates.append(duplicate)
        
        except Exception as e:
            self.logger.error(f"查找重复代码失败 {file_path}: {e}")
        
        return duplicates
    
    def _compare_code_blocks(self, lines: List[str], start1: int, start2: int, length: int) -> bool:
        """
        比较两个代码块是否相同
        
        Args:
            lines: 代码行列表
            start1: 第一个块的起始位置
            start2: 第二个块的起始位置
            length: 块长度
            
        Returns:
            是否相同
        """
        for i in range(length):
            if lines[start1 + i].strip() != lines[start2 + i].strip():
                return False
        return True
    
    def suggest_refactoring(self, complexity_issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        建议重构方案
        
        Args:
            complexity_issues: 复杂度问题列表
            
        Returns:
            重构建议列表
        """
        suggestions = []
        
        for issue in complexity_issues:
            suggestion = {
                'file': issue['file'],
                'function_name': issue['function_name'],
                'line': issue['line'],
                'issue_type': issue['issue_type'],
                'suggestions': []
            }
            
            if issue['issue_type'] == 'high_complexity':
                suggestion['suggestions'].extend([
                    "提取条件判断为独立方法",
                    "使用策略模式替换复杂的条件分支",
                    "将复杂逻辑拆分为多个小方法",
                    "考虑使用状态模式"
                ])
            
            elif issue['issue_type'] == 'long_function':
                suggestion['suggestions'].extend([
                    "将函数拆分为多个小函数",
                    "提取重复代码为独立方法",
                    "使用组合模式",
                    "考虑使用命令模式"
                ])
            
            elif issue['issue_type'] == 'too_many_parameters':
                suggestion['suggestions'].extend([
                    "使用配置对象或数据类",
                    "使用建造者模式",
                    "将相关参数组合为对象",
                    "使用依赖注入"
                ])
            
            suggestions.append(suggestion)
        
        return suggestions
    
    def extract_method_suggestion(self, file_path: Path, function_name: str) -> Optional[Dict[str, Any]]:
        """
        建议方法提取
        
        Args:
            file_path: 文件路径
            function_name: 函数名
            
        Returns:
            提取建议
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    # 分析函数体，寻找可以提取的代码块
                    extractable_blocks = self._find_extractable_blocks(node)
                    
                    if extractable_blocks:
                        return {
                            'function_name': function_name,
                            'file': str(file_path),
                            'line': node.lineno,
                            'extractable_blocks': extractable_blocks,
                            'suggestion': f"建议将函数 {function_name} 中的 {len(extractable_blocks)} 个代码块提取为独立方法"
                        }
        
        except Exception as e:
            self.logger.error(f"分析方法提取失败 {file_path}:{function_name}: {e}")
        
        return None
    
    def _find_extractable_blocks(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """
        查找可提取的代码块
        
        Args:
            node: 函数节点
            
        Returns:
            可提取的代码块列表
        """
        extractable_blocks = []
        
        for i, stmt in enumerate(node.body):
            # 查找复杂的if语句
            if isinstance(stmt, ast.If):
                if self._is_complex_condition(stmt.test):
                    extractable_blocks.append({
                        'type': 'complex_condition',
                        'line': stmt.lineno,
                        'suggestion': f"提取条件判断为独立方法: {self._get_condition_text(stmt.test)}"
                    })
            
            # 查找循环
            elif isinstance(stmt, (ast.For, ast.While)):
                if len(stmt.body) > 3:
                    extractable_blocks.append({
                        'type': 'complex_loop',
                        'line': stmt.lineno,
                        'suggestion': f"提取循环体为独立方法"
                    })
            
            # 查找try-except块
            elif isinstance(stmt, ast.Try):
                if len(stmt.body) > 2:
                    extractable_blocks.append({
                        'type': 'complex_try_except',
                        'line': stmt.lineno,
                        'suggestion': f"提取try块为独立方法"
                    })
        
        return extractable_blocks
    
    def _is_complex_condition(self, condition: ast.expr) -> bool:
        """
        判断条件是否复杂
        
        Args:
            condition: 条件表达式
            
        Returns:
            是否复杂
        """
        # 简单的复杂度判断：包含多个操作符
        operators = 0
        for node in ast.walk(condition):
            if isinstance(node, (ast.And, ast.Or, ast.Compare)):
                operators += 1
        
        return operators > 2
    
    def _get_condition_text(self, condition: ast.expr) -> str:
        """
        获取条件文本
        
        Args:
            condition: 条件表达式
            
        Returns:
            条件文本
        """
        # 这里简化处理，实际应该使用ast.unparse
        return "complex_condition"
    
    def generate_refactor_report(self, issues: List[Dict[str, Any]], 
                               suggestions: List[Dict[str, Any]]) -> str:
        """
        生成重构报告
        
        Args:
            issues: 问题列表
            suggestions: 建议列表
            
        Returns:
            报告内容
        """
        report = []
        report.append("# 代码重构报告")
        report.append("")
        
        if not issues:
            report.append("✅ 代码质量良好，无需重构")
            return "\n".join(report)
        
        # 按问题类型分组
        issues_by_type = {}
        for issue in issues:
            issue_type = issue['issue_type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)
        
        # 生成报告
        for issue_type, type_issues in issues_by_type.items():
            report.append(f"## {issue_type} 问题 ({len(type_issues)}个)")
            report.append("")
            
            for issue in type_issues:
                report.append(f"- **{issue['file']}:{issue['line']}** - {issue['message']}")
            
            report.append("")
        
        # 添加重构建议
        if suggestions:
            report.append("## 重构建议")
            report.append("")
            
            for suggestion in suggestions:
                report.append(f"### {suggestion['function_name']} ({suggestion['file']}:{suggestion['line']})")
                report.append("")
                report.append("**建议方案:**")
                for sug in suggestion['suggestions']:
                    report.append(f"- {sug}")
                report.append("")
        
        return "\n".join(report)
