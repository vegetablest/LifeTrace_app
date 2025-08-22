#!/usr/bin/env python3
"""
测试文件监听功能
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.processor import FileProcessor
from lifetrace_backend.storage import db_manager


def test_file_monitoring():
    """测试文件监听功能"""
    print("=== 文件监听测试 ===")
    
    # 检查截图目录
    screenshots_dir = config.screenshots_dir
    print(f"截图目录: {screenshots_dir}")
    
    if not os.path.exists(screenshots_dir):
        print(f"❌ 截图目录不存在: {screenshots_dir}")
        return False
    
    # 创建处理器但不启动
    processor = FileProcessor()
    print(f"✅ 处理器创建成功")
    
    # 检查队列状态
    print(f"队列大小: {processor.file_queue.qsize()}")
    print(f"已处理文件数: {len(processor.processed_files)}")
    
    # 列出最近的截图文件
    screenshot_files = []
    for file_path in Path(screenshots_dir).glob("*.png"):
        if file_path.is_file():
            screenshot_files.append(file_path)
    
    screenshot_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\n最近的5个截图文件:")
    for i, file_path in enumerate(screenshot_files[:5]):
        file_stat = file_path.stat()
        file_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(file_stat.st_mtime))
        print(f"  {i+1}. {file_path.name} ({file_time})")
        
        # 检查是否在数据库中
        try:
            with db_manager.get_session() as session:
                from lifetrace_backend.models import Screenshot
                screenshot = session.query(Screenshot).filter_by(file_path=str(file_path)).first()
                if screenshot:
                    print(f"     ✅ 已在数据库中 (ID: {screenshot.id})")
                else:
                    print(f"     ❌ 不在数据库中")
        except Exception as e:
            print(f"     ❌ 数据库查询失败: {e}")
    
    # 测试手动添加文件到队列
    if screenshot_files:
        test_file = screenshot_files[0]
        print(f"\n测试添加文件到队列: {test_file.name}")
        
        try:
            processor.add_file_to_queue(str(test_file))
            print(f"✅ 文件已添加到队列")
            print(f"队列大小: {processor.file_queue.qsize()}")
        except Exception as e:
            print(f"❌ 添加文件到队列失败: {e}")
    
    return True


def test_database_consistency():
    """测试数据库一致性"""
    print("\n=== 数据库一致性测试 ===")
    
    try:
        with db_manager.get_session() as session:
            from lifetrace_backend.models import Screenshot, OCRResult, ProcessingQueue
            
            # 统计数据
            screenshot_count = session.query(Screenshot).count()
            ocr_count = session.query(OCRResult).count()
            queue_count = session.query(ProcessingQueue).count()
            
            print(f"截图记录: {screenshot_count}")
            print(f"OCR记录: {ocr_count}")
            print(f"处理队列: {queue_count}")
            
            # 查找未处理的截图
            unprocessed = session.query(Screenshot).outerjoin(
                OCRResult, Screenshot.id == OCRResult.screenshot_id
            ).filter(
                OCRResult.id.is_(None)
            ).count()
            
            print(f"未处理截图: {unprocessed}")
            
            if unprocessed > 0:
                print(f"\n未处理的截图详情:")
                unprocessed_screenshots = session.query(Screenshot).outerjoin(
                    OCRResult, Screenshot.id == OCRResult.screenshot_id
                ).filter(
                    OCRResult.id.is_(None)
                ).order_by(Screenshot.created_at.desc()).limit(5).all()
                
                for screenshot in unprocessed_screenshots:
                    print(f"  ID: {screenshot.id}, 文件: {os.path.basename(screenshot.file_path)}, 时间: {screenshot.created_at}")
                    
                    # 检查文件是否存在
                    if os.path.exists(screenshot.file_path):
                        print(f"    ✅ 文件存在")
                    else:
                        print(f"    ❌ 文件不存在")
            
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return False
    
    return True


def main():
    """主函数"""
    print("LifeTrace 文件监听测试工具")
    print("=" * 40)
    
    # 测试文件监听
    if not test_file_monitoring():
        return
    
    # 测试数据库一致性
    if not test_database_consistency():
        return
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    main()