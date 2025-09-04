"""
复杂重构服务 - 支持大型项目的复杂重构操作
"""

import logging
import os
import re
import ast
import json
import networkx as nx
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class ComplexRefactorService:
    """复杂重构服务，支持大型项目的复杂重构操作"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.dependency_graph = nx.DiGraph()
        self.file_analysis_cache = {}
        self.refactor_plan = {}
        
    def analyze_project_structure(self, project_path: str, 
                                 include_patterns: List[str] = None,
                                 exclude_patterns: List[str] = None) -> Dict[str, Any]:
        """
        分析项目结构，包括文件依赖关系、模块结构等
        
        Args:
            project_path: 项目根路径
            include_patterns: 包含的文件模式
            exclude_patterns: 排除的文件模式
            
        Returns:
            项目结构分析结果
        """
        try:
            self.logger.info(f"开始分析项目结构: {project_path}")
            
            analysis_result = {
                'project_path': project_path,
                'total_files': 0,
                'modules': {},
                'dependencies': {},
                'file_graph': {},
                'complexity_metrics': {},
                'refactor_hotspots': []
            }
            
            # 设置项目路径到依赖图
            self.dependency_graph.graph['project_path'] = project_path
            
            # 扫描项目文件
            all_files = self._scan_project_files(project_path, include_patterns, exclude_patterns)
            analysis_result['total_files'] = len(all_files)
            
            # 分析每个文件
            for file_path in all_files:
                file_analysis = self._analyze_single_file(file_path)
                if file_analysis:
                    self.file_analysis_cache[file_path] = file_analysis
                    
                    # 构建依赖图
                    self._build_dependency_graph(file_path, file_analysis)
            
            # 分析模块结构
            analysis_result['modules'] = self._analyze_module_structure()
            
            # 分析依赖关系
            analysis_result['dependencies'] = self._analyze_dependencies()
            
            # 计算复杂度指标
            analysis_result['complexity_metrics'] = self._calculate_complexity_metrics()
            
            # 识别重构热点
            analysis_result['refactor_hotspots'] = self._identify_refactor_hotspots()
            
            self.logger.info(f"项目结构分析完成，共分析 {analysis_result['total_files']} 个文件")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"项目结构分析失败: {e}")
            return {'error': str(e)}
    
    def _scan_project_files(self, project_path: str, 
                           include_patterns: List[str] = None,
                           exclude_patterns: List[str] = None) -> List[str]:
        """扫描项目文件"""
        all_files = []
        
        # 默认包含模式
        if not include_patterns:
            include_patterns = ['*.py', '*.java', '*.js', '*.ts', '*.cpp', '*.c', '*.h']
        
        # 默认排除模式
        if not exclude_patterns:
            exclude_patterns = [
                '*/node_modules/*', '*/venv/*', '*/__pycache__/*', 
                '*/target/*', '*/build/*', '*/.git/*', '*/dist/*'
            ]
        
        for root, dirs, files in os.walk(project_path):
            # 排除目录
            dirs[:] = [d for d in dirs if not any(self._match_pattern(os.path.join(root, d), pattern) 
                                                for pattern in exclude_patterns)]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查是否匹配包含模式
                if any(self._match_pattern(file_path, pattern) for pattern in include_patterns):
                    # 检查是否匹配排除模式
                    if not any(self._match_pattern(file_path, pattern) for pattern in exclude_patterns):
                        all_files.append(file_path)
        
        return all_files
    
    def _match_pattern(self, file_path: str, pattern: str) -> bool:
        """匹配文件路径模式"""
        try:
            # 将glob模式转换为正则表达式
            pattern = pattern.replace('*', '.*').replace('?', '.')
            pattern = pattern.replace('/', r'\/').replace('\\', r'\\')
            return bool(re.match(pattern, file_path))
        except Exception:
            return False
    
    def _analyze_single_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext == '.py':
                return self._analyze_python_file(file_path, content)
            elif file_ext in ['.js', '.ts']:
                return self._analyze_javascript_file(file_path, content)
            elif file_ext == '.java':
                return self._analyze_java_file(file_path, content)
            else:
                return self._analyze_generic_file(file_path, content)
                
        except Exception as e:
            self.logger.warning(f"分析文件失败 {file_path}: {e}")
            return None
    
    def _analyze_python_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """分析Python文件"""
        try:
            tree = ast.parse(content)
            
            classes = []
            functions = []
            imports = []
            dependencies = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'bases': [base.id for base in node.bases if isinstance(base, ast.Name)]
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
                        dependencies.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        imports.append(f"{module}.{alias.name}")
                        dependencies.append(module)
            
            return {
                'type': 'python',
                'classes': classes,
                'functions': functions,
                'imports': imports,
                'dependencies': list(set(dependencies)),
                'lines': len(content.splitlines()),
                'complexity': self._calculate_file_complexity(content)
            }
            
        except SyntaxError:
            return {
                'type': 'python',
                'error': 'syntax_error',
                'lines': len(content.splitlines())
            }
    
    def _analyze_javascript_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """分析JavaScript文件"""
        classes = []
        functions = []
        imports = []
        dependencies = []
        
        lines = content.splitlines()
        
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
            if line.startswith('import '):
                imports.append(line)
                # 提取模块名
                module_match = re.search(r'from\s+[\'"]([^\'"]+)[\'"]', line)
                if module_match:
                    dependencies.append(module_match.group(1))
            elif line.startswith('const ') or line.startswith('let '):
                imports.append(line)
        
        return {
            'type': 'javascript',
            'classes': classes,
            'functions': functions,
            'imports': imports,
            'dependencies': list(set(dependencies)),
            'lines': len(lines),
            'complexity': self._calculate_file_complexity(content)
        }
    
    def _analyze_java_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """分析Java文件"""
        classes = []
        methods = []
        imports = []
        dependencies = []
        
        lines = content.splitlines()
        
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
                # 提取包名
                package_match = re.search(r'import\s+([^;]+);', line)
                if package_match:
                    dependencies.append(package_match.group(1))
        
        return {
            'type': 'java',
            'classes': classes,
            'methods': methods,
            'imports': imports,
            'dependencies': list(set(dependencies)),
            'lines': len(lines),
            'complexity': self._calculate_file_complexity(content)
        }
    
    def _analyze_generic_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """通用文件分析"""
        return {
            'type': 'generic',
            'lines': len(content.splitlines()),
            'complexity': self._calculate_file_complexity(content)
        }
    
    def _calculate_file_complexity(self, content: str) -> Dict[str, Any]:
        """计算文件复杂度"""
        lines = content.splitlines()
        
        # 计算圈复杂度（简化版）
        complexity = 1  # 基础复杂度
        for line in lines:
            line = line.strip()
            if any(keyword in line for keyword in ['if ', 'for ', 'while ', 'case ', 'catch ', '&&', '||']):
                complexity += 1
        
        return {
            'cyclomatic': complexity,
            'lines_of_code': len(lines),
            'comment_ratio': self._calculate_comment_ratio(content)
        }
    
    def _calculate_comment_ratio(self, content: str) -> float:
        """计算注释比例"""
        lines = content.splitlines()
        comment_lines = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
                comment_lines += 1
        
        return comment_lines / len(lines) if lines else 0
    
    def _build_dependency_graph(self, file_path: str, file_analysis: Dict[str, Any]):
        """构建依赖图"""
        # 添加文件节点
        self.dependency_graph.add_node(file_path, **file_analysis)
        
        # 添加依赖边
        for dep in file_analysis.get('dependencies', []):
            # 这里可以进一步解析依赖关系
            self.dependency_graph.add_edge(file_path, dep)
    
    def _analyze_module_structure(self) -> Dict[str, Any]:
        """分析模块结构"""
        modules = defaultdict(list)
        
        for file_path, analysis in self.file_analysis_cache.items():
            try:
                # 根据文件路径确定模块
                relative_path = os.path.relpath(file_path, self.dependency_graph.graph.get('project_path', ''))
                module_name = relative_path.split(os.sep)[0] if os.sep in relative_path else 'root'
                
                modules[module_name].append({
                    'file': file_path,
                    'analysis': analysis
                })
            except ValueError:
                # 处理跨磁盘的路径问题
                module_name = 'external'
                modules[module_name].append({
                    'file': file_path,
                    'analysis': analysis
                })
        
        return dict(modules)
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖关系"""
        # 计算入度和出度
        in_degrees = dict(self.dependency_graph.in_degree())
        out_degrees = dict(self.dependency_graph.out_degree())
        
        # 识别循环依赖
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
        except:
            cycles = []
        
        # 识别强连通分量
        strongly_connected = list(nx.strongly_connected_components(self.dependency_graph))
        
        return {
            'in_degrees': in_degrees,
            'out_degrees': out_degrees,
            'cycles': cycles,
            'strongly_connected': [list(comp) for comp in strongly_connected if len(comp) > 1]
        }
    
    def _calculate_complexity_metrics(self) -> Dict[str, Any]:
        """计算复杂度指标"""
        total_complexity = 0
        total_lines = 0
        file_complexities = []
        
        for analysis in self.file_analysis_cache.values():
            complexity = analysis.get('complexity', {})
            total_complexity += complexity.get('cyclomatic', 0)
            total_lines += complexity.get('lines_of_code', 0)
            file_complexities.append(complexity.get('cyclomatic', 0))
        
        return {
            'total_complexity': total_complexity,
            'total_lines': total_lines,
            'average_complexity': total_complexity / len(self.file_analysis_cache) if self.file_analysis_cache else 0,
            'max_complexity': max(file_complexities) if file_complexities else 0,
            'complexity_distribution': self._calculate_complexity_distribution(file_complexities)
        }
    
    def _calculate_complexity_distribution(self, complexities: List[int]) -> Dict[str, int]:
        """计算复杂度分布"""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'very_high': 0}
        
        for complexity in complexities:
            if complexity <= 5:
                distribution['low'] += 1
            elif complexity <= 10:
                distribution['medium'] += 1
            elif complexity <= 20:
                distribution['high'] += 1
            else:
                distribution['very_high'] += 1
        
        return distribution
    
    def _identify_refactor_hotspots(self) -> List[Dict[str, Any]]:
        """识别重构热点"""
        hotspots = []
        
        for file_path, analysis in self.file_analysis_cache.items():
            complexity = analysis.get('complexity', {})
            cyclomatic = complexity.get('cyclomatic', 0)
            
            # 高复杂度文件
            if cyclomatic > 15:
                hotspots.append({
                    'file': file_path,
                    'type': 'high_complexity',
                    'metric': cyclomatic,
                    'priority': 'high'
                })
            
            # 大文件
            lines = complexity.get('lines_of_code', 0)
            if lines > 500:
                hotspots.append({
                    'file': file_path,
                    'type': 'large_file',
                    'metric': lines,
                    'priority': 'medium'
                })
            
            # 低注释比例
            comment_ratio = complexity.get('comment_ratio', 0)
            if comment_ratio < 0.1:
                hotspots.append({
                    'file': file_path,
                    'type': 'low_comments',
                    'metric': comment_ratio,
                    'priority': 'low'
                })
        
        # 按优先级排序
        hotspots.sort(key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x['priority']], reverse=True)
        
        return hotspots
    
    def generate_refactor_plan(self, refactor_request: str, 
                             project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成重构计划
        
        Args:
            refactor_request: 重构请求描述
            project_analysis: 项目分析结果
            
        Returns:
            重构计划
        """
        try:
            self.logger.info("开始生成重构计划")
            
            # 分析重构请求
            refactor_analysis = self._analyze_refactor_request(refactor_request)
            
            # 识别受影响的文件
            affected_files = self._identify_affected_files(refactor_analysis, project_analysis)
            
            # 生成重构步骤
            refactor_steps = self._generate_refactor_steps(refactor_analysis, affected_files)
            
            # 评估风险和影响
            risk_assessment = self._assess_refactor_risks(refactor_steps, project_analysis)
            
            # 生成测试策略
            test_strategy = self._generate_test_strategy(refactor_steps, affected_files)
            
            refactor_plan = {
                'refactor_request': refactor_request,
                'refactor_analysis': refactor_analysis,
                'affected_files': affected_files,
                'refactor_steps': refactor_steps,
                'risk_assessment': risk_assessment,
                'test_strategy': test_strategy,
                'estimated_effort': self._estimate_effort(refactor_steps),
                'dependencies': self._analyze_refactor_dependencies(refactor_steps)
            }
            
            self.refactor_plan = refactor_plan
            self.logger.info("重构计划生成完成")
            
            return refactor_plan
            
        except Exception as e:
            self.logger.error(f"生成重构计划失败: {e}")
            return {'error': str(e)}
    
    def _analyze_refactor_request(self, refactor_request: str) -> Dict[str, Any]:
        """分析重构请求"""
        # 这里可以使用NLP技术分析重构请求
        # 暂时使用简单的关键词匹配
        
        refactor_types = []
        if 'rename' in refactor_request.lower():
            refactor_types.append('rename')
        if 'extract' in refactor_request.lower():
            refactor_types.append('extract')
        if 'move' in refactor_request.lower():
            refactor_types.append('move')
        if 'split' in refactor_request.lower():
            refactor_types.append('split')
        if 'merge' in refactor_request.lower():
            refactor_types.append('merge')
        if 'optimize' in refactor_request.lower():
            refactor_types.append('optimize')
        
        return {
            'types': refactor_types,
            'description': refactor_request,
            'scope': self._estimate_refactor_scope(refactor_request)
        }
    
    def _estimate_refactor_scope(self, refactor_request: str) -> str:
        """估算重构范围"""
        if any(keyword in refactor_request.lower() for keyword in ['class', 'method', 'function']):
            return 'method_level'
        elif any(keyword in refactor_request.lower() for keyword in ['module', 'package', 'namespace']):
            return 'module_level'
        elif any(keyword in refactor_request.lower() for keyword in ['architecture', 'structure', 'design']):
            return 'architecture_level'
        else:
            return 'file_level'
    
    def _identify_affected_files(self, refactor_analysis: Dict[str, Any], 
                               project_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别受影响的文件"""
        affected_files = []
        
        # 根据重构类型和范围识别受影响文件
        scope = refactor_analysis.get('scope', 'file_level')
        
        if scope == 'method_level':
            # 方法级重构，影响相对较小
            affected_files = self._identify_method_level_affected_files(refactor_analysis)
        elif scope == 'module_level':
            # 模块级重构，影响中等
            affected_files = self._identify_module_level_affected_files(refactor_analysis)
        elif scope == 'architecture_level':
            # 架构级重构，影响较大
            affected_files = self._identify_architecture_level_affected_files(refactor_analysis)
        
        return affected_files
    
    def _identify_method_level_affected_files(self, refactor_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别方法级重构的受影响文件"""
        # 这里需要根据具体的重构请求来识别
        # 暂时返回空列表
        return []
    
    def _identify_module_level_affected_files(self, refactor_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别模块级重构的受影响文件"""
        # 这里需要根据具体的重构请求来识别
        # 暂时返回空列表
        return []
    
    def _identify_architecture_level_affected_files(self, refactor_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """识别架构级重构的受影响文件"""
        # 架构级重构通常影响整个项目
        affected_files = []
        
        for file_path, analysis in self.file_analysis_cache.items():
            affected_files.append({
                'file': file_path,
                'impact_level': 'high',
                'reason': 'architecture_level_refactor',
                'analysis': analysis
            })
        
        return affected_files
    
    def _generate_refactor_steps(self, refactor_analysis: Dict[str, Any], 
                               affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成重构步骤"""
        steps = []
        
        # 根据重构类型生成具体步骤
        refactor_types = refactor_analysis.get('types', [])
        
        for refactor_type in refactor_types:
            if refactor_type == 'rename':
                steps.extend(self._generate_rename_steps(affected_files))
            elif refactor_type == 'extract':
                steps.extend(self._generate_extract_steps(affected_files))
            elif refactor_type == 'move':
                steps.extend(self._generate_move_steps(affected_files))
            elif refactor_type == 'split':
                steps.extend(self._generate_split_steps(affected_files))
            elif refactor_type == 'merge':
                steps.extend(self._generate_merge_steps(affected_files))
            elif refactor_type == 'optimize':
                steps.extend(self._generate_optimize_steps(affected_files))
        
        # 添加通用步骤
        steps.extend(self._generate_common_steps(affected_files))
        
        return steps
    
    def _generate_rename_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成重命名步骤"""
        return [
            {
                'step_id': 'rename_1',
                'type': 'rename',
                'description': '重命名类、方法或变量',
                'actions': [
                    '识别需要重命名的元素',
                    '更新所有引用',
                    '更新文档和注释',
                    '运行测试验证'
                ],
                'estimated_time': '2-4 hours',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_extract_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成提取步骤"""
        return [
            {
                'step_id': 'extract_1',
                'type': 'extract',
                'description': '提取方法、类或模块',
                'actions': [
                    '识别可提取的代码块',
                    '创建新的方法/类/模块',
                    '移动代码到新位置',
                    '更新调用点',
                    '验证功能正确性'
                ],
                'estimated_time': '4-8 hours',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_move_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成移动步骤"""
        return [
            {
                'step_id': 'move_1',
                'type': 'move',
                'description': '移动文件或代码到新位置',
                'actions': [
                    '确定目标位置',
                    '移动文件或代码',
                    '更新导入语句',
                    '更新配置文件',
                    '验证路径正确性'
                ],
                'estimated_time': '2-6 hours',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_split_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成拆分步骤"""
        return [
            {
                'step_id': 'split_1',
                'type': 'split',
                'description': '拆分大型类或方法',
                'actions': [
                    '分析类的职责',
                    '识别拆分点',
                    '创建新的类',
                    '移动相关方法',
                    '更新依赖关系'
                ],
                'estimated_time': '6-12 hours',
                'risk_level': 'high'
            }
        ]
    
    def _generate_merge_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成合并步骤"""
        return [
            {
                'step_id': 'merge_1',
                'type': 'merge',
                'description': '合并相似或相关的类',
                'actions': [
                    '识别可合并的类',
                    '分析合并策略',
                    '合并类定义',
                    '更新所有引用',
                    '清理冗余代码'
                ],
                'estimated_time': '4-10 hours',
                'risk_level': 'high'
            }
        ]
    
    def _generate_optimize_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成优化步骤"""
        return [
            {
                'step_id': 'optimize_1',
                'type': 'optimize',
                'description': '优化代码性能和结构',
                'actions': [
                    '识别性能瓶颈',
                    '优化算法和数据结构',
                    '减少代码重复',
                    '改进代码可读性',
                    '性能测试验证'
                ],
                'estimated_time': '8-16 hours',
                'risk_level': 'medium'
            }
        ]
    
    def _generate_common_steps(self, affected_files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成通用步骤"""
        return [
            {
                'step_id': 'backup_1',
                'type': 'backup',
                'description': '创建备份',
                'actions': [
                    '创建项目备份',
                    '创建Git分支',
                    '记录当前状态'
                ],
                'estimated_time': '30 minutes',
                'risk_level': 'low'
            },
            {
                'step_id': 'test_1',
                'type': 'test',
                'description': '运行测试',
                'actions': [
                    '运行单元测试',
                    '运行集成测试',
                    '运行回归测试',
                    '验证功能正确性'
                ],
                'estimated_time': '2-4 hours',
                'risk_level': 'low'
            },
            {
                'step_id': 'deploy_1',
                'type': 'deploy',
                'description': '部署和验证',
                'actions': [
                    '部署到测试环境',
                    '进行功能验证',
                    '性能测试',
                    '用户验收测试'
                ],
                'estimated_time': '4-8 hours',
                'risk_level': 'medium'
            }
        ]
    
    def _assess_refactor_risks(self, refactor_steps: List[Dict[str, Any]], 
                             project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """评估重构风险"""
        total_risk_score = 0
        risk_factors = []
        
        for step in refactor_steps:
            risk_level = step.get('risk_level', 'low')
            risk_score = {'low': 1, 'medium': 2, 'high': 3}[risk_level]
            total_risk_score += risk_score
            
            risk_factors.append({
                'step': step['step_id'],
                'risk_level': risk_level,
                'risk_score': risk_score,
                'description': step['description']
            })
        
        # 考虑项目复杂度
        complexity_metrics = project_analysis.get('complexity_metrics', {})
        if complexity_metrics.get('average_complexity', 0) > 10:
            total_risk_score += 2
            risk_factors.append({
                'step': 'project_complexity',
                'risk_level': 'high',
                'risk_score': 2,
                'description': '项目整体复杂度较高'
            })
        
        return {
            'total_risk_score': total_risk_score,
            'risk_level': 'high' if total_risk_score > 10 else 'medium' if total_risk_score > 5 else 'low',
            'risk_factors': risk_factors,
            'mitigation_strategies': self._generate_risk_mitigation_strategies(risk_factors)
        }
    
    def _generate_risk_mitigation_strategies(self, risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成风险缓解策略"""
        strategies = []
        
        for factor in risk_factors:
            if factor['risk_level'] == 'high':
                strategies.append({
                    'risk_factor': factor['step'],
                    'strategy': '分步执行，每步后进行充分测试',
                    'priority': 'high'
                })
            elif factor['risk_level'] == 'medium':
                strategies.append({
                    'risk_factor': factor['step'],
                    'strategy': '准备回滚方案，监控执行过程',
                    'priority': 'medium'
                })
        
        return strategies
    
    def _generate_test_strategy(self, refactor_steps: List[Dict[str, Any]], 
                              affected_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成测试策略"""
        return {
            'unit_tests': {
                'scope': 'affected_files',
                'coverage_target': 90,
                'focus_areas': ['refactored_methods', 'changed_interfaces']
            },
            'integration_tests': {
                'scope': 'affected_modules',
                'focus_areas': ['module_interactions', 'data_flow']
            },
            'regression_tests': {
                'scope': 'full_project',
                'focus_areas': ['existing_functionality', 'performance']
            },
            'manual_tests': {
                'scope': 'user_scenarios',
                'focus_areas': ['critical_paths', 'user_experience']
            }
        }
    
    def _estimate_effort(self, refactor_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """估算工作量"""
        total_hours = 0
        step_efforts = []
        
        for step in refactor_steps:
            time_str = step.get('estimated_time', '1 hour')
            # 简单的时间解析
            if '-' in time_str:
                min_time, max_time = time_str.split('-')
                avg_time = (int(min_time.split()[0]) + int(max_time.split()[0])) / 2
            else:
                avg_time = int(time_str.split()[0])
            
            total_hours += avg_time
            step_efforts.append({
                'step': step['step_id'],
                'estimated_time': time_str,
                'avg_hours': avg_time
            })
        
        return {
            'total_hours': total_hours,
            'estimated_days': total_hours / 8,  # 假设每天8小时工作
            'step_efforts': step_efforts
        }
    
    def _analyze_refactor_dependencies(self, refactor_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析重构步骤间的依赖关系"""
        dependencies = []
        
        # 分析步骤间的依赖
        for i, step in enumerate(refactor_steps):
            for j, other_step in enumerate(refactor_steps[i+1:], i+1):
                # 简单的依赖分析逻辑
                if self._has_dependency(step, other_step):
                    dependencies.append({
                        'from_step': step['step_id'],
                        'to_step': other_step['step_id'],
                        'dependency_type': 'required'
                    })
        
        return {
            'dependencies': dependencies,
            'execution_order': self._determine_execution_order(refactor_steps, dependencies)
        }
    
    def _has_dependency(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> bool:
        """判断两个步骤是否有依赖关系"""
        # 简单的依赖判断逻辑
        if step1['type'] == 'backup' and step2['type'] != 'backup':
            return True
        if step1['type'] == 'test' and step2['type'] in ['rename', 'extract', 'move', 'split', 'merge']:
            return True
        return False
    
    def _determine_execution_order(self, steps: List[Dict[str, Any]], 
                                 dependencies: List[Dict[str, Any]]) -> List[str]:
        """确定执行顺序"""
        # 使用拓扑排序确定执行顺序
        step_ids = [step['step_id'] for step in steps]
        dep_graph = nx.DiGraph()
        
        for dep in dependencies:
            dep_graph.add_edge(dep['from_step'], dep['to_step'])
        
        try:
            execution_order = list(nx.topological_sort(dep_graph))
            # 添加没有依赖的步骤
            for step_id in step_ids:
                if step_id not in execution_order:
                    execution_order.append(step_id)
            return execution_order
        except nx.NetworkXError:
            # 如果有循环依赖，返回原始顺序
            return step_ids
    
    def execute_refactor_step(self, step_id: str, 
                            refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行重构步骤
        
        Args:
            step_id: 步骤ID
            refactor_plan: 重构计划
            
        Returns:
            执行结果
        """
        try:
            self.logger.info(f"开始执行重构步骤: {step_id}")
            
            # 查找步骤
            step = None
            for s in refactor_plan.get('refactor_steps', []):
                if s['step_id'] == step_id:
                    step = s
                    break
            
            if not step:
                raise ValueError(f"未找到重构步骤: {step_id}")
            
            # 执行步骤
            result = self._execute_single_step(step, refactor_plan)
            
            self.logger.info(f"重构步骤执行完成: {step_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"执行重构步骤失败: {e}")
            return {'error': str(e)}
    
    def _execute_single_step(self, step: Dict[str, Any], 
                           refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个重构步骤"""
        step_type = step.get('type', '')
        
        if step_type == 'backup':
            return self._execute_backup_step(step, refactor_plan)
        elif step_type == 'rename':
            return self._execute_rename_step(step, refactor_plan)
        elif step_type == 'extract':
            return self._execute_extract_step(step, refactor_plan)
        elif step_type == 'move':
            return self._execute_move_step(step, refactor_plan)
        elif step_type == 'split':
            return self._execute_split_step(step, refactor_plan)
        elif step_type == 'merge':
            return self._execute_merge_step(step, refactor_plan)
        elif step_type == 'optimize':
            return self._execute_optimize_step(step, refactor_plan)
        elif step_type == 'test':
            return self._execute_test_step(step, refactor_plan)
        elif step_type == 'deploy':
            return self._execute_deploy_step(step, refactor_plan)
        else:
            return {'error': f'不支持的重构步骤类型: {step_type}'}
    
    def _execute_backup_step(self, step: Dict[str, Any], 
                           refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行备份步骤"""
        try:
            # 创建备份
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 复制项目文件
            project_path = refactor_plan.get('project_analysis', {}).get('project_path', '')
            if project_path:
                import shutil
                shutil.copytree(project_path, os.path.join(backup_dir, 'project'))
            
            return {
                'success': True,
                'backup_dir': backup_dir,
                'message': '项目备份创建成功'
            }
        except Exception as e:
            return {'error': f'备份失败: {e}'}
    
    def _execute_rename_step(self, step: Dict[str, Any], 
                           refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行重命名步骤"""
        # 这里需要具体的重命名逻辑
        return {
            'success': True,
            'message': '重命名步骤执行完成（模拟）'
        }
    
    def _execute_extract_step(self, step: Dict[str, Any], 
                            refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行提取步骤"""
        # 这里需要具体的提取逻辑
        return {
            'success': True,
            'message': '提取步骤执行完成（模拟）'
        }
    
    def _execute_move_step(self, step: Dict[str, Any], 
                         refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行移动步骤"""
        # 这里需要具体的移动逻辑
        return {
            'success': True,
            'message': '移动步骤执行完成（模拟）'
        }
    
    def _execute_split_step(self, step: Dict[str, Any], 
                          refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行拆分步骤"""
        # 这里需要具体的拆分逻辑
        return {
            'success': True,
            'message': '拆分步骤执行完成（模拟）'
        }
    
    def _execute_merge_step(self, step: Dict[str, Any], 
                          refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行合并步骤"""
        # 这里需要具体的合并逻辑
        return {
            'success': True,
            'message': '合并步骤执行完成（模拟）'
        }
    
    def _execute_optimize_step(self, step: Dict[str, Any], 
                             refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行优化步骤"""
        # 这里需要具体的优化逻辑
        return {
            'success': True,
            'message': '优化步骤执行完成（模拟）'
        }
    
    def _execute_test_step(self, step: Dict[str, Any], 
                         refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试步骤"""
        # 这里需要具体的测试逻辑
        return {
            'success': True,
            'message': '测试步骤执行完成（模拟）'
        }
    
    def _execute_deploy_step(self, step: Dict[str, Any], 
                           refactor_plan: Dict[str, Any]) -> Dict[str, Any]:
        """执行部署步骤"""
        # 这里需要具体的部署逻辑
        return {
            'success': True,
            'message': '部署步骤执行完成（模拟）'
        }
