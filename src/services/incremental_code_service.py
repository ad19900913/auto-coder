"""
增量代码修改服务 - 支持读取现有代码并进行增量修改
"""

import logging
import os
import re
import ast
import difflib
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime


class IncrementalCodeService:
    """增量代码修改服务，支持读取现有代码并进行增量修改"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def read_existing_code(self, file_path: str) -> Optional[str]:
        """
        读取现有代码文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容，如果文件不存在则返回None
        """
        try:
            if not os.path.exists(file_path):
                self.logger.info(f"文件不存在，将创建新文件: {file_path}")
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.info(f"成功读取现有代码文件: {file_path}, 长度: {len(content)} 字符")
            return content
            
        except Exception as e:
            self.logger.error(f"读取现有代码文件失败: {e}")
            return None
    
    def analyze_code_structure(self, code_content: str, language: str = 'python') -> Dict[str, Any]:
        """
        分析代码结构
        
        Args:
            code_content: 代码内容
            language: 编程语言
            
        Returns:
            代码结构分析结果
        """
        try:
            if language.lower() == 'python':
                return self._analyze_python_structure(code_content)
            elif language.lower() in ['javascript', 'js']:
                return self._analyze_javascript_structure(code_content)
            elif language.lower() in ['java']:
                return self._analyze_java_structure(code_content)
            else:
                return self._analyze_generic_structure(code_content)
                
        except Exception as e:
            self.logger.error(f"分析代码结构失败: {e}")
            return {'error': str(e)}
    
    def _analyze_python_structure(self, code_content: str) -> Dict[str, Any]:
        """分析Python代码结构"""
        try:
            tree = ast.parse(code_content)
            
            classes = []
            functions = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    })
                elif isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args]
                    })
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
            
            return {
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'total_lines': len(code_content.splitlines()),
                'language': 'python'
            }
            
        except SyntaxError as e:
            return {
                'error': f'语法错误: {e}',
                'language': 'python'
            }
    
    def _analyze_javascript_structure(self, code_content: str) -> Dict[str, Any]:
        """分析JavaScript代码结构"""
        classes = []
        functions = []
        imports = []
        
        # 使用正则表达式分析JavaScript结构
        lines = code_content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检测类定义
            class_match = re.match(r'class\s+(\w+)', line)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line': i
                })
            
            # 检测函数定义
            func_match = re.match(r'(?:function\s+)?(\w+)\s*\(', line)
            if func_match and not line.startswith('if') and not line.startswith('for'):
                functions.append({
                    'name': func_match.group(1),
                    'line': i
                })
            
            # 检测导入语句
            if line.startswith('import ') or line.startswith('const ') or line.startswith('let '):
                imports.append(line)
        
        return {
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'total_lines': len(lines),
            'language': 'javascript'
        }
    
    def _analyze_java_structure(self, code_content: str) -> Dict[str, Any]:
        """分析Java代码结构"""
        classes = []
        methods = []
        imports = []
        
        lines = code_content.splitlines()
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # 检测类定义
            class_match = re.match(r'(?:public\s+)?class\s+(\w+)', line)
            if class_match:
                classes.append({
                    'name': class_match.group(1),
                    'line': i
                })
            
            # 检测方法定义
            method_match = re.match(r'(?:public|private|protected)?\s*(?:\w+\s+)?(\w+)\s*\(', line)
            if method_match and not line.startswith('if') and not line.startswith('for'):
                methods.append({
                    'name': method_match.group(1),
                    'line': i
                })
            
            # 检测导入语句
            if line.startswith('import '):
                imports.append(line)
        
        return {
            'classes': classes,
            'methods': methods,
            'imports': imports,
            'total_lines': len(lines),
            'language': 'java'
        }
    
    def _analyze_generic_structure(self, code_content: str) -> Dict[str, Any]:
        """通用代码结构分析"""
        lines = code_content.splitlines()
        
        return {
            'total_lines': len(lines),
            'language': 'generic',
            'content_preview': code_content[:500] + '...' if len(code_content) > 500 else code_content
        }
    
    def generate_incremental_prompt(self, existing_code: str, modification_request: str, 
                                  code_structure: Dict[str, Any], language: str = 'python') -> str:
        """
        生成增量修改的AI提示
        
        Args:
            existing_code: 现有代码
            modification_request: 修改请求
            code_structure: 代码结构分析结果
            language: 编程语言
            
        Returns:
            增量修改的AI提示
        """
        prompt = f"""
请根据以下要求对现有代码进行增量修改：

【现有代码】
```{language}
{existing_code}
```

【代码结构分析】
- 语言: {code_structure.get('language', 'unknown')}
- 总行数: {code_structure.get('total_lines', 0)}
- 类数量: {len(code_structure.get('classes', []))}
- 函数/方法数量: {len(code_structure.get('functions', [])) + len(code_structure.get('methods', []))}

【修改要求】
{modification_request}

【修改规则】
1. 只修改必要的部分，保持现有代码结构
2. 保持现有的导入语句和依赖关系
3. 保持现有的函数签名和类结构
4. 只添加或修改指定的功能，不要重写整个文件
5. 确保修改后的代码语法正确且可运行
6. 如果需要在现有类中添加方法，请在合适的位置插入
7. 如果需要在现有函数中修改逻辑，请保持函数签名不变

请返回完整的修改后的代码文件内容。
"""
        return prompt
    
    def apply_incremental_changes(self, original_code: str, new_code: str, 
                                file_path: str, backup: bool = True) -> Dict[str, Any]:
        """
        应用增量修改
        
        Args:
            original_code: 原始代码
            new_code: 新代码
            file_path: 文件路径
            backup: 是否创建备份
            
        Returns:
            修改结果
        """
        try:
            # 创建备份
            if backup and original_code:
                backup_path = self._create_backup(file_path)
            
            # 生成差异报告
            diff_report = self._generate_diff_report(original_code, new_code)
            
            # 写入新代码
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_code)
            
            result = {
                'success': True,
                'file_path': file_path,
                'backup_path': backup_path if backup and original_code else None,
                'diff_report': diff_report,
                'original_length': len(original_code) if original_code else 0,
                'new_length': len(new_code),
                'changes_made': len(new_code) - len(original_code) if original_code else len(new_code)
            }
            
            self.logger.info(f"增量修改应用成功: {file_path}")
            return result
            
        except Exception as e:
            self.logger.error(f"应用增量修改失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _create_backup(self, file_path: str) -> str:
        """创建文件备份"""
        try:
            backup_dir = Path(file_path).parent / '.backups'
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{Path(file_path).stem}_{timestamp}{Path(file_path).suffix}"
            backup_path = backup_dir / backup_name
            
            # 复制原文件到备份
            import shutil
            shutil.copy2(file_path, backup_path)
            
            self.logger.info(f"备份文件创建成功: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            self.logger.error(f"创建备份失败: {e}")
            return None
    
    def _generate_diff_report(self, original_code: str, new_code: str) -> str:
        """生成差异报告"""
        try:
            original_lines = original_code.splitlines(keepends=True) if original_code else []
            new_lines = new_code.splitlines(keepends=True)
            
            diff = difflib.unified_diff(
                original_lines,
                new_lines,
                fromfile='original',
                tofile='modified',
                lineterm=''
            )
            
            diff_report = '\n'.join(diff)
            return diff_report
            
        except Exception as e:
            self.logger.error(f"生成差异报告失败: {e}")
            return f"差异报告生成失败: {e}"
    
    def validate_code_syntax(self, code_content: str, language: str = 'python') -> Dict[str, Any]:
        """
        验证代码语法
        
        Args:
            code_content: 代码内容
            language: 编程语言
            
        Returns:
            验证结果
        """
        try:
            if language.lower() == 'python':
                ast.parse(code_content)
                return {'valid': True, 'language': 'python'}
            else:
                # 对于其他语言，暂时返回基本验证
                return {'valid': True, 'language': language, 'note': '基本验证通过'}
                
        except SyntaxError as e:
            return {
                'valid': False,
                'error': str(e),
                'language': language
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'language': language
            }
