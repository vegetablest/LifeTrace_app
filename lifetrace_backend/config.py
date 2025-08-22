import os
import yaml
from pathlib import Path
from typing import Optional, List

class LifeTraceConfig:
    """LifeTrace配置管理类"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._config = self._load_config()
    
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return os.path.join(Path.home(), '.lifetrace', 'config.yaml')
    
    def _load_config(self) -> dict:
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """默认配置"""
        return {
            'base_dir': os.path.join(Path.home(), '.lifetrace'),
            'database_path': 'lifetrace.db',
            'screenshots_dir': 'screenshots',
            'server': {
                'host': '127.0.0.1',
                'port': 8840
            },
            'record': {
                'interval': 1,  # 截图间隔（秒）
                'screens': 'all'  # 截图屏幕：all 或屏幕编号列表
            },
            'ocr': {
                'enabled': True,
                'use_gpu': False,
                'language': ['ch', 'en'],
                'check_interval': 5,  # 数据库检查间隔（秒）
                'confidence_threshold': 0.5
            },
            'storage': {
                'max_days': 30,  # 数据保留天数
                'deduplicate': True  # 启用去重
            },
            'processing': {
                'batch_size': 10,
                'queue_size': 100
            },
            'consistency_check': {
                'interval': 300  # 一致性检查间隔（秒）
            },
            'vector_db': {
                'enabled': True,  # 启用向量数据库
                'collection_name': 'lifetrace_ocr',  # 集合名称
                'embedding_model': 'shibing624/text2vec-base-chinese',  # 嵌入模型
                'rerank_model': 'BAAI/bge-reranker-base',  # 重排序模型
                'persist_directory': 'vector_db',  # 持久化目录
                'chunk_size': 512,  # 文本块大小
                'chunk_overlap': 50,  # 文本块重叠
                'batch_size': 32,  # 批处理大小
                'auto_sync': True,  # 自动同步
                'sync_interval': 300  # 同步间隔（秒）
            },
            'sync_service': {
                'enable_file_monitor': True,  # 启用文件监控
                'enable_consistency_check': True,  # 启用一致性检查
                'consistency_check_interval': 300,  # 一致性检查间隔（秒）
                'vector_sync_interval': 600,  # 向量数据库同步间隔（秒）
                'file_monitor_delay': 2.0,  # 文件监控延迟（秒）
                'cleanup_orphaned_files': True,  # 清理孤立文件
                'log_level': 'INFO'  # 日志级别
            }
        }
    
    def save_config(self):
        """保存配置到文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, allow_unicode=True, default_flow_style=False)
    
    def get(self, key: str, default=None):
        """获取配置值"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        """设置配置值"""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    @property
    def base_dir(self) -> str:
        return self.get('base_dir')
    
    @property
    def database_path(self) -> str:
        db_path = self.get('database_path')
        if not os.path.isabs(db_path):
            return os.path.join(self.base_dir, db_path)
        return db_path
    
    @property
    def screenshots_dir(self) -> str:
        return os.path.join(self.base_dir, self.get('screenshots_dir'))
    
    @property
    def vector_db_enabled(self) -> bool:
        return self.get('vector_db.enabled', True)
    
    @property
    def vector_db_collection_name(self) -> str:
        return self.get('vector_db.collection_name', 'lifetrace_ocr')
    
    @property
    def vector_db_embedding_model(self) -> str:
        return self.get('vector_db.embedding_model', 'shibing624/text2vec-base-chinese')
    
    @property
    def vector_db_rerank_model(self) -> str:
        return self.get('vector_db.rerank_model', 'BAAI/bge-reranker-base')
    
    @property
    def vector_db_persist_directory(self) -> str:
        persist_dir = self.get('vector_db.persist_directory', 'vector_db')
        if not os.path.isabs(persist_dir):
            return os.path.join(self.base_dir, persist_dir)
        return persist_dir
    
    @property
    def vector_db_chunk_size(self) -> int:
        return self.get('vector_db.chunk_size', 512)
    
    @property
    def vector_db_chunk_overlap(self) -> int:
        return self.get('vector_db.chunk_overlap', 50)
    
    @property
    def vector_db_batch_size(self) -> int:
        return self.get('vector_db.batch_size', 32)
    
    @property
    def vector_db_auto_sync(self) -> bool:
        return self.get('vector_db.auto_sync', True)
    
    @property
    def vector_db_sync_interval(self) -> int:
        return self.get('vector_db.sync_interval', 300)
    
    # 同步服务配置属性
    @property
    def enable_file_monitor(self) -> bool:
        return self.get('sync_service.enable_file_monitor', True)
    
    @property
    def enable_consistency_check(self) -> bool:
        return self.get('sync_service.enable_consistency_check', True)
    
    @property
    def consistency_check_interval(self) -> int:
        return self.get('sync_service.consistency_check_interval', 300)
    
    @property
    def vector_sync_interval(self) -> int:
        return self.get('sync_service.vector_sync_interval', 600)
    
    @property
    def file_monitor_delay(self) -> float:
        return self.get('sync_service.file_monitor_delay', 2.0)
    
    @property
    def cleanup_orphaned_files(self) -> bool:
        return self.get('sync_service.cleanup_orphaned_files', True)
    
    @property
    def sync_service_log_level(self) -> str:
        return self.get('sync_service.log_level', 'INFO')

# 全局配置实例
config = LifeTraceConfig()