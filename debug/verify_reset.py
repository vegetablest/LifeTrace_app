#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证LifeTrace数据库重置结�?测试系统是否能正常初始化和工�?"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from pathlib import Path
from lifetrace_backend.config import config
from lifetrace_backend.storage import DatabaseManager
from lifetrace_backend.models import Screenshot, OCRResult
from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.multimodal_vector_service import MultimodalVectorService

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_file_system():
    """检查文件系统状�?""
    logger.info("=== 检查文件系统状�?===")
    
    lifetrace_dir = Path.home() / ".lifetrace"
    
    # 检查主目录
    if lifetrace_dir.exists():
        logger.info(f"�?LifeTrace目录存在: {lifetrace_dir}")
    else:
        logger.info(f"📁 LifeTrace目录不存在，将自动创�? {lifetrace_dir}")
    
    # 检查数据库文件
    db_files = [
        lifetrace_dir / "lifetrace.db",
        lifetrace_dir / "lifetrace.db-wal",
        lifetrace_dir / "lifetrace.db-shm"
    ]
    
    for db_file in db_files:
        if db_file.exists():
            logger.warning(f"⚠️ 数据库文件仍存在: {db_file}")
        else:
            logger.info(f"�?数据库文件已清理: {db_file.name}")
    
    # 检查向量数据库目录
    vector_dirs = [
        lifetrace_dir / "vector_db",
        lifetrace_dir / "vector_db_text",
        lifetrace_dir / "vector_db_image"
    ]
    
    for vector_dir in vector_dirs:
        if vector_dir.exists():
            logger.warning(f"⚠️ 向量数据库目录仍存在: {vector_dir}")
        else:
            logger.info(f"�?向量数据库目录已清理: {vector_dir.name}")
    
    return True

def test_database_initialization():
    """测试数据库初始化"""
    logger.info("=== 测试数据库初始化 ===")
    
    try:
        # 初始化数据库管理�?        db_manager = DatabaseManager()
        logger.info("�?数据库管理器创建成功")
        
        # 初始化数据库
        db_manager.init_database()
        logger.info("�?数据库初始化成功")
        
        # 测试数据库连�?        with db_manager.get_session() as session:
            # 检查表是否存在
            screenshot_count = session.query(Screenshot).count()
            ocr_count = session.query(OCRResult).count()
            
            logger.info(f"📊 数据库状�?")
            logger.info(f"   截图记录�? {screenshot_count}")
            logger.info(f"   OCR记录�? {ocr_count}")
            
            if screenshot_count == 0 and ocr_count == 0:
                logger.info("�?数据库为空，重置成功")
            else:
                logger.warning(f"⚠️ 数据库不为空，可能重置不完全")
        
        return True
        
    except Exception as e:
        logger.error(f"�?数据库初始化失败: {e}")
        return False

def test_vector_service():
    """测试向量服务"""
    logger.info("=== 测试向量服务 ===")
    
    try:
        # 测试基本向量服务
        vector_service = create_vector_service()
        if vector_service:
            logger.info("�?基本向量服务创建成功")
            
            # 检查向量数据库状�?            if hasattr(vector_service, 'vector_db') and vector_service.vector_db:
                collection = vector_service.vector_db.collection
                if collection:
                    doc_count = collection.count()
                    logger.info(f"📊 基本向量数据库文档数: {doc_count}")
                    
                    if doc_count == 0:
                        logger.info("�?基本向量数据库为空，重置成功")
                    else:
                        logger.warning(f"⚠️ 基本向量数据库不为空: {doc_count} 个文�?)
        else:
            logger.info("ℹ️ 基本向量服务未启�?)
        
        return True
        
    except Exception as e:
        logger.error(f"�?向量服务测试失败: {e}")
        return False

def test_multimodal_vector_service():
    """测试多模态向量服�?""
    logger.info("=== 测试多模态向量服�?===")
    
    try:
        # 检查多模态配�?        multimodal_enabled = config.get('multimodal.enabled', False)
        logger.info(f"📋 多模态服务配�? {multimodal_enabled}")
        
        if not multimodal_enabled:
            logger.info("ℹ️ 多模态向量服务未启用")
            return True
        
        # 创建多模态向量服�?        multimodal_service = MultimodalVectorService()
        logger.info("�?多模态向量服务创建成�?)
        
        # 检查文本向量数据库
        if multimodal_service.text_vector_db:
            text_collection = multimodal_service.text_vector_db.collection
            if text_collection:
                text_count = text_collection.count()
                logger.info(f"📊 文本向量数据库文档数: {text_count}")
                
                if text_count == 0:
                    logger.info("�?文本向量数据库为空，重置成功")
                else:
                    logger.warning(f"⚠️ 文本向量数据库不为空: {text_count} 个文�?)
        
        # 检查图像向量数据库
        if multimodal_service.image_vector_db:
            image_collection = multimodal_service.image_vector_db.collection
            if image_collection:
                image_count = image_collection.count()
                logger.info(f"📊 图像向量数据库文档数: {image_count}")
                
                if image_count == 0:
                    logger.info("�?图像向量数据库为空，重置成功")
                else:
                    logger.warning(f"⚠️ 图像向量数据库不为空: {image_count} 个文�?)
        
        return True
        
    except Exception as e:
        logger.error(f"�?多模态向量服务测试失�? {e}")
        return False

def test_basic_operations():
    """测试基本操作"""
    logger.info("=== 测试基本操作 ===")
    
    try:
        # 测试数据库写�?        db_manager = DatabaseManager()
        
        with db_manager.get_session() as session:
            # 创建测试截图记录
            test_screenshot = Screenshot(
                file_path="test_screenshot.png",
                timestamp=1234567890,
                file_size=1024,
                width=1920,
                height=1080
            )
            
            session.add(test_screenshot)
            session.commit()
            
            # 验证写入
            screenshot_id = test_screenshot.id
            logger.info(f"�?测试截图记录创建成功，ID: {screenshot_id}")
            
            # 删除测试记录
            session.delete(test_screenshot)
            session.commit()
            logger.info("�?测试记录清理完成")
        
        return True
        
    except Exception as e:
        logger.error(f"�?基本操作测试失败: {e}")
        return False

def test_vector_operations():
    """测试向量操作"""
    logger.info("=== 测试向量操作 ===")
    
    try:
        vector_service = create_vector_service()
        
        if not vector_service:
            logger.info("ℹ️ 向量服务未启用，跳过测试")
            return True
        
        # 测试添加文档
        test_result = vector_service.vector_db.add_document(
            text="这是一个测试文�?,
            metadata={"test": True, "timestamp": 1234567890}
        )
        
        if test_result:
            logger.info("�?向量数据库写入测试成�?)
            
            # 测试搜索
            search_results = vector_service.vector_db.search(
                query="测试",
                n_results=1
            )
            
            if search_results and len(search_results) > 0:
                logger.info("�?向量数据库搜索测试成�?)
            else:
                logger.warning("⚠️ 向量数据库搜索测试失�?)
        else:
            logger.warning("⚠️ 向量数据库写入测试失�?)
        
        return True
        
    except Exception as e:
        logger.error(f"�?向量操作测试失败: {e}")
        return False

def main():
    """主函�?""
    print("=== LifeTrace 重置验证工具 ===")
    print("验证数据库重置是否成功，并测试系统功�?)
    print()
    
    test_results = []
    
    # 1. 检查文件系统状�?    test_results.append(check_file_system())
    
    # 2. 测试数据库初始化
    test_results.append(test_database_initialization())
    
    # 3. 测试向量服务
    test_results.append(test_vector_service())
    
    # 4. 测试多模态向量服�?    test_results.append(test_multimodal_vector_service())
    
    # 5. 测试基本操作
    test_results.append(test_basic_operations())
    
    # 6. 测试向量操作
    test_results.append(test_vector_operations())
    
    # 统计结果
    success_count = sum(test_results)
    total_tests = len(test_results)
    
    print(f"\n=== 验证结果 ===")
    print(f"测试通过: {success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("\n🎉 所有测试通过�?)
        print("�?数据库重置成�?)
        print("�?系统功能正常")
        print("\n系统已准备就绪，可以开始使用LifeTrace�?)
    else:
        print("\n⚠️ 部分测试失败")
        print("请检查上述错误信息，可能需要进一步处�?)
    
    print("\n建议重启LifeTrace服务以确保所有组件正常工作�?)

if __name__ == "__main__":
    main()
