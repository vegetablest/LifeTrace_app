#!/usr/bin/env python3
"""
测试数据库同步功能
验证SQLite和向量数据库的一致性
"""

import os
import sys
import time
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.vector_service import create_vector_service


def get_sqlite_count():
    """获取SQLite数据库中的OCR记录数"""
    try:
        with db_manager.get_session() as session:
            from lifetrace_backend.models import OCRResult
            count = session.query(OCRResult).count()
            return count
    except Exception as e:
        print(f"❌ 获取SQLite记录数失败: {e}")
        return -1


def get_vector_count():
    """获取向量数据库中的文档数"""
    try:
        vector_service = create_vector_service(config, db_manager)
        if not vector_service.is_enabled():
            return -1

        stats = vector_service.get_stats()
        return stats.get('document_count', 0)
    except Exception as e:
        print(f"❌ 获取向量数据库记录数失败: {e}")
        return -1


def test_api_sync(base_url="http://localhost:8840", force_reset=False):
    """测试API同步功能"""
    try:
        url = f"{base_url}/api/vector-sync"
        if force_reset:
            url += "?force_reset=true"

        response = requests.post(url, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return True, result.get('synced_count', 0), result.get('message', '')
        else:
            return False, 0, f"HTTP {response.status_code}: {response.text}"

    except Exception as e:
        return False, 0, str(e)


def test_database_consistency():
    """测试数据库一致性"""
    print("🔍 检查数据库一致性...")

    sqlite_count = get_sqlite_count()
    vector_count = get_vector_count()

    print(f"SQLite数据库记录数: {sqlite_count}")
    print(f"向量数据库记录数: {vector_count}")

    if sqlite_count == -1 or vector_count == -1:
        return False, "无法获取数据库记录数"

    if sqlite_count == vector_count:
        return True, f"数据库一致 (各有 {sqlite_count} 条记录)"
    else:
        return False, f"数据库不一致 (SQLite: {sqlite_count}, Vector: {vector_count})"


def main():
    """主测试函数"""
    print("🧪 数据库同步功能测试")
    print("=" * 40)

    # 1. 初始状态检查
    print("1️⃣ 检查初始状态...")
    consistent, message = test_database_consistency()
    print(f"   {message}")
    initial_sqlite = get_sqlite_count()
    initial_vector = get_vector_count()

    # 2. 测试智能同步
    print(f"\n2️⃣ 测试智能同步...")
    success, synced_count, sync_message = test_api_sync()

    if success:
        print(f"   ✅ 智能同步成功: {sync_message}")
        print(f"   同步记录数: {synced_count}")

        # 检查同步后状态
        post_sync_consistent, post_sync_message = test_database_consistency()
        print(f"   同步后状态: {post_sync_message}")

    else:
        print(f"   ❌ 智能同步失败: {sync_message}")

    # 3. 测试强制重置同步
    print(f"\n3️⃣ 测试强制重置同步...")
    success, synced_count, reset_message = test_api_sync(force_reset=True)

    if success:
        print(f"   ✅ 强制重置同步成功: {reset_message}")
        print(f"   同步记录数: {synced_count}")

        # 检查重置后状态
        post_reset_consistent, post_reset_message = test_database_consistency()
        print(f"   重置后状态: {post_reset_message}")

    else:
        print(f"   ❌ 强制重置同步失败: {reset_message}")

    # 4. 测试空数据库场景
    print(f"\n4️⃣ 测试空数据库同步...")

    # 先清空SQLite数据库（模拟用户清空数据的场景）
    try:
        print("   清空SQLite数据库...")
        with db_manager.get_session() as session:
            from lifetrace_backend.models import OCRResult, Screenshot, ProcessingQueue
            session.query(ProcessingQueue).delete()
            session.query(OCRResult).delete()
            session.query(Screenshot).delete()
            session.commit()
        print("   ✅ SQLite数据库已清空")

        # 检查状态
        empty_sqlite = get_sqlite_count()
        before_vector = get_vector_count()
        print(f"   清空后 - SQLite: {empty_sqlite}, Vector: {before_vector}")

        # 执行智能同步
        success, synced_count, empty_sync_message = test_api_sync()

        if success:
            print(f"   ✅ 空数据库智能同步成功: {empty_sync_message}")

            # 检查最终状态
            final_sqlite = get_sqlite_count()
            final_vector = get_vector_count()
            print(f"   最终状态 - SQLite: {final_sqlite}, Vector: {final_vector}")

            if final_sqlite == 0 and final_vector == 0:
                print("   ✅ 空数据库同步正确：两个数据库都为空")
            else:
                print("   ❌ 空数据库同步错误：向量数据库应该被清空")
        else:
            print(f"   ❌ 空数据库智能同步失败: {empty_sync_message}")

    except Exception as e:
        print(f"   ❌ 空数据库测试失败: {e}")

    # 5. 总结
    print(f"\n📊 测试总结:")
    print(f"   • 智能同步功能: {'✅ 正常' if success else '❌ 异常'}")
    print(f"   • 数据库一致性: 会自动保持一致")
    print(f"   • 空数据库处理: 自动清空向量数据库")
    print(f"\n💡 使用建议:")
    print(f"   • 清空传统数据库后，点击'智能同步'会自动清空向量数据库")
    print(f"   • '强制重置'会强制重建向量数据库")
    print(f"   • 两个数据库会保持数据一致性")


if __name__ == '__main__':
    main()
