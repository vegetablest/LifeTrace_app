#!/usr/bin/env python3
"""
检查数据库状态
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import Screenshot, OCRResult


def check_database_status():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")

    try:
        with db_manager.get_session() as session:
            # 检查截图数量
            screenshot_count = session.query(Screenshot).count()
            print(f"📸 截图总数: {screenshot_count}")

            # 检查OCR结果数量
            ocr_count = session.query(OCRResult).count()
            print(f"📝 OCR结果总数: {ocr_count}")

            # 检查最近的截图
            recent_screenshots = session.query(Screenshot).order_by(Screenshot.created_at.desc()).limit(5).all()
            print(f"\n📋 最近的5个截图:")
            for i, screenshot in enumerate(recent_screenshots, 1):
                print(f"  {i}. ID: {screenshot.id}, 应用: {screenshot.app_name}, 时间: {screenshot.created_at}")
                print(f"     文件: {screenshot.file_path}")
                print(f"     尺寸: {screenshot.width}x{screenshot.height}")

            # 检查最近的OCR结果
            recent_ocr = session.query(OCRResult).order_by(OCRResult.created_at.desc()).limit(5).all()
            print(f"\n📄 最近的5个OCR结果:")
            for i, ocr in enumerate(recent_ocr, 1):
                text_preview = (ocr.text_content or "")[:100]
                print(f"  {i}. ID: {ocr.id}, 截图ID: {ocr.screenshot_id}, 置信度: {ocr.confidence}")
                print(f"     文本预览: {text_preview}...")
                print(f"     语言: {ocr.language}, 时间: {ocr.created_at}")

            return screenshot_count, ocr_count

    except Exception as e:
        print(f"❌ 检查数据库失败: {e}")
        return 0, 0


def check_vector_database():
    """检查向量数据库状态"""
    print("\n🔍 检查向量数据库状态...")

    try:
        from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.config import config

        vector_service = create_vector_service(config, db_manager)

        if vector_service and vector_service.is_enabled():
            stats = vector_service.get_stats()
            print(f"✅ 向量数据库已启用")
            print(f"📊 文档数量: {stats.get('document_count', 0)}")
            print(f"📁 集合名称: {stats.get('collection_name', 'unknown')}")
        else:
            print(f"❌ 向量数据库未启用或不可用")

    except Exception as e:
        print(f"❌ 检查向量数据库失败: {e}")


def check_multimodal_database():
    """检查多模态数据库状态"""
    print("\n🔍 检查多模态数据库状态...")

    try:
        from lifetrace_backend.multimodal_vector_service import create_multimodal_vector_service
from lifetrace_backend.config import config

        multimodal_service = create_multimodal_vector_service(config, db_manager)

        if multimodal_service and multimodal_service.is_enabled():
            stats = multimodal_service.get_stats()
            print(f"✅ 多模态数据库已启用")
            print(f"📊 文本数据库文档数: {stats.get('text_database', {}).get('document_count', 0)}")
            print(f"📊 图像数据库文档数: {stats.get('image_database', {}).get('document_count', 0)}")
            print(f"⚖️ 文本权重: {stats.get('text_weight', 0)}")
            print(f"⚖️ 图像权重: {stats.get('image_weight', 0)}")
        else:
            print(f"❌ 多模态数据库未启用或不可用")

    except Exception as e:
        print(f"❌ 检查多模态数据库失败: {e}")


def main():
    """主函数"""
    print("🚀 LifeTrace 数据库状态检查")
    print("=" * 50)

    # 检查基础数据库
    screenshot_count, ocr_count = check_database_status()

    # 检查向量数据库
    check_vector_database()

    # 检查多模态数据库
    check_multimodal_database()

    # 总结
    print("\n" + "=" * 50)
    print("📊 状态总结:")

    if screenshot_count == 0:
        print("⚠️  数据库中没有截图数据！")
        print("💡 建议:")
        print("  1. 启动截图记录功能")
        print("  2. 手动添加一些测试数据")
        print("  3. 检查截图保存路径和权限")
    elif ocr_count == 0:
        print("⚠️  数据库中没有OCR结果！")
        print("💡 建议:")
        print("  1. 运行OCR处理")
        print("  2. 检查OCR服务状态")
        print("  3. 手动触发OCR处理")
    else:
        print(f"✅ 数据库状态正常: {screenshot_count} 个截图, {ocr_count} 个OCR结果")
        print("💡 如果搜索仍然没有结果，可能是:")
        print("  1. 向量数据库需要同步")
        print("  2. 搜索查询词不匹配")
        print("  3. 搜索API有问题")


if __name__ == '__main__':
    main()
