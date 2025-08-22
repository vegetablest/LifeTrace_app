#!/usr/bin/env python3

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import ProcessingQueue, Screenshot, OCRResult

def main():
    print("=== 处理队列检查 ===")
    
    with db_manager.get_session() as session:
        # 检查处理队列
        tasks = session.query(ProcessingQueue).all()
        print(f"处理队列任务数: {len(tasks)}")
        
        if tasks:
            print("\n处理队列详情:")
            for task in tasks[:10]:
                print(f"  任务ID: {task.id}, 截图ID: {task.screenshot_id}, 类型: {task.task_type}, 状态: {task.status}")
                print(f"    创建时间: {task.created_at}, 更新时间: {task.updated_at}")
        
        # 检查未处理的截图
        unprocessed = session.query(Screenshot).outerjoin(
            OCRResult, Screenshot.id == OCRResult.screenshot_id
        ).filter(
            OCRResult.id.is_(None)
        ).all()
        
        print(f"\n未处理截图数: {len(unprocessed)}")
        
        if unprocessed:
            print("\n未处理截图详情:")
            for screenshot in unprocessed[:5]:
                print(f"  截图ID: {screenshot.id}, 文件: {screenshot.file_path}")
                print(f"    创建时间: {screenshot.created_at}")
                
                # 检查是否有对应的处理任务
                task = session.query(ProcessingQueue).filter_by(
                    screenshot_id=screenshot.id,
                    task_type='ocr'
                ).first()
                
                if task:
                    print(f"    ✅ 有处理任务 (状态: {task.status})")
                else:
                    print(f"    ❌ 没有处理任务")
        
        # 统计各种状态的任务
        print("\n=== 任务状态统计 ===")
        statuses = ['pending', 'processing', 'completed', 'failed']
        for status in statuses:
            count = session.query(ProcessingQueue).filter_by(status=status).count()
            print(f"{status}: {count}")

if __name__ == '__main__':
    main()