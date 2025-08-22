#!/usr/bin/env python3
"""
综合诊断工具
用于分析 LifeTrace 服务可能出现的问题
"""

import os
import sys
import time
import psutil
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import gc

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lifetrace_backend'))

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager

class SystemDiagnostic:
    """系统诊断类"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.baseline_memory = None
        self.baseline_handles = None
        self.db_path = config.database_path
        
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存使用信息"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available / 1024 / 1024,  # MB
            'gc_objects': len(gc.get_objects())
        }
    
    def get_file_handles(self) -> Dict[str, Any]:
        """获取文件句柄信息"""
        try:
            process = psutil.Process()
            open_files = process.open_files()
            
            file_types = {}
            for file_info in open_files:
                ext = os.path.splitext(file_info.path)[1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
            
            return {
                'total_handles': len(open_files),
                'file_types': file_types,
                'db_handles': sum(1 for f in open_files if '.db' in f.path.lower())
            }
        except Exception as e:
            return {'error': str(e)}
    
    def check_database_status(self) -> Dict[str, Any]:
        """检查数据库状态"""
        try:
            # 检查数据库文件
            if not os.path.exists(self.db_path):
                return {'error': 'Database file not found'}
            
            db_size = os.path.getsize(self.db_path) / 1024 / 1024  # MB
            
            # 检查数据库连接
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # 检查表状态
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # 检查数据量
            table_counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
                except Exception as e:
                    table_counts[table] = f"Error: {e}"
            
            # 检查数据库锁定状态
            cursor.execute("PRAGMA database_list")
            db_info = cursor.fetchall()
            
            # 检查WAL模式
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'size_mb': db_size,
                'tables': tables,
                'table_counts': table_counts,
                'journal_mode': journal_mode,
                'db_info': db_info
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def check_processing_queue(self) -> Dict[str, Any]:
        """检查处理队列状态"""
        try:
            with db_manager.get_session() as session:
                from lifetrace_backend.models import ProcessingQueue
                
                # 统计各状态的任务数量
                pending = session.query(ProcessingQueue).filter_by(status='pending').count()
                processing = session.query(ProcessingQueue).filter_by(status='processing').count()
                completed = session.query(ProcessingQueue).filter_by(status='completed').count()
                failed = session.query(ProcessingQueue).filter_by(status='failed').count()
                
                # 检查长时间处理的任务
                cutoff_time = datetime.now() - timedelta(minutes=10)
                stuck_tasks = session.query(ProcessingQueue).filter(
                    ProcessingQueue.status == 'processing',
                    ProcessingQueue.updated_at < cutoff_time
                ).count()
                
                return {
                    'pending': pending,
                    'processing': processing,
                    'completed': completed,
                    'failed': failed,
                    'stuck_tasks': stuck_tasks,
                    'total': pending + processing + completed + failed
                }
                
        except Exception as e:
            return {'error': str(e)}
    
    def check_screenshot_files(self) -> Dict[str, Any]:
        """检查截图文件状态"""
        try:
            screenshot_dir = config.get('record.output_dir', 'screenshots')
            if not os.path.isabs(screenshot_dir):
                screenshot_dir = os.path.join(os.path.expanduser('~'), '.lifetrace', screenshot_dir)
            
            if not os.path.exists(screenshot_dir):
                return {'error': 'Screenshot directory not found'}
            
            files = os.listdir(screenshot_dir)
            total_files = len(files)
            total_size = sum(os.path.getsize(os.path.join(screenshot_dir, f)) 
                           for f in files if os.path.isfile(os.path.join(screenshot_dir, f)))
            
            # 按日期分组
            today = datetime.now().date()
            today_files = 0
            for f in files:
                file_path = os.path.join(screenshot_dir, f)
                if os.path.isfile(file_path):
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
                    if mtime == today:
                        today_files += 1
            
            return {
                'total_files': total_files,
                'total_size_mb': total_size / 1024 / 1024,
                'today_files': today_files,
                'directory': screenshot_dir
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """运行综合检查"""
        print("开始综合诊断...")
        
        # 设置基线
        if self.baseline_memory is None:
            self.baseline_memory = self.get_memory_info()
            self.baseline_handles = self.get_file_handles()
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'memory': self.get_memory_info(),
            'file_handles': self.get_file_handles(),
            'database': self.check_database_status(),
            'processing_queue': self.check_processing_queue(),
            'screenshot_files': self.check_screenshot_files()
        }
        
        # 计算变化
        if self.baseline_memory:
            result['memory_delta'] = {
                'rss_mb': result['memory']['rss'] - self.baseline_memory['rss'],
                'gc_objects': result['memory']['gc_objects'] - self.baseline_memory['gc_objects']
            }
        
        if self.baseline_handles and 'total_handles' in result['file_handles']:
            if 'total_handles' in self.baseline_handles:
                result['handles_delta'] = result['file_handles']['total_handles'] - self.baseline_handles['total_handles']
        
        return result
    
    def monitor_continuous(self, duration_minutes: int = 10, interval_seconds: int = 30):
        """连续监控"""
        print(f"开始连续监控 {duration_minutes} 分钟，每 {interval_seconds} 秒检查一次...")
        
        results = []
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            result = self.run_comprehensive_check()
            results.append(result)
            
            print(f"[{result['timestamp']}] 内存: {result['memory']['rss']:.1f}MB, "
                  f"句柄: {result['file_handles'].get('total_handles', 'N/A')}, "
                  f"队列: {result['processing_queue'].get('total', 'N/A')}")
            
            time.sleep(interval_seconds)
        
        # 保存结果
        output_file = f"diagnostic_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"监控完成，结果已保存到: {output_file}")
        return results

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LifeTrace 诊断工具')
    parser.add_argument('--mode', choices=['check', 'monitor'], default='check',
                       help='运行模式: check=单次检查, monitor=连续监控')
    parser.add_argument('--duration', type=int, default=10,
                       help='监控持续时间（分钟）')
    parser.add_argument('--interval', type=int, default=30,
                       help='监控间隔（秒）')
    
    args = parser.parse_args()
    
    diagnostic = SystemDiagnostic()
    
    if args.mode == 'check':
        result = diagnostic.run_comprehensive_check()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        diagnostic.monitor_continuous(args.duration, args.interval)

if __name__ == '__main__':
    main()