#!/usr/bin/env python3
"""
检查OCR服务状态
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.simple_ocr import SimpleOCRProcessor
from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import ProcessingQueue

def main():
    print("=== OCR服务状态检查 ===")
    
    # 检查OCR处理器
    ocr = SimpleOCRProcessor()
    print(f"OCR可用: {ocr.is_available()}")
    
    # 检查是否有运行状态属性
    if hasattr(ocr, 'is_running'):
        print(f"OCR运行状态: {ocr.is_running}")
    else:
        print("OCR运行状态: 未知")
    
    # 检查处理队列
    with db_manager.get_session() as session:
        total_tasks = session.query(ProcessingQueue).count()
        pending_tasks = session.query(ProcessingQueue).filter_by(status='pending').count()
        processing_tasks = session.query(ProcessingQueue).filter_by(status='processing').count()
        completed_tasks = session.query(ProcessingQueue).filter_by(status='completed').count()
        failed_tasks = session.query(ProcessingQueue).filter_by(status='failed').count()
        
        print(f"\n=== 处理队列状态 ===")
        print(f"总任务数: {total_tasks}")
        print(f"待处理: {pending_tasks}")
        print(f"处理中: {processing_tasks}")
        print(f"已完成: {completed_tasks}")
        print(f"失败: {failed_tasks}")
        
        if pending_tasks > 0:
            print(f"\n=== 待处理任务详情 ===")
            pending = session.query(ProcessingQueue).filter_by(status='pending').limit(5).all()
            for task in pending:
                print(f"任务ID: {task.id}, 截图ID: {task.screenshot_id}, 类型: {task.task_type}, 创建时间: {task.created_at}")

if __name__ == '__main__':
    main()