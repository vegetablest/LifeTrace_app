#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OCR任务队列日志记录
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.logging_config import setup_logging
from lifetrace_backend.models import Screenshot
import logging
from datetime import datetime

def test_ocr_queue_logging():
    """测试OCR队列日志记录"""
    print("开始测试OCR任务队列日志记录...")
    
    # 设置日志系统
    logger_manager = setup_logging(config)
    logger = logger_manager.get_processor_logger()
    
    # 设置debug级别以查看所有日志
    logger.setLevel(logging.DEBUG)
    
    # 添加控制台处理器以便实时查看
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    print("\n1. 创建测试截图记录...")
    
    # 创建一个测试截图记录
    with db_manager.get_session() as session:
        import time
        test_screenshot = Screenshot(
            file_path=f"/test/screenshot_test_{int(time.time())}.png",
            file_hash="test_hash_123",
            file_size=1024,
            width=1920,
            height=1080,
            window_title="测试窗口",
            app_name="test_process"
        )
        session.add(test_screenshot)
        session.flush()
        screenshot_id = test_screenshot.id
        print(f"创建测试截图记录，ID: {screenshot_id}")
    
    print("\n2. 添加OCR任务到队列...")
    
    # 添加OCR任务
    task_id = db_manager.add_processing_task(screenshot_id, 'ocr')
    if task_id:
        print(f"成功添加OCR任务，任务ID: {task_id}")
        logger.info(f"测试：添加OCR任务到队列，任务ID: {task_id}")
    else:
        print("添加OCR任务失败")
        logger.error("测试：添加OCR任务失败")
    
    print("\n3. 获取队列状态...")
    
    # 获取队列状态
    pending_tasks = db_manager.get_pending_tasks('ocr')
    print(f"当前待处理OCR任务数量: {len(pending_tasks)}")
    logger.info(f"测试：当前待处理OCR任务数量: {len(pending_tasks)}")
    
    for task in pending_tasks:
        print(f"  任务ID: {task.id}, 截图ID: {task.screenshot_id}, 状态: {task.status}")
        logger.debug(f"测试：任务详情 - ID: {task.id}, 截图ID: {task.screenshot_id}, 状态: {task.status}")
    
    print("\n4. 更新任务状态...")
    
    if pending_tasks:
        task = pending_tasks[0]
        # 更新任务状态为processing
        success = db_manager.update_task_status(task.id, 'processing')
        if success:
            print(f"成功更新任务 {task.id} 状态为 processing")
            logger.info(f"测试：更新任务 {task.id} 状态为 processing")
        
        # 再次更新为completed
        success = db_manager.update_task_status(task.id, 'completed')
        if success:
            print(f"成功更新任务 {task.id} 状态为 completed")
            logger.info(f"测试：更新任务 {task.id} 状态为 completed")
    
    print("\n5. 最终队列状态...")
    
    # 获取最终状态
    from lifetrace_backend.models import ProcessingQueue
    with db_manager.get_session() as session:
        pending_count = session.query(ProcessingQueue).filter_by(status='pending').count()
        processing_count = session.query(ProcessingQueue).filter_by(status='processing').count()
        completed_count = session.query(ProcessingQueue).filter_by(status='completed').count()
        failed_count = session.query(ProcessingQueue).filter_by(status='failed').count()
        
        print(f"队列状态统计:")
        print(f"  待处理: {pending_count}")
        print(f"  处理中: {processing_count}")
        print(f"  已完成: {completed_count}")
        print(f"  失败: {failed_count}")
        
        logger.info(f"测试：最终队列状态 - 待处理:{pending_count}, 处理中:{processing_count}, 已完成:{completed_count}, 失败:{failed_count}")
    
    print("\nOCR任务队列日志测试完成！")
    print("请查看日志文件：logs/core/lifetrace_processor.log")

if __name__ == "__main__":
    test_ocr_queue_logging()