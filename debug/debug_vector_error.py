#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试向量数据库集合错�?重现 "Collection [c34bc427-8f37-4dd4-b0db-81a45da04e8e] does not exists" 错误
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.multimodal_vector_service import MultimodalVectorService
from lifetrace_backend.models import OCRResult, Screenshot

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_all_vector_databases():
    """调试所有向量数据库实例"""
    print("=== 全面向量数据库调�?===")
    
    try:
        # 1. 检查基本向量服�?        print("\n=== 基本向量服务 ===")
        vector_service = create_vector_service(config, db_manager)
        print(f"向量服务可用: {vector_service.is_enabled()}")
        
        if vector_service.is_enabled():
            vector_db = vector_service.vector_db
            print(f"集合名称: {vector_db.collection_name}")
            print(f"集合ID: {vector_db.collection.id}")
            print(f"文档数量: {vector_db.collection.count()}")
            print(f"持久化目�? {vector_db.vector_db_path}")
        
        # 2. 检查多模态向量服�?        print("\n=== 多模态向量服�?===")
        try:
            multimodal_service = MultimodalVectorService(config, db_manager)
            print(f"多模态服务可�? {multimodal_service.is_enabled()}")
            
            if multimodal_service.is_enabled():
                # 检查文本向量数据库
                if multimodal_service.text_vector_db:
                    text_db = multimodal_service.text_vector_db
                    print(f"文本向量数据�?")
                    print(f"  集合名称: {text_db.collection_name}")
                    print(f"  集合ID: {text_db.collection.id}")
                    print(f"  文档数量: {text_db.collection.count()}")
                    print(f"  持久化目�? {text_db.vector_db_path}")
                
                # 检查图像向量数据库
                if multimodal_service.image_vector_db:
                    image_db = multimodal_service.image_vector_db
                    print(f"图像向量数据�?")
                    print(f"  集合名称: {image_db.collection_name}")
                    print(f"  集合ID: {image_db.collection.id}")
                    print(f"  文档数量: {image_db.collection.count()}")
                    print(f"  持久化目�? {image_db.vector_db_path}")
                    
        except Exception as e:
            print(f"多模态向量服务初始化失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. 检查所有ChromaDB持久化目�?        print("\n=== ChromaDB持久化目录检�?===")
        base_dir = os.path.expanduser("~/.lifetrace")
        print(f"基础目录: {base_dir}")
        
        if os.path.exists(base_dir):
            for item in os.listdir(base_dir):
                item_path = os.path.join(base_dir, item)
                if os.path.isdir(item_path) and "vector_db" in item:
                    print(f"发现向量数据库目�? {item}")
                    
                    # 检查目录内�?                    try:
                        import chromadb
                        from chromadb.config import Settings
                        
                        client = chromadb.PersistentClient(
                            path=item_path,
                            settings=Settings(
                                anonymized_telemetry=False,
                                allow_reset=True
                            )
                        )
                        
                        collections = client.list_collections()
                        print(f"  集合数量: {len(collections)}")
                        for collection in collections:
                            print(f"    集合: {collection.name}, ID: {collection.id}, 文档�? {collection.count()}")
                            
                            # 检查是否是问题集合ID
                            if collection.id == "c34bc427-8f37-4dd4-b0db-81a45da04e8e":
                                print(f"    *** 找到问题集合ID! ***")
                                
                                # 尝试访问集合
                                try:
                                    count = collection.count()
                                    print(f"    集合可正常访问，文档�? {count}")
                                except Exception as access_e:
                                    print(f"    集合访问失败: {access_e}")
                        
                    except Exception as e:
                        print(f"  检查目�?{item} 失败: {e}")
        
        # 4. 模拟OCR处理过程
        print("\n=== 模拟OCR处理过程 ===")
        try:
            with db_manager.get_session() as session:
                # 获取最新的OCR结果
                latest_ocr = session.query(OCRResult).order_by(OCRResult.id.desc()).first()
                if latest_ocr:
                    print(f"最新OCR结果ID: {latest_ocr.id}")
                    screenshot = session.query(Screenshot).filter(Screenshot.id == latest_ocr.screenshot_id).first()
                    
                    # 尝试用基本向量服务添�?                    print("尝试用基本向量服务添�?..")
                    try:
                        success = vector_service.add_ocr_result(latest_ocr, screenshot)
                        print(f"基本向量服务添加结果: {success}")
                    except Exception as e:
                        print(f"基本向量服务添加失败: {e}")
                        if "does not exists" in str(e):
                            print("*** 发现集合不存在错�? ***")
                    
                    # 尝试用多模态向量服务添�?                    if multimodal_service.is_enabled():
                        print("尝试用多模态向量服务添�?..")
                        try:
                            success = multimodal_service.add_ocr_result(latest_ocr, screenshot)
                            print(f"多模态向量服务添加结�? {success}")
                        except Exception as e:
                            print(f"多模态向量服务添加失�? {e}")
                            if "does not exists" in str(e):
                                print("*** 发现集合不存在错�? ***")
                
        except Exception as e:
            print(f"模拟OCR处理失败: {e}")
        
        # 5. 检查配置差�?        print("\n=== 配置检�?===")
        print(f"基本配置:")
        print(f"  vector_db_enabled: {config.vector_db_enabled}")
        print(f"  vector_db_collection_name: {config.vector_db_collection_name}")
        print(f"  vector_db_persist_directory: {config.vector_db_persist_directory}")
        print(f"多模态配�?")
        print(f"  multimodal.enabled: {config.get('multimodal.enabled', True)}")
        print(f"  multimodal.text_weight: {config.get('multimodal.text_weight', 0.6)}")
        print(f"  multimodal.image_weight: {config.get('multimodal.image_weight', 0.4)}")
        
    except Exception as e:
        print(f"调试过程出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_all_vector_databases()
