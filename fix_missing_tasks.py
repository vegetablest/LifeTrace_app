#!/usr/bin/env python3
"""
为未处理的截图创建处理任务
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import Screenshot, OCRResult, ProcessingQueue

def main():
    print("=== 修复缺失的处理任务 ===")
    
    with db_manager.get_session() as session:
        # 查找未处理的截图
        unprocessed = session.query(Screenshot).outerjoin(
            OCRResult, Screenshot.id == OCRResult.screenshot_id
        ).filter(
            OCRResult.id.is_(None)
        ).all()
        
        print(f"发现 {len(unprocessed)} 张未处理的截图")
        
        if not unprocessed:
            print("所有截图都已处理")
            return
        
        # 为每张未处理的截图创建处理任务
        created_tasks = 0
        for screenshot in unprocessed:
            print(f"\n处理截图 ID: {screenshot.id}")
            print(f"文件: {screenshot.file_path}")
            print(f"创建时间: {screenshot.created_at}")
            
            # 检查是否已有处理任务
            existing_task = session.query(ProcessingQueue).filter_by(
                screenshot_id=screenshot.id,
                task_type='ocr'
            ).first()
            
            if existing_task:
                print(f"  ✅ 已有处理任务 (状态: {existing_task.status})")
                continue
            
            # 创建新的处理任务
            try:
                task_id = db_manager.add_processing_task(screenshot.id, 'ocr')
                if task_id:
                    print(f"  ✅ 创建处理任务成功 (任务ID: {task_id})")
                    created_tasks += 1
                else:
                    print(f"  ❌ 创建处理任务失败")
            except Exception as e:
                print(f"  ❌ 创建处理任务异常: {e}")
        
        print(f"\n=== 总结 ===")
        print(f"未处理截图: {len(unprocessed)}")
        print(f"创建任务: {created_tasks}")
        
        # 验证结果
        print(f"\n=== 验证结果 ===")
        total_tasks = session.query(ProcessingQueue).count()
        pending_tasks = session.query(ProcessingQueue).filter_by(status='pending').count()
        print(f"总处理任务: {total_tasks}")
        print(f"待处理任务: {pending_tasks}")

if __name__ == '__main__':
    main()