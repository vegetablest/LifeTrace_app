#!/usr/bin/env python3
"""
检查失败的OCR任务详情
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import ProcessingQueue, Screenshot

def main():
    print("=== 检查失败的OCR任务 ===")
    
    with db_manager.get_session() as session:
        # 获取失败的任务
        failed_tasks = session.query(ProcessingQueue).filter_by(
            status='failed',
            task_type='ocr'
        ).all()
        
        print(f"发现 {len(failed_tasks)} 个失败的任务")
        
        if not failed_tasks:
            print("没有失败的任务")
            return
        
        for i, task in enumerate(failed_tasks[:10], 1):  # 只显示前10个
            print(f"\n=== 失败任务 {i} ===")
            print(f"任务ID: {task.id}")
            print(f"截图ID: {task.screenshot_id}")
            print(f"创建时间: {task.created_at}")
            print(f"更新时间: {task.updated_at}")
            print(f"错误信息: {task.error_message}")
            print(f"重试次数: {task.retry_count}")           # 获取对应的截图信息
            screenshot = session.query(Screenshot).filter_by(id=task.screenshot_id).first()
            if screenshot:
                print(f"截图文件: {screenshot.file_path}")
                print(f"文件存在: {Path(screenshot.file_path).exists()}")
            else:
                print("截图记录: 未找到")
        
        # 统计错误类型
        print(f"\n=== 错误统计 ===")
        error_counts = {}
        for task in failed_tasks:
            error = task.error_message or "未知错误"
            error_counts[error] = error_counts.get(error, 0) + 1
        
        for error, count in error_counts.items():
            print(f"{error}: {count} 次")

if __name__ == '__main__':
    main()