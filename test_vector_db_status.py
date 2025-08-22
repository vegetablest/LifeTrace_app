#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试向量数据库状�?"""

import logging
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.config import config
from lifetrace_backend.vector_db import create_vector_db
from lifetrace_backend.storage import DatabaseManager
from lifetrace_backend.vector_service import create_vector_service

def main():
    # 设置日志
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("=== 向量数据库状态检�?===")
    
    try:
        # 检查配�?        print(f"\n📋 配置信息:")
        print(f"  向量数据库启�? {config.vector_db_enabled}")
        print(f"  集合名称: {config.vector_db_collection_name}")
        print(f"  持久化目�? {config.vector_db_persist_directory}")
        print(f"  嵌入模型: {config.vector_db_embedding_model}")
        
        # 检查向量数据库
        print(f"\n🔍 创建向量数据库实�?..")
        vector_db = create_vector_db(config)
        
        if vector_db is None:
            print("�?向量数据库创建失�?)
            return
        
        print("�?向量数据库创建成�?)
        
        # 检查集合状�?        print(f"\n📊 集合状�?")
        try:
            collection_count = vector_db.collection.count()
            print(f"  文档数量: {collection_count}")
            
            # 获取集合统计信息
            stats = vector_db.get_collection_stats()
            print(f"  统计信息: {stats}")
            
        except Exception as e:
            print(f"�?获取集合信息失败: {e}")
            logger.error(f"Collection error: {e}", exc_info=True)
        
        # 检查向量服�?        print(f"\n🔧 检查向量服�?..")
        db_manager = DatabaseManager()  # 使用默认配置
        vector_service = create_vector_service(config, db_manager)
        
        if vector_service and vector_service.is_enabled():
            print("�?向量服务可用")
            service_stats = vector_service.get_stats()
            print(f"  服务统计: {service_stats}")
        else:
            print("�?向量服务不可�?)
            
    except Exception as e:
        print(f"�?检查过程中出现错误: {e}")
        logger.error(f"Main error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
