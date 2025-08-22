#!/usr/bin/env python3
"""
启动OCR服务处理队列中的任务
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import ProcessingQueue, Screenshot, OCRResult
from lifetrace_backend.simple_ocr import SimpleOCRProcessor
from lifetrace_backend.config import config

def process_queue_tasks():
    """处理队列中的OCR任务"""
    print("=== 启动OCR队列处理服务 ===")
    
    # 初始化OCR处理器
    ocr_processor = SimpleOCRProcessor()
    
    if not ocr_processor.is_available():
        print("错误: OCR引擎不可用")
        return
    
    print("OCR引擎初始化成功")
    processed_count = 0
    
    try:
        while True:
            with db_manager.get_session() as session:
                # 获取待处理的OCR任务
                pending_tasks = session.query(ProcessingQueue).filter_by(
                    status='pending',
                    task_type='ocr'
                ).limit(10).all()
                
                if not pending_tasks:
                    print(f"\r当前无待处理任务，已处理: {processed_count} 个任务", end="", flush=True)
                    time.sleep(2)
                    continue
                
                print(f"\n发现 {len(pending_tasks)} 个待处理任务")
                
                for task in pending_tasks:
                    try:
                        # 更新任务状态为处理中
                        task.status = 'processing'
                        task.started_at = datetime.now()
                        session.commit()
                        
                        # 获取对应的截图
                        screenshot = session.query(Screenshot).filter_by(id=task.screenshot_id).first()
                        if not screenshot:
                            print(f"警告: 找不到截图记录 ID: {task.screenshot_id}")
                            task.status = 'failed'
                            task.error_message = '找不到对应的截图记录'
                            task.completed_at = datetime.now()
                            session.commit()
                            continue
                        
                        # 检查文件是否存在
                        if not Path(screenshot.file_path).exists():
                            print(f"警告: 截图文件不存在: {screenshot.file_path}")
                            task.status = 'failed'
                            task.error_message = '截图文件不存在'
                            task.completed_at = datetime.now()
                            session.commit()
                            continue
                        
                        # 检查是否已有OCR结果
                        existing_ocr = session.query(OCRResult).filter_by(screenshot_id=screenshot.id).first()
                        if existing_ocr:
                            print(f"跳过已处理的截图: {screenshot.file_path}")
                            task.status = 'completed'
                            task.completed_at = datetime.now()
                            session.commit()
                            continue
                        
                        print(f"处理截图: {Path(screenshot.file_path).name}")
                        
                        # 处理图像
                        result = ocr_processor.process_image(screenshot.file_path)
                        
                        if result['success']:
                            print(f"  ✅ OCR处理成功，用时: {result['processing_time']:.2f}秒")
                            task.status = 'completed'
                            task.completed_at = datetime.now()
                            processed_count += 1
                        else:
                            print(f"  ❌ OCR处理失败: {result.get('error', '未知错误')}")
                            task.status = 'failed'
                            task.error_message = result.get('error', '未知错误')
                            task.completed_at = datetime.now()
                        
                        session.commit()
                        
                    except Exception as e:
                        print(f"处理任务异常: {e}")
                        try:
                            task.status = 'failed'
                            task.error_message = str(e)
                            task.completed_at = datetime.now()
                            session.commit()
                        except:
                            pass
                
                # 短暂休息
                time.sleep(0.5)
                
    except KeyboardInterrupt:
        print("\n\n收到停止信号，正在退出...")
    except Exception as e:
        print(f"\n服务异常: {e}")
        logging.error(f"OCR队列处理服务异常: {e}")
    finally:
        print(f"\nOCR队列处理服务已停止，共处理 {processed_count} 个任务")

def main():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 检查数据库
    if not Path(config.database_path).exists():
        print(f"错误: 数据库文件不存在: {config.database_path}")
        return
    
    # 启动队列处理
    process_queue_tasks()

if __name__ == '__main__':
    main()