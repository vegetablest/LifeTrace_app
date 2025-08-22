#!/usr/bin/env python3
"""
内存分析工具
专门用于分析 LifeTrace 服务的内存使用模式和潜在泄漏
"""

import os
import sys
import gc
import tracemalloc
import psutil
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import weakref

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lifetrace_backend'))

class MemoryAnalyzer:
    """内存分析器"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.snapshots = []
        self.object_tracker = defaultdict(list)
        self.weak_refs = set()
        
        # 启动内存跟踪
        tracemalloc.start()
        
    def take_snapshot(self, label: str = None) -> Dict[str, Any]:
        """拍摄内存快照"""
        # 强制垃圾回收
        collected = gc.collect()
        
        # 获取进程内存信息
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # 获取 tracemalloc 快照
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        # 分析对象类型
        object_counts = Counter()
        for obj in gc.get_objects():
            obj_type = type(obj).__name__
            object_counts[obj_type] += 1
        
        # 分析大对象
        large_objects = []
        for obj in gc.get_objects():
            try:
                size = sys.getsizeof(obj)
                if size > 1024 * 1024:  # 大于1MB的对象
                    large_objects.append({
                        'type': type(obj).__name__,
                        'size_mb': size / 1024 / 1024,
                        'id': id(obj)
                    })
            except:
                pass
        
        snapshot_data = {
            'timestamp': datetime.now().isoformat(),
            'label': label or f"snapshot_{len(self.snapshots)}",
            'memory': {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent()
            },
            'gc': {
                'collected': collected,
                'total_objects': len(gc.get_objects()),
                'generations': [len(gc.get_objects(i)) for i in range(3)]
            },
            'top_memory_usage': [
                {
                    'file': stat.traceback.format()[-1] if stat.traceback else 'unknown',
                    'size_mb': stat.size / 1024 / 1024,
                    'count': stat.count
                }
                for stat in top_stats[:10]
            ],
            'object_counts': dict(object_counts.most_common(20)),
            'large_objects': large_objects[:10]
        }
        
        self.snapshots.append(snapshot_data)
        return snapshot_data
    
    def track_object_creation(self, obj_type: type, max_instances: int = 100):
        """跟踪特定类型对象的创建"""
        original_new = obj_type.__new__
        
        def tracked_new(cls, *args, **kwargs):
            instance = original_new(cls)
            
            # 使用弱引用跟踪对象
            weak_ref = weakref.ref(instance, lambda ref: self.weak_refs.discard(ref))
            self.weak_refs.add(weak_ref)
            
            # 记录创建信息
            self.object_tracker[obj_type.__name__].append({
                'created_at': datetime.now(),
                'traceback': tracemalloc.get_traced_memory(),
                'weak_ref': weak_ref
            })
            
            # 限制跟踪数量
            if len(self.object_tracker[obj_type.__name__]) > max_instances:
                self.object_tracker[obj_type.__name__].pop(0)
            
            return instance
        
        obj_type.__new__ = tracked_new
    
    def analyze_memory_growth(self) -> Dict[str, Any]:
        """分析内存增长模式"""
        if len(self.snapshots) < 2:
            return {'error': 'Need at least 2 snapshots'}
        
        first = self.snapshots[0]
        last = self.snapshots[-1]
        
        memory_growth = {
            'rss_mb': last['memory']['rss_mb'] - first['memory']['rss_mb'],
            'vms_mb': last['memory']['vms_mb'] - first['memory']['vms_mb'],
            'objects': last['gc']['total_objects'] - first['gc']['total_objects']
        }
        
        # 分析对象类型变化
        object_changes = {}
        first_counts = first['object_counts']
        last_counts = last['object_counts']
        
        all_types = set(first_counts.keys()) | set(last_counts.keys())
        for obj_type in all_types:
            first_count = first_counts.get(obj_type, 0)
            last_count = last_counts.get(obj_type, 0)
            change = last_count - first_count
            if abs(change) > 10:  # 只关注显著变化
                object_changes[obj_type] = change
        
        return {
            'memory_growth': memory_growth,
            'object_changes': object_changes,
            'duration_seconds': (datetime.fromisoformat(last['timestamp']) - 
                               datetime.fromisoformat(first['timestamp'])).total_seconds()
        }
    
    def find_memory_leaks(self) -> List[Dict[str, Any]]:
        """查找潜在的内存泄漏"""
        leaks = []
        
        # 检查持续增长的对象类型
        if len(self.snapshots) >= 3:
            for i in range(len(self.snapshots) - 2):
                current = self.snapshots[i]
                next_snap = self.snapshots[i + 1]
                last_snap = self.snapshots[i + 2]
                
                for obj_type in current['object_counts']:
                    current_count = current['object_counts'].get(obj_type, 0)
                    next_count = next_snap['object_counts'].get(obj_type, 0)
                    last_count = last_snap['object_counts'].get(obj_type, 0)
                    
                    # 检查是否持续增长
                    if (next_count > current_count and 
                        last_count > next_count and 
                        last_count - current_count > 50):
                        
                        leaks.append({
                            'type': obj_type,
                            'growth_pattern': [current_count, next_count, last_count],
                            'total_growth': last_count - current_count,
                            'severity': 'high' if last_count - current_count > 1000 else 'medium'
                        })
        
        # 检查大对象
        if self.snapshots:
            last_snapshot = self.snapshots[-1]
            for large_obj in last_snapshot['large_objects']:
                if large_obj['size_mb'] > 10:  # 大于10MB
                    leaks.append({
                        'type': 'large_object',
                        'object_type': large_obj['type'],
                        'size_mb': large_obj['size_mb'],
                        'severity': 'critical' if large_obj['size_mb'] > 50 else 'high'
                    })
        
        return leaks
    
    def generate_report(self) -> str:
        """生成内存分析报告"""
        report = []
        report.append("=== LifeTrace 内存分析报告 ===")
        report.append(f"分析时间: {self.start_time} - {datetime.now()}")
        report.append(f"快照数量: {len(self.snapshots)}")
        report.append("")
        
        if self.snapshots:
            # 当前内存状态
            current = self.snapshots[-1]
            report.append("=== 当前内存状态 ===")
            report.append(f"RSS内存: {current['memory']['rss_mb']:.1f} MB")
            report.append(f"虚拟内存: {current['memory']['vms_mb']:.1f} MB")
            report.append(f"内存占用率: {current['memory']['percent']:.1f}%")
            report.append(f"总对象数: {current['gc']['total_objects']:,}")
            report.append("")
            
            # 内存增长分析
            growth = self.analyze_memory_growth()
            if 'memory_growth' in growth:
                report.append("=== 内存增长分析 ===")
                mg = growth['memory_growth']
                report.append(f"RSS增长: {mg['rss_mb']:+.1f} MB")
                report.append(f"对象增长: {mg['objects']:+,}")
                report.append(f"分析时长: {growth['duration_seconds']:.1f} 秒")
                report.append("")
                
                if growth['object_changes']:
                    report.append("对象类型变化:")
                    for obj_type, change in sorted(growth['object_changes'].items(), 
                                                  key=lambda x: abs(x[1]), reverse=True)[:10]:
                        report.append(f"  {obj_type}: {change:+,}")
                    report.append("")
            
            # 内存泄漏检测
            leaks = self.find_memory_leaks()
            if leaks:
                report.append("=== 潜在内存泄漏 ===")
                for leak in leaks:
                    if leak['type'] == 'large_object':
                        report.append(f"大对象: {leak['object_type']} ({leak['size_mb']:.1f} MB) - {leak['severity']}")
                    else:
                        report.append(f"对象增长: {leak['type']} (+{leak['total_growth']}) - {leak['severity']}")
                report.append("")
            
            # 顶级内存使用
            report.append("=== 顶级内存使用 ===")
            for usage in current['top_memory_usage'][:5]:
                report.append(f"{usage['size_mb']:.1f} MB - {usage['file']}")
        
        return "\n".join(report)

def monitor_memory_during_operation(duration_minutes: int = 5):
    """在操作期间监控内存"""
    analyzer = MemoryAnalyzer()
    
    print(f"开始内存监控，持续 {duration_minutes} 分钟...")
    
    # 初始快照
    analyzer.take_snapshot("initial")
    
    # 定期拍摄快照
    interval = 30  # 30秒间隔
    snapshots_count = (duration_minutes * 60) // interval
    
    for i in range(snapshots_count):
        time.sleep(interval)
        snapshot = analyzer.take_snapshot(f"interval_{i+1}")
        print(f"快照 {i+1}: RSS={snapshot['memory']['rss_mb']:.1f}MB, "
              f"对象={snapshot['gc']['total_objects']:,}")
    
    # 最终快照
    analyzer.take_snapshot("final")
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 保存报告
    report_file = f"memory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n内存分析完成，报告已保存到: {report_file}")
    print("\n=== 报告摘要 ===")
    print(report)
    
    return analyzer

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LifeTrace 内存分析工具')
    parser.add_argument('--duration', type=int, default=5,
                       help='监控持续时间（分钟）')
    
    args = parser.parse_args()
    
    monitor_memory_during_operation(args.duration)

if __name__ == '__main__':
    main()