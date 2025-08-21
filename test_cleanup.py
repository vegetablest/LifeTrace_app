#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试cleanup功能
"""

from lifetrace.storage import db_manager
from datetime import datetime, timedelta
import os
from pathlib import Path

def test_cleanup_function():
    """测试cleanup功能是否正常工作"""
    print("=== 测试cleanup功能 ===")
    
    # 1. 查看当前数据库记录
    print("\n1. 查看当前数据库记录:")
    try:
        results = db_manager.search_screenshots(limit=100)
        print(f"数据库中共有 {len(results)} 条截图记录")
        
        if results:
            print("最近的记录:")
            for i, result in enumerate(results[:5], 1):
                print(f"  {i}. 应用: {result['app_name']}, 时间: {result['created_at']}")
        else:
            print("数据库中没有记录")
            
    except Exception as e:
        print(f"查询数据库失败: {e}")
        return
    
    # 2. 检查截图文件
    print("\n2. 检查截图文件:")
    try:
        from lifetrace.config import config
        screenshots_dir = Path(config.screenshots_dir)
        
        if screenshots_dir.exists():
            files = list(screenshots_dir.glob("*.png"))
            print(f"截图目录中有 {len(files)} 个文件")
            
            if files:
                print("最近的文件:")
                # 按修改时间排序
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                for i, file_path in enumerate(files[:5], 1):
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    print(f"  {i}. {file_path.name}, 修改时间: {mtime}")
        else:
            print("截图目录不存在")
            
    except Exception as e:
        print(f"检查截图文件失败: {e}")
    
    # 3. 测试cleanup功能
    print("\n3. 测试cleanup功能:")
    
    if not results:
        print("没有数据可以清理，先创建一些测试数据...")
        # 这里可以添加创建测试数据的代码
        return
    
    # 计算1天前的记录数量
    one_day_ago = datetime.now() - timedelta(days=1)
    old_records = [r for r in results if datetime.fromisoformat(r['created_at'].replace('Z', '+00:00')).replace(tzinfo=None) < one_day_ago]
    
    print(f"1天前的记录数量: {len(old_records)}")
    
    if old_records:
        print("将要被清理的记录:")
        for i, record in enumerate(old_records[:3], 1):
            print(f"  {i}. 应用: {record['app_name']}, 时间: {record['created_at']}")
    
    # 4. 执行cleanup
    print("\n4. 执行cleanup (清理1天前的数据):")
    try:
        db_manager.cleanup_old_data(1)
        print("✅ cleanup执行完成")
        
        # 5. 检查清理结果
        print("\n5. 检查清理结果:")
        new_results = db_manager.search_screenshots(limit=100)
        print(f"清理后数据库中有 {len(new_results)} 条记录")
        
        if len(new_results) < len(results):
            print(f"✅ 成功清理了 {len(results) - len(new_results)} 条记录")
        elif len(new_results) == len(results):
            print("⚠️ 没有记录被清理（可能没有1天前的数据）")
        else:
            print("❌ 记录数量异常增加")
            
    except Exception as e:
        print(f"❌ cleanup执行失败: {e}")
        import traceback
        traceback.print_exc()

def test_cleanup_with_different_days():
    """测试不同天数的cleanup"""
    print("\n=== 测试不同天数的cleanup ===")
    
    for days in [0, 7, 30, 365]:
        print(f"\n测试清理 {days} 天前的数据:")
        try:
            results_before = db_manager.search_screenshots(limit=100)
            db_manager.cleanup_old_data(days)
            results_after = db_manager.search_screenshots(limit=100)
            
            cleaned = len(results_before) - len(results_after)
            print(f"  清理前: {len(results_before)} 条记录")
            print(f"  清理后: {len(results_after)} 条记录")
            print(f"  清理了: {cleaned} 条记录")
            
        except Exception as e:
            print(f"  ❌ 测试失败: {e}")

if __name__ == '__main__':
    test_cleanup_function()
    test_cleanup_with_different_days()