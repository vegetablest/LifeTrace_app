#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
录制器异常分析脚本
分析录制器进程为什么会出现异常停止工作的情况
"""

import os
import sys
import psutil
import sqlite3
import json
import traceback
from datetime import datetime, timedelta
from pathlib import Path

def check_system_resources():
    """检查系统资源使用情况"""
    print("\n=== 系统资源检查 ===")
    
    # CPU使用率
    cpu_percent = psutil.cpu_percent(interval=1)
    print(f"CPU使用率: {cpu_percent}%")
    
    # 内存使用情况
    memory = psutil.virtual_memory()
    print(f"内存使用率: {memory.percent}%")
    print(f"可用内存: {memory.available / 1024 / 1024 / 1024:.2f} GB")
    
    # 磁盘使用情况
    disk = psutil.disk_usage('E:\\')
    print(f"磁盘使用率: {disk.used / disk.total * 100:.2f}%")
    print(f"可用磁盘空间: {disk.free / 1024 / 1024 / 1024:.2f} GB")
    
    return {
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': disk.used / disk.total * 100
    }

def check_python_processes():
    """检查Python进程情况"""
    print("\n=== Python进程检查 ===")
    
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'create_time']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else 'N/A'
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                create_time = datetime.fromtimestamp(proc.info['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                
                python_processes.append({
                    'pid': proc.info['pid'],
                    'cmdline': cmdline,
                    'memory_mb': memory_mb,
                    'create_time': create_time
                })
                
                print(f"PID: {proc.info['pid']}")
                print(f"  命令行: {cmdline}")
                print(f"  内存使用: {memory_mb:.2f} MB")
                print(f"  创建时间: {create_time}")
                print()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return python_processes

def check_file_handles():
    """检查文件句柄使用情况"""
    print("\n=== 文件句柄检查 ===")
    
    try:
        # 检查当前进程的文件句柄
        current_process = psutil.Process()
        open_files = current_process.open_files()
        print(f"当前进程打开的文件数: {len(open_files)}")
        
        # 检查截图目录相关的文件句柄
        screenshot_files = [f for f in open_files if 'screenshot' in f.path.lower()]
        if screenshot_files:
            print("\n截图相关的打开文件:")
            for f in screenshot_files:
                print(f"  {f.path}")
        
        # 检查数据库文件句柄
        db_files = [f for f in open_files if f.path.endswith('.db') or f.path.endswith('.sqlite3')]
        if db_files:
            print("\n数据库相关的打开文件:")
            for f in db_files:
                print(f"  {f.path}")
                
    except Exception as e:
        print(f"检查文件句柄时出错: {e}")

def check_database_status():
    """检查数据库状态"""
    print("\n=== 数据库状态检查 ===")
    
    db_path = Path.home() / '.lifetrace' / 'lifetrace.db'
    
    if not db_path.exists():
        print(f"数据库文件不存在: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        cursor = conn.cursor()
        
        # 检查数据库文件大小
        db_size = db_path.stat().st_size / 1024 / 1024
        print(f"数据库文件大小: {db_size:.2f} MB")
        
        # 检查表结构
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"数据库表数量: {len(tables)}")
        
        # 检查截图记录数量
        cursor.execute("SELECT COUNT(*) FROM screenshots")
        screenshot_count = cursor.fetchone()[0]
        print(f"截图记录数量: {screenshot_count}")
        
        # 检查最近的截图记录
        cursor.execute("""
            SELECT timestamp, file_path 
            FROM screenshots 
            ORDER BY timestamp DESC 
            LIMIT 5
        """)
        recent_screenshots = cursor.fetchall()
        
        if recent_screenshots:
            print("\n最近的截图记录:")
            for timestamp, file_path in recent_screenshots:
                print(f"  {timestamp}: {file_path}")
        
        # 检查数据库锁定状态
        cursor.execute("PRAGMA locking_mode")
        locking_mode = cursor.fetchone()[0]
        print(f"\n数据库锁定模式: {locking_mode}")
        
        cursor.execute("PRAGMA journal_mode")
        journal_mode = cursor.fetchone()[0]
        print(f"日志模式: {journal_mode}")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库检查出错: {e}")
    except Exception as e:
        print(f"检查数据库时出现异常: {e}")

def check_screenshot_directory():
    """检查截图目录状态"""
    print("\n=== 截图目录检查 ===")
    
    screenshot_dir = Path.home() / '.lifetrace' / 'screenshots'
    
    if not screenshot_dir.exists():
        print(f"截图目录不存在: {screenshot_dir}")
        return
    
    # 统计文件数量和大小
    png_files = list(screenshot_dir.glob('*.png'))
    total_size = sum(f.stat().st_size for f in png_files) / 1024 / 1024
    
    print(f"截图目录: {screenshot_dir}")
    print(f"PNG文件数量: {len(png_files)}")
    print(f"总大小: {total_size:.2f} MB")
    
    if png_files:
        # 最新和最旧的文件
        newest_file = max(png_files, key=lambda f: f.stat().st_mtime)
        oldest_file = min(png_files, key=lambda f: f.stat().st_mtime)
        
        newest_time = datetime.fromtimestamp(newest_file.stat().st_mtime)
        oldest_time = datetime.fromtimestamp(oldest_file.stat().st_mtime)
        
        print(f"\n最新文件: {newest_file.name}")
        print(f"最新时间: {newest_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"最旧文件: {oldest_file.name}")
        print(f"最旧时间: {oldest_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 检查最近1小时内的文件
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_files = [f for f in png_files if datetime.fromtimestamp(f.stat().st_mtime) > one_hour_ago]
        print(f"\n最近1小时内的文件: {len(recent_files)}")

def analyze_potential_causes():
    """分析可能的异常原因"""
    print("\n=== 潜在异常原因分析 ===")
    
    causes = []
    
    # 检查系统资源
    resources = check_system_resources()
    
    if resources['memory_percent'] > 90:
        causes.append("内存使用率过高，可能导致进程异常")
    
    if resources['cpu_percent'] > 95:
        causes.append("CPU使用率过高，可能影响进程稳定性")
    
    if resources['disk_percent'] > 95:
        causes.append("磁盘空间不足，可能导致文件写入失败")
    
    # 检查Python进程数量
    python_processes = check_python_processes()
    recorder_processes = [p for p in python_processes if 'recorder' in p['cmdline']]
    
    if len(recorder_processes) > 1:
        causes.append(f"发现多个录制器进程({len(recorder_processes)}个)，可能存在进程冲突")
    
    # 检查内存使用
    high_memory_processes = [p for p in python_processes if p['memory_mb'] > 500]
    if high_memory_processes:
        causes.append(f"发现高内存使用的Python进程({len(high_memory_processes)}个)，可能存在内存泄漏")
    
    print("\n可能的异常原因:")
    if causes:
        for i, cause in enumerate(causes, 1):
            print(f"{i}. {cause}")
    else:
        print("未发现明显的系统级异常原因")
    
    return causes

def check_error_logs():
    """检查错误日志"""
    print("\n=== 错误日志检查 ===")
    
    log_dirs = [
        Path('data/logs/error'),
        Path('data/logs/core'),
        Path('data/logs/app'),
        Path('data/logs/debug')
    ]
    
    error_found = False
    
    for log_dir in log_dirs:
        if log_dir.exists():
            log_files = list(log_dir.glob('*.log'))
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if any(keyword in content.lower() for keyword in ['error', 'exception', 'traceback', 'failed']):
                            print(f"\n在 {log_file} 中发现错误信息:")
                            lines = content.split('\n')
                            error_lines = [line for line in lines if any(keyword in line.lower() for keyword in ['error', 'exception', 'traceback', 'failed'])]
                            for line in error_lines[-10:]:  # 显示最后10个错误行
                                print(f"  {line}")
                            error_found = True
                except Exception as e:
                    print(f"读取日志文件 {log_file} 时出错: {e}")
    
    if not error_found:
        print("未在日志文件中发现明显的错误信息")

def main():
    """主函数"""
    print("录制器异常分析报告")
    print("=" * 50)
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 系统资源检查
        check_system_resources()
        
        # Python进程检查
        check_python_processes()
        
        # 文件句柄检查
        check_file_handles()
        
        # 数据库状态检查
        check_database_status()
        
        # 截图目录检查
        check_screenshot_directory()
        
        # 错误日志检查
        check_error_logs()
        
        # 分析潜在原因
        analyze_potential_causes()
        
        print("\n=== 分析完成 ===")
        print("\n建议的预防措施:")
        print("1. 定期监控系统资源使用情况")
        print("2. 实现进程健康检查机制")
        print("3. 添加异常处理和自动重启功能")
        print("4. 定期清理日志和临时文件")
        print("5. 监控内存使用，防止内存泄漏")
        
    except Exception as e:
        print(f"\n分析过程中出现异常: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    main()