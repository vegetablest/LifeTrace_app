#!/usr/bin/env python3
"""
处理器调试工具
专门用于诊断处理器的工作状态和队列处理问题
"""

import os
import sys
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lifetrace_backend'))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import Screenshot, OCRResult, ProcessingQueue
from lifetrace_backend.config import config

def check_unprocessed_screenshots() -> List[Dict[str, Any]]:
    """检查未处理的截图"""
    try:
        with db_manager.get_session() as session:
            # 查找没有OCR结果的截图
            unprocessed = session.query(Screenshot).outerjoin(
                OCRResult, Screenshot.id == OCRResult.screenshot_id
            ).filter(
                OCRResult.id.is_(None)
            ).order_by(Screenshot.created_at.desc()).limit(20).all()
            
            result = []
            for screenshot in unprocessed:
                file_exists = os.path.exists(screenshot.file_path)
                file_size = 0
                if file_exists:
                    try:
                        file_size = os.path.getsize(screenshot.file_path)
                    except:
                        pass
                
                result.append({
                    'id': screenshot.id,
                    'file_path': screenshot.file_path,
                    'created_at': screenshot.created_at.isoformat(),
                    'file_exists': file_exists,
                    'file_size': file_size,
                    'age_minutes': (datetime.now() - screenshot.created_at).total_seconds() / 60
                })
            
            return result
            
    except Exception as e:
        print(f"检查未处理截图失败: {e}")
        return []

def check_processing_queue_details() -> Dict[str, Any]:
    """检查处理队列详细状态"""
    try:
        with db_manager.get_session() as session:
            # 统计各状态任务
            pending = session.query(ProcessingQueue).filter_by(status='pending').all()
            processing = session.query(ProcessingQueue).filter_by(status='processing').all()
            failed = session.query(ProcessingQueue).filter_by(status='failed').all()
            
            # 检查长时间处理的任务
            cutoff_time = datetime.now() - timedelta(minutes=5)
            stuck_tasks = session.query(ProcessingQueue).filter(
                ProcessingQueue.status == 'processing',
                ProcessingQueue.updated_at < cutoff_time
            ).all()
            
            return {
                'pending_count': len(pending),
                'processing_count': len(processing),
                'failed_count': len(failed),
                'stuck_count': len(stuck_tasks),
                'pending_details': [{
                    'id': task.id,
                    'screenshot_id': task.screenshot_id,
                    'created_at': task.created_at.isoformat(),
                    'age_minutes': (datetime.now() - task.created_at).total_seconds() / 60
                } for task in pending[:10]],
                'processing_details': [{
                    'id': task.id,
                    'screenshot_id': task.screenshot_id,
                    'created_at': task.created_at.isoformat(),
                    'updated_at': task.updated_at.isoformat(),
                    'processing_minutes': (datetime.now() - task.updated_at).total_seconds() / 60
                } for task in processing],
                'stuck_details': [{
                    'id': task.id,
                    'screenshot_id': task.screenshot_id,
                    'stuck_minutes': (datetime.now() - task.updated_at).total_seconds() / 60
                } for task in stuck_tasks]
            }
            
    except Exception as e:
        print(f"检查处理队列失败: {e}")
        return {}

def check_file_monitor_status() -> Dict[str, Any]:
    """检查文件监控状态"""
    try:
        screenshot_dir = config.get('record.output_dir', 'screenshots')
        if not os.path.isabs(screenshot_dir):
            screenshot_dir = os.path.join(os.path.expanduser('~'), '.lifetrace', screenshot_dir)
        
        if not os.path.exists(screenshot_dir):
            return {'error': 'Screenshot directory not found'}
        
        # 检查最近的文件
        files = []
        for f in os.listdir(screenshot_dir):
            file_path = os.path.join(screenshot_dir, f)
            if os.path.isfile(file_path) and f.endswith('.png'):
                mtime = os.path.getmtime(file_path)
                files.append({
                    'name': f,
                    'path': file_path,
                    'mtime': datetime.fromtimestamp(mtime),
                    'size': os.path.getsize(file_path)
                })
        
        # 按修改时间排序
        files.sort(key=lambda x: x['mtime'], reverse=True)
        
        # 检查最近5分钟的文件
        recent_cutoff = datetime.now() - timedelta(minutes=5)
        recent_files = [f for f in files if f['mtime'] > recent_cutoff]
        
        return {
            'total_files': len(files),
            'recent_files_count': len(recent_files),
            'latest_file': files[0] if files else None,
            'recent_files': [{
                'name': f['name'],
                'mtime': f['mtime'].isoformat(),
                'size': f['size']
            } for f in recent_files[:10]]
        }
        
    except Exception as e:
        return {'error': str(e)}

def test_manual_processing():
    """测试手动处理一张未处理的截图"""
    print("\n=== 测试手动处理 ===")
    
    unprocessed = check_unprocessed_screenshots()
    if not unprocessed:
        print("没有找到未处理的截图")
        return
    
    # 选择最新的一张未处理截图
    target = unprocessed[0]
    print(f"尝试处理截图 ID: {target['id']}, 文件: {target['file_path']}")
    
    if not target['file_exists']:
        print("文件不存在，跳过处理")
        return
    
    try:
        # 导入处理器相关模块
        from lifetrace_backend.simple_ocr import SimpleOCRProcessor
        
        # 创建OCR实例
        ocr = SimpleOCRProcessor()
        
        # 处理截图
        print("开始OCR处理...")
        start_time = time.time()
        
        result = ocr.process_image(target['file_path'])
        
        processing_time = time.time() - start_time
        print(f"OCR处理完成，耗时: {processing_time:.2f}秒")
        
        if result and result.get('text'):
            print(f"识别到文本: {result['text'][:100]}...")
            print(f"置信度: {result.get('confidence', 0):.2f}")
            
            # 尝试保存到数据库
            with db_manager.get_session() as session:
                ocr_result = OCRResult(
                    screenshot_id=target['id'],
                    text_content=result['text'],
                    confidence=result.get('confidence', 0.0),
                    processing_time=processing_time
                )
                session.add(ocr_result)
                session.commit()
                print("✅ 成功保存OCR结果到数据库")
        else:
            print("❌ OCR处理失败或未识别到文本")
            
    except Exception as e:
        print(f"❌ 手动处理失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("=== 处理器调试报告 ===")
    print(f"时间: {datetime.now()}")
    print()
    
    # 检查未处理的截图
    print("=== 未处理的截图 ===")
    unprocessed = check_unprocessed_screenshots()
    if unprocessed:
        print(f"发现 {len(unprocessed)} 张未处理的截图:")
        for item in unprocessed[:10]:
            print(f"  ID: {item['id']}, 年龄: {item['age_minutes']:.1f}分钟, "
                  f"文件存在: {item['file_exists']}, 大小: {item['file_size']} bytes")
            print(f"    文件: {item['file_path']}")
    else:
        print("✅ 所有截图都已处理")
    print()
    
    # 检查处理队列
    print("=== 处理队列状态 ===")
    queue_status = check_processing_queue_details()
    if queue_status:
        print(f"待处理: {queue_status['pending_count']}")
        print(f"处理中: {queue_status['processing_count']}")
        print(f"失败: {queue_status['failed_count']}")
        print(f"卡住的任务: {queue_status['stuck_count']}")
        
        if queue_status['stuck_details']:
            print("卡住的任务详情:")
            for task in queue_status['stuck_details']:
                print(f"  任务 {task['id']}: 卡住 {task['stuck_minutes']:.1f} 分钟")
    print()
    
    # 检查文件监控
    print("=== 文件监控状态 ===")
    file_status = check_file_monitor_status()
    if 'error' not in file_status:
        print(f"总文件数: {file_status['total_files']}")
        print(f"最近5分钟文件: {file_status['recent_files_count']}")
        if file_status['latest_file']:
            latest = file_status['latest_file']
            print(f"最新文件: {latest['name']} ({latest['mtime'].isoformat()})")
    else:
        print(f"❌ 文件监控检查失败: {file_status['error']}")
    print()
    
    # 如果有未处理的截图，询问是否进行手动测试
    if unprocessed:
        response = input("发现未处理的截图，是否进行手动处理测试？(y/N): ")
        if response.lower() == 'y':
            test_manual_processing()

if __name__ == '__main__':
    main()