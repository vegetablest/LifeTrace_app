#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多模态向量数据库状态
"""

import logging
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace.config import config
from lifetrace.multimodal_vector_service import MultimodalVectorService
from lifetrace.storage import DatabaseManager

def main():
    # 设置日志
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    print("=== 多模态向量数据库状态检查 ===")
    
    try:
        # 检查配置
        print(f"\n📋 多模态配置信息:")
        print(f"  多模态启用: {config.get('multimodal.enabled', False)}")
        print(f"  文本权重: {config.get('multimodal.text_weight', 0.6)}")
        print(f"  图像权重: {config.get('multimodal.image_weight', 0.4)}")
        print(f"  CLIP模型: {config.get('multimodal.model_name', 'openai/clip-vit-base-patch32')}")
        
        # 创建数据库管理器
        print(f"\n🔧 创建数据库管理器...")
        db_manager = DatabaseManager()
        
        # 创建多模态向量服务
        print(f"\n🔍 创建多模态向量服务...")
        multimodal_service = MultimodalVectorService(config, db_manager)
        
        if not multimodal_service.is_enabled():
            print("❌ 多模态向量服务不可用")
            return
        
        print("✅ 多模态向量服务创建成功")
        
        # 检查文本向量数据库
        print(f"\n📊 文本向量数据库状态:")
        try:
            if multimodal_service.text_vector_db:
                text_count = multimodal_service.text_vector_db.collection.count()
                print(f"  文本集合文档数量: {text_count}")
                text_stats = multimodal_service.text_vector_db.get_collection_stats()
                print(f"  文本集合统计: {text_stats}")
            else:
                print("❌ 文本向量数据库不可用")
        except Exception as e:
            print(f"❌ 文本向量数据库错误: {e}")
            logger.error(f"Text vector DB error: {e}", exc_info=True)
        
        # 检查图像向量数据库
        print(f"\n🖼️ 图像向量数据库状态:")
        try:
            if multimodal_service.image_vector_db:
                image_count = multimodal_service.image_vector_db.collection.count()
                print(f"  图像集合文档数量: {image_count}")
                image_stats = multimodal_service.image_vector_db.get_collection_stats()
                print(f"  图像集合统计: {image_stats}")
            else:
                print("❌ 图像向量数据库不可用")
        except Exception as e:
            print(f"❌ 图像向量数据库错误: {e}")
            logger.error(f"Image vector DB error: {e}", exc_info=True)
        
        # 获取服务统计信息
        print(f"\n📈 多模态服务统计:")
        try:
            service_stats = multimodal_service.get_stats()
            print(f"  服务统计: {service_stats}")
        except Exception as e:
            print(f"❌ 获取服务统计失败: {e}")
            logger.error(f"Service stats error: {e}", exc_info=True)
            
    except Exception as e:
        print(f"❌ 检查过程中出现错误: {e}")
        logger.error(f"Main error: {e}", exc_info=True)

if __name__ == "__main__":
    main()