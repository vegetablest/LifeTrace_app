#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置失败的OCR任务
将所有失败的任务状态重置为pending，以便重新处理
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import ProcessingQueue
from datetime import datetime

def reset_failed_tasks():
    """重置失败的任务状态"""
    try:
        with db_manager.get_session() as session:
            # 查找所有失败的任务
            failed_tasks = session.query(ProcessingQueue).filter_by(status='failed').all()
            
            print(f"找到 {len(failed_tasks)} 个失败的任务")
            
            if not failed_tasks:
                print("没有失败的任务需要重置")
                return
            
            # 重置任务状态
            reset_count = 0
            for task in failed_tasks:
                print(f"重置任务 {task.id} (截图ID: {task.screenshot_id})")
                task.status = 'pending'
                task.error_message = None
                task.retry_count = 0
                task.updated_at = datetime.now()
                reset_count += 1
            
            # 提交更改
            session.commit()
            print(f"\n成功重置 {reset_count} 个任务")
            
            # 验证重置结果
            pending_count = session.query(ProcessingQueue).filter_by(status='pending').count()
            failed_count = session.query(ProcessingQueue).filter_by(status='failed').count()
            
            print(f"\n=== 重置后状态 ===")
            print(f"待处理任务: {pending_count}")
            print(f"失败任务: {failed_count}")
            
    except Exception as e:
        print(f"重置失败任务时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    reset_failed_tasks()