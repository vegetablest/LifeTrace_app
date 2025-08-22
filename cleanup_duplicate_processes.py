#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
进程清理脚本
清理重复的录制器进程，解决进程冲突问题
"""

import os
import sys
import psutil
import time
from datetime import datetime

def find_recorder_processes():
    """查找所有录制器进程"""
    recorder_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'create_time']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'recorder' in cmdline and 'python' in cmdline:
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                    create_time = datetime.fromtimestamp(proc.info['create_time'])
                    
                    recorder_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'memory_mb': memory_mb,
                        'create_time': create_time,
                        'process': proc
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return recorder_processes

def find_duplicate_ocr_processes():
    """查找重复的OCR进程"""
    ocr_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info', 'create_time']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'simple_ocr' in cmdline and 'python' in cmdline:
                    memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                    create_time = datetime.fromtimestamp(proc.info['create_time'])
                    
                    ocr_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'memory_mb': memory_mb,
                        'create_time': create_time,
                        'process': proc
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return ocr_processes

def cleanup_duplicate_processes():
    """清理重复进程"""
    print("开始清理重复进程...")
    print("=" * 50)
    
    # 查找录制器进程
    recorder_processes = find_recorder_processes()
    print(f"\n发现 {len(recorder_processes)} 个录制器进程:")
    
    for proc_info in recorder_processes:
        print(f"PID: {proc_info['pid']}")
        print(f"  命令行: {proc_info['cmdline']}")
        print(f"  内存使用: {proc_info['memory_mb']:.2f} MB")
        print(f"  创建时间: {proc_info['create_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # 如果有多个录制器进程，保留最新的一个
    if len(recorder_processes) > 1:
        print("检测到多个录制器进程，将保留最新的进程...")
        
        # 按创建时间排序，保留最新的
        recorder_processes.sort(key=lambda x: x['create_time'])
        processes_to_kill = recorder_processes[:-1]  # 除了最新的，其他都要终止
        
        for proc_info in processes_to_kill:
            try:
                print(f"终止进程 PID: {proc_info['pid']} (创建时间: {proc_info['create_time'].strftime('%Y-%m-%d %H:%M:%S')})")
                proc_info['process'].terminate()
                
                # 等待进程终止
                try:
                    proc_info['process'].wait(timeout=5)
                    print(f"  进程 {proc_info['pid']} 已正常终止")
                except psutil.TimeoutExpired:
                    print(f"  进程 {proc_info['pid']} 未在5秒内终止，强制杀死")
                    proc_info['process'].kill()
                    proc_info['process'].wait()
                    print(f"  进程 {proc_info['pid']} 已强制终止")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"  无法终止进程 {proc_info['pid']}: {e}")
        
        print(f"\n保留的录制器进程: PID {recorder_processes[-1]['pid']}")
    else:
        print("只有一个录制器进程，无需清理")
    
    # 查找OCR进程
    ocr_processes = find_duplicate_ocr_processes()
    print(f"\n发现 {len(ocr_processes)} 个OCR进程:")
    
    for proc_info in ocr_processes:
        print(f"PID: {proc_info['pid']}")
        print(f"  命令行: {proc_info['cmdline']}")
        print(f"  内存使用: {proc_info['memory_mb']:.2f} MB")
        print(f"  创建时间: {proc_info['create_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # 如果有多个OCR进程，保留最新的一个
    if len(ocr_processes) > 1:
        print("检测到多个OCR进程，将保留最新的进程...")
        
        # 按创建时间排序，保留最新的
        ocr_processes.sort(key=lambda x: x['create_time'])
        processes_to_kill = ocr_processes[:-1]  # 除了最新的，其他都要终止
        
        for proc_info in processes_to_kill:
            try:
                print(f"终止进程 PID: {proc_info['pid']} (创建时间: {proc_info['create_time'].strftime('%Y-%m-%d %H:%M:%S')})")
                proc_info['process'].terminate()
                
                # 等待进程终止
                try:
                    proc_info['process'].wait(timeout=5)
                    print(f"  进程 {proc_info['pid']} 已正常终止")
                except psutil.TimeoutExpired:
                    print(f"  进程 {proc_info['pid']} 未在5秒内终止，强制杀死")
                    proc_info['process'].kill()
                    proc_info['process'].wait()
                    print(f"  进程 {proc_info['pid']} 已强制终止")
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                print(f"  无法终止进程 {proc_info['pid']}: {e}")
        
        print(f"\n保留的OCR进程: PID {ocr_processes[-1]['pid']}")
    else:
        print("只有一个OCR进程，无需清理")

def check_memory_usage():
    """检查内存使用情况"""
    print("\n=== 内存使用检查 ===")
    
    high_memory_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            if proc.info['cmdline'] and 'python' in ' '.join(proc.info['cmdline']):
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0
                
                if memory_mb > 500:  # 超过500MB的进程
                    cmdline = ' '.join(proc.info['cmdline'])
                    high_memory_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': cmdline,
                        'memory_mb': memory_mb
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if high_memory_processes:
        print("发现高内存使用的Python进程:")
        for proc_info in high_memory_processes:
            print(f"PID: {proc_info['pid']}")
            print(f"  命令行: {proc_info['cmdline']}")
            print(f"  内存使用: {proc_info['memory_mb']:.2f} MB")
            print()
    else:
        print("未发现高内存使用的Python进程")
    
    return high_memory_processes

def main():
    """主函数"""
    print("进程清理工具")
    print("=" * 50)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 清理重复进程
        cleanup_duplicate_processes()
        
        # 等待一下，让系统稳定
        print("\n等待系统稳定...")
        time.sleep(3)
        
        # 检查内存使用
        check_memory_usage()
        
        print("\n=== 清理完成 ===")
        print("\n建议:")
        print("1. 重新检查录制器是否正常工作")
        print("2. 监控进程是否会再次重复启动")
        print("3. 如果问题持续，考虑重启所有服务")
        
    except Exception as e:
        print(f"\n清理过程中出现异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()