"""
示例服务类 - 用于演示增量修改功能
"""

import logging
from typing import List, Dict, Any


class ExampleService:
    """示例服务类，用于演示增量修改功能"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_cache = {}
    
    def process_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        处理数据
        
        Args:
            data: 要处理的数据列表
            
        Returns:
            处理结果
        """
        result = {
            'total_count': len(data),
            'processed_count': 0,
            'errors': []
        }
        
        for item in data:
            try:
                # 处理单个数据项
                self._process_single_item(item)
                result['processed_count'] += 1
            except Exception as e:
                result['errors'].append(str(e))
        
        return result
    
    def _process_single_item(self, item: Dict[str, Any]):
        """处理单个数据项"""
        # 这里是一些示例处理逻辑
        if 'id' not in item:
            raise ValueError("数据项缺少id字段")
        
        # 缓存处理结果
        self.data_cache[item['id']] = item
    
    def get_cached_data(self, item_id: str) -> Dict[str, Any]:
        """
        获取缓存的数据
        
        Args:
            item_id: 数据项ID
            
        Returns:
            缓存的数据
        """
        return self.data_cache.get(item_id, {})
    
    def clear_cache(self):
        """清空缓存"""
        self.data_cache.clear()
        self.logger.info("缓存已清空")
