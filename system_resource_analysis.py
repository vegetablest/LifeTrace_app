#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LifeTrace系统资源占用分析工具
分析当前系统中LifeTrace相关进程的资源使用情况
"""

import psutil
import os
import sqlite3
from pathlib import Path
import time
from datetime import datetime

def get_lifetrace_processes():
    """获取所有LifeTrace相关的进程"""
    lifetrace_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'cpu_percent']):
        try:
            # 检查进程名称或命令行参数中是否包含lifetrace相关关键词
            cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
            
            if any(keyword in cmdline.lower() for keyword in [
                'lifetrace', 'recorder.py', 'processor.py', 'server.py', 
                'start_all_services.py', 'start_ocr_service.py'
            ]):
                # 获取详细的CPU使用率（需要一点时间来计算）
                cpu_percent = proc.cpu_percent(interval=0.1)
                
                process_info = {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': cmdline,
                    'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                    'memory_vms_mb': proc.info['memory_info'].vms / 1024 / 1024,
                    'cpu_percent': cpu_percent
                }
                lifetrace_processes.append(process_info)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return lifetrace_processes

def get_system_resources():
    """获取系统整体资源使用情况"""
    # 内存信息
    memory = psutil.virtual_memory()
    
    # CPU信息
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    
    # 磁盘信息
    disk_usage = {}
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_usage[partition.device] = {
                'total_gb': usage.total / 1024**3,
                'used_gb': usage.used / 1024**3,
                'free_gb': usage.free / 1024**3,
                'percent': (usage.used / usage.total) * 100
            }
        except PermissionError:
            continue
    
    return {
        'memory': {
            'total_gb': memory.total / 1024**3,
            'available_gb': memory.available / 1024**3,
            'used_gb': (memory.total - memory.available) / 1024**3,
            'percent': memory.percent
        },
        'cpu': {
            'percent': cpu_percent,
            'count': cpu_count
        },
        'disk': disk_usage
    }

def get_database_size():
    """获取数据库文件大小"""
    db_path = Path.home() / '.lifetrace' / 'lifetrace.db'
    if db_path.exists():
        return db_path.stat().st_size / 1024 / 1024  # MB
    return 0

def get_screenshots_info():
    """获取截图文件夹信息"""
    screenshots_path = Path.home() / '.lifetrace' / 'screenshots'
    if not screenshots_path.exists():
        return {'count': 0, 'total_size_mb': 0}
    
    total_size = 0
    file_count = 0
    
    for file_path in screenshots_path.glob('*.png'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
            file_count += 1
    
    return {
        'count': file_count,
        'total_size_mb': total_size / 1024 / 1024
    }

def analyze_resource_usage():
    """分析资源使用情况"""
    print("=" * 60)
    print(f"LifeTrace系统资源占用分析报告")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 系统整体资源
    print("\n📊 系统整体资源使用情况:")
    system_resources = get_system_resources()
    
    memory = system_resources['memory']
    print(f"  内存: {memory['used_gb']:.2f}GB / {memory['total_gb']:.2f}GB ({memory['percent']:.1f}%)")
    print(f"  可用内存: {memory['available_gb']:.2f}GB")
    
    cpu = system_resources['cpu']
    print(f"  CPU: {cpu['percent']:.1f}% (核心数: {cpu['count']})")
    
    print(f"\n  磁盘使用情况:")
    for device, usage in system_resources['disk'].items():
        print(f"    {device} {usage['used_gb']:.1f}GB / {usage['total_gb']:.1f}GB ({usage['percent']:.1f}%)")
    
    # LifeTrace进程
    print("\n🔍 LifeTrace相关进程:")
    lifetrace_processes = get_lifetrace_processes()
    
    if not lifetrace_processes:
        print("  ❌ 未发现运行中的LifeTrace进程")
    else:
        total_memory = 0
        total_cpu = 0
        
        for proc in lifetrace_processes:
            print(f"  PID {proc['pid']}: {proc['name']}")
            print(f"    内存: {proc['memory_mb']:.1f}MB (虚拟内存: {proc['memory_vms_mb']:.1f}MB)")
            print(f"    CPU: {proc['cpu_percent']:.1f}%")
            print(f"    命令行: {proc['cmdline'][:80]}..." if len(proc['cmdline']) > 80 else f"    命令行: {proc['cmdline']}")
            print()
            
            total_memory += proc['memory_mb']
            total_cpu += proc['cpu_percent']
        
        print(f"  📈 LifeTrace进程总计:")
        print(f"    总内存使用: {total_memory:.1f}MB ({total_memory/1024:.2f}GB)")
        print(f"    总CPU使用: {total_cpu:.1f}%")
        print(f"    进程数量: {len(lifetrace_processes)}")
    
    # 数据存储
    print("\n💾 数据存储情况:")
    db_size = get_database_size()
    print(f"  数据库大小: {db_size:.2f}MB")
    
    screenshots_info = get_screenshots_info()
    print(f"  截图文件: {screenshots_info['count']} 个文件, {screenshots_info['total_size_mb']:.2f}MB")
    
    total_storage = db_size + screenshots_info['total_size_mb']
    print(f"  总存储占用: {total_storage:.2f}MB ({total_storage/1024:.2f}GB)")
    
    # 资源使用评估
    print("\n📋 资源使用评估:")
    
    # 内存评估
    if total_memory > 2000:  # 超过2GB
        print(f"  ⚠️  内存使用较高: {total_memory:.1f}MB")
    elif total_memory > 1000:  # 超过1GB
        print(f"  ⚡ 内存使用中等: {total_memory:.1f}MB")
    else:
        print(f"  ✅ 内存使用正常: {total_memory:.1f}MB")
    
    # CPU评估
    if total_cpu > 50:
        print(f"  ⚠️  CPU使用较高: {total_cpu:.1f}%")
    elif total_cpu > 20:
        print(f"  ⚡ CPU使用中等: {total_cpu:.1f}%")
    else:
        print(f"  ✅ CPU使用正常: {total_cpu:.1f}%")
    
    # 存储评估
    if total_storage > 5000:  # 超过5GB
        print(f"  ⚠️  存储占用较大: {total_storage:.2f}MB")
    elif total_storage > 1000:  # 超过1GB
        print(f"  ⚡ 存储占用中等: {total_storage:.2f}MB")
    else:
        print(f"  ✅ 存储占用正常: {total_storage:.2f}MB")
    
    print("\n" + "=" * 60)
    
    return {
        'system_resources': system_resources,
        'lifetrace_processes': lifetrace_processes,
        'storage': {
            'database_mb': db_size,
            'screenshots': screenshots_info,
            'total_mb': total_storage
        },
        'summary': {
            'total_memory_mb': total_memory if lifetrace_processes else 0,
            'total_cpu_percent': total_cpu if lifetrace_processes else 0,
            'process_count': len(lifetrace_processes),
            'total_storage_mb': total_storage
        }
    }

if __name__ == "__main__":
    try:
        result = analyze_resource_usage()
    except Exception as e:
        print(f"❌ 分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()