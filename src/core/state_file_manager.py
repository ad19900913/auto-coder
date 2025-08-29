"""
状态文件管理器 - 负责状态文件的清理、归档和备份
"""

import os
import json
import shutil
import zipfile
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class StateFileManager:
    """状态文件管理器，负责状态文件的清理、归档和备份"""
    
    def __init__(self, config_manager):
        """
        初始化状态文件管理器
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 获取配置
        self.state_config = config_manager.get_state_management_config()
        self.work_dir = Path(config_manager.get_system_config().get('work_dir', './states'))
        self.archive_path = Path(self.state_config.get('archive_path', './archives/states'))
        
        # 创建必要的目录
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.archive_path.mkdir(parents=True, exist_ok=True)
    
    def cleanup_expired_states(self) -> int:
        """
        清理过期的状态文件
        
        Returns:
            清理的文件数量
        """
        try:
            self.logger.info("开始清理过期的状态文件...")
            
            retention_days = self.state_config.get('retention_days', 90)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cleanup_strategy = self.state_config.get('cleanup_strategy', {})
            
            cleaned_count = 0
            
            for state_file in self.work_dir.glob("*.json"):
                try:
                    # 读取状态文件
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state_data = json.load(f)
                    
                    # 检查文件是否过期
                    updated_at_str = state_data.get('updated_at')
                    if not updated_at_str:
                        continue
                    
                    try:
                        updated_at = datetime.fromisoformat(updated_at_str)
                    except ValueError:
                        self.logger.warning(f"无效的时间格式: {updated_at_str}")
                        continue
                    
                    if updated_at < cutoff_date:
                        # 文件过期，根据策略处理
                        filename = state_file.name
                        cleaned_count += self._process_expired_state(
                            state_file, filename, state_data, cleanup_strategy
                        )
                
                except Exception as e:
                    self.logger.error(f"处理状态文件失败 {state_file}: {e}")
            
            self.logger.info(f"状态文件清理完成，共处理 {cleaned_count} 个文件")
            return cleaned_count
            
        except Exception as e:
            self.logger.error(f"清理过期状态文件失败: {e}")
            return 0
    
    def _process_expired_state(self, file_path: Path, filename: str, 
                              state_data: Dict[str, Any], 
                              cleanup_strategy: Dict[str, str]) -> int:
        """
        处理过期的状态文件
        
        Args:
            file_path: 文件路径
            filename: 文件名
            state_data: 状态数据
            cleanup_strategy: 清理策略
            
        Returns:
            处理的文件数量
        """
        status = state_data.get('status', 'unknown')
        
        # 根据状态和策略决定处理方式
        if status in ['running', 'reviewing']:
            strategy = cleanup_strategy.get('running_tasks', 'skip')
        elif status in ['completed', 'approved']:
            strategy = cleanup_strategy.get('completed_tasks', 'archive')
        elif status in ['failed', 'rejected']:
            strategy = cleanup_strategy.get('failed_tasks', 'archive')
        else:
            strategy = cleanup_strategy.get('expired_tasks', 'delete')
        
        try:
            if strategy == 'archive':
                # 归档文件
                self._archive_state_file(file_path, filename, state_data)
                return 1
            elif strategy == 'delete':
                # 删除文件
                file_path.unlink()
                self.logger.info(f"删除过期状态文件: {filename}")
                return 1
            elif strategy == 'skip':
                # 跳过处理
                self.logger.debug(f"跳过过期状态文件: {filename} (状态: {status})")
                return 0
            else:
                self.logger.warning(f"未知的清理策略: {strategy}")
                return 0
                
        except Exception as e:
            self.logger.error(f"处理过期状态文件失败 {filename}: {e}")
            return 0
    
    def _archive_state_file(self, file_path: Path, filename: str, 
                           state_data: Dict[str, Any]):
        """
        归档状态文件
        
        Args:
            file_path: 文件路径
            filename: 文件名
            state_data: 状态数据
        """
        try:
            # 创建归档目录（按年月组织）
            archive_date = datetime.now()
            archive_subdir = self.archive_path / f"{archive_date.year:04d}" / f"{archive_date.month:02d}"
            archive_subdir.mkdir(parents=True, exist_ok=True)
            
            # 归档文件路径
            archive_file_path = archive_subdir / filename
            
            # 复制文件到归档目录
            shutil.copy2(file_path, archive_file_path)
            
            # 如果启用压缩，则压缩归档文件
            if self.state_config.get('archive', {}).get('compression', True):
                self._compress_archive(archive_file_path)
                # 删除未压缩的归档文件
                archive_file_path.unlink()
            
            # 删除原始状态文件
            file_path.unlink()
            
            self.logger.info(f"状态文件归档成功: {filename} -> {archive_subdir}")
            
        except Exception as e:
            self.logger.error(f"归档状态文件失败 {filename}: {e}")
            raise
    
    def _compress_archive(self, archive_path: Path):
        """
        压缩归档文件
        
        Args:
            archive_path: 归档文件路径
        """
        try:
            compression_format = self.state_config.get('archive', {}).get('compression_format', 'zip')
            
            if compression_format == 'zip':
                zip_path = archive_path.with_suffix('.zip')
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.write(archive_path, archive_path.name)
                
                self.logger.debug(f"归档文件压缩成功: {archive_path.name} -> {zip_path.name}")
            else:
                self.logger.warning(f"不支持的压缩格式: {compression_format}")
                
        except Exception as e:
            self.logger.error(f"压缩归档文件失败 {archive_path}: {e}")
            raise
    
    def get_archive_info(self) -> Dict[str, Any]:
        """
        获取归档信息
        
        Returns:
            归档信息字典
        """
        try:
            archive_info = {
                'archive_path': str(self.archive_path),
                'total_archives': 0,
                'total_size': 0,
                'compression_enabled': self.state_config.get('archive', {}).get('compression', True),
                'compression_format': self.state_config.get('archive', {}).get('compression_format', 'zip'),
                'retention_days': self.state_config.get('retention_days', 90),
                'cleanup_enabled': self.state_config.get('cleanup_enabled', True),
                'cleanup_schedule': self.state_config.get('cleanup_schedule', '0 2 * * *'),
                'backup_enabled': self.state_config.get('state_file', {}).get('backup_enabled', True)
            }
            
            # 统计归档文件数量和大小
            if self.archive_path.exists():
                for file_path in self.archive_path.rglob("*"):
                    if file_path.is_file():
                        archive_info['total_archives'] += 1
                        archive_info['total_size'] += file_path.stat().st_size
            
            # 转换文件大小为可读格式
            archive_info['total_size_mb'] = round(archive_info['total_size'] / (1024 * 1024), 2)
            
            return archive_info
            
        except Exception as e:
            self.logger.error(f"获取归档信息失败: {e}")
            return {}
