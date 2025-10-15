#!/usr/bin/env python3
"""
同步多模态数据库
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.multimodal_vector_service import create_multimodal_vector_service
from lifetrace_backend.models import OCRResult, Screenshot


def sync_multimodal_database():
    """同步多模态数据库"""
    print("🚀 开始同步多模态数据库...")

    try:
        # 创建多模态向量服�?        service = create_multimodal_vector_service(config, db_manager)

        if not service.is_enabled():
            print("�?多模态向量服务未启用")
            return False

        print("�?多模态向量服务已启用")

        # 获取所有OCR结果和对应的截图
        with db_manager.get_session() as session:
            ocr_results = session.query(OCRResult).all()
            print(f"📋 找到 {len(ocr_results)} 个OCR结果")

            success_count = 0
            fail_count = 0

            for ocr in ocr_results:
                try:
                    # 获取对应的截�?                    screenshot = session.query(Screenshot).filter_by(id=ocr.screenshot_id).first()

                    if screenshot:
                        # 检查截图文件是否存�?                        if not os.path.exists(screenshot.file_path):
                            print(f"⚠️  截图文件不存�? {screenshot.file_path}")
                            fail_count += 1
                            continue

                        # 添加到多模态数据库
                        result = service.add_multimodal_result(ocr, screenshot)

                        if result:
                            print(f"�?同步OCR {ocr.id} (截图 {screenshot.id}): 成功")
                            success_count += 1
                        else:
                            print(f"�?同步OCR {ocr.id} (截图 {screenshot.id}): 失败")
                            fail_count += 1
                    else:
                        print(f"⚠️  找不到OCR {ocr.id} 对应的截�?)
                        fail_count += 1

                except Exception as e:
                    print(f"�?同步OCR {ocr.id} 时出�? {e}")
                    fail_count += 1

            print(f"\n📊 同步结果: {success_count} 成功, {fail_count} 失败")

            # 检查同步后的状�?            stats = service.get_stats()
            print(f"\n📈 同步后状�?")
            print(f"  - 文本数据库文档数: {stats.get('text_database', {}).get('document_count', 0)}")
            print(f"  - 图像数据库文档数: {stats.get('image_database', {}).get('document_count', 0)}")

            return success_count > 0

    except Exception as e:
        print(f"�?同步多模态数据库失败: {e}")
        return False


def test_multimodal_search():
    """测试多模态搜�?""
    print("\n🔍 测试多模态搜�?..")

    try:
        service = create_multimodal_vector_service(config, db_manager)

        if not service.is_enabled():
            print("�?多模态向量服务未启用")
            return False

        # 测试搜索
        test_queries = ["连接", "页面", "视频", "灵笼"]

        for query in test_queries:
            try:
                results = service.multimodal_search(query, top_k=3)
                print(f"🔍 查询 '{query}': 找到 {len(results)} 个结�?)

                for i, result in enumerate(results[:2], 1):
                    text_preview = result.get('text', '')[:50]
                    score = result.get('combined_score', 0)
                    print(f"  {i}. 得分: {score:.4f}, 文本: {text_preview}...")

            except Exception as e:
                print(f"�?查询 '{query}' 失败: {e}")

        return True

    except Exception as e:
        print(f"�?测试多模态搜索失�? {e}")
        return False


def main():
    """主函�?""
    print("🚀 LifeTrace 多模态数据库同步")
    print("=" * 50)

    # 同步数据�?    sync_success = sync_multimodal_database()

    if sync_success:
        # 测试搜索
        test_multimodal_search()

        print("\n�?多模态数据库同步完成�?)
        print("💡 现在可以尝试使用多模态搜索功能了�?)
    else:
        print("\n�?多模态数据库同步失败�?)
        print("💡 请检�?")
        print("  1. 截图文件是否存在")
        print("  2. 多模态依赖是否正确安�?)
        print("  3. 向量数据库是否正常工�?)


if __name__ == '__main__':
    main()
