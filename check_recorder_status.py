#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查录制器服务状态
"""

import sys
import os
import psutil
import requests
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_recorder_process():
    """检查录制器进程状态"""
    print("=== 录制器进程检查 ===")
    
    # 查找录制器进程
    recorder_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline']:
                cmdline = ' '.join(proc.info['cmdline'])
                if 'recorder.py' in cmdline or 'screen_recorder' in cmdline:
                    recorder_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if recorder_processes:
        for proc in recorder_processes:
            print(f"✅ 找到录制器进程: PID {proc.pid}")
            print(f"   命令行: {' '.join(proc.cmdline())}")
            print(f"   状态: {proc.status()}")
            print(f"   CPU使用率: {proc.cpu_percent()}%")
            print(f"   内存使用: {proc.memory_info().rss / 1024 / 1024:.1f} MB")
    else:
        print("❌ 未找到录制器进程")
    
    return len(recorder_processes) > 0

def check_recorder_config():
    """检查录制器配置"""
    print("\n=== 录制器配置检查 ===")
    
    config_file = 'config.json'
    if os.path.exists(config_file):
        import json
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            recorder_config = config.get('recorder', {})
            print(f"录制间隔: {recorder_config.get('interval', 'N/A')} 秒")
            print(f"录制启用: {recorder_config.get('enabled', 'N/A')}")
            print(f"截图质量: {recorder_config.get('quality', 'N/A')}")
            
            # 检查截图目录配置
            storage_config = config.get('storage', {})
            screenshot_dir = storage_config.get('screenshot_dir', 'N/A')
            print(f"截图目录: {screenshot_dir}")
            
            if screenshot_dir != 'N/A':
                expanded_dir = os.path.expanduser(screenshot_dir)
                print(f"展开后目录: {expanded_dir}")
                print(f"目录存在: {os.path.exists(expanded_dir)}")
                
                if not os.path.exists(expanded_dir):
                    print(f"❌ 截图目录不存在，尝试创建...")
                    try:
                        os.makedirs(expanded_dir, exist_ok=True)
                        print(f"✅ 截图目录创建成功")
                    except Exception as e:
                        print(f"❌ 创建截图目录失败: {e}")
            
        except Exception as e:
            print(f"❌ 读取配置文件失败: {e}")
    else:
        print(f"❌ 配置文件不存在: {config_file}")

def check_recorder_logs():
    """检查录制器日志"""
    print("\n=== 录制器日志检查 ===")
    
    log_files = [
        'logs/recorder.log',
        'logs/app.log',
        'recorder.log'
    ]
    
    for log_file in log_files:
        if os.path.exists(log_file):
            print(f"\n📄 日志文件: {log_file}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print("最近的日志条目:")
                        for line in lines[-10:]:  # 显示最后10行
                            if 'recorder' in line.lower() or 'screenshot' in line.lower():
                                print(f"  {line.strip()}")
                    else:
                        print("  日志文件为空")
            except Exception as e:
                print(f"  ❌ 读取日志文件失败: {e}")
        else:
            print(f"❌ 日志文件不存在: {log_file}")

def check_system_resources():
    """检查系统资源"""
    print("\n=== 系统资源检查 ===")
    
    # 检查磁盘空间
    try:
        disk_usage = psutil.disk_usage('.')
        free_gb = disk_usage.free / (1024**3)
        print(f"磁盘剩余空间: {free_gb:.1f} GB")
        
        if free_gb < 1:
            print("⚠️ 磁盘空间不足，可能影响截图保存")
    except Exception as e:
        print(f"❌ 检查磁盘空间失败: {e}")
    
    # 检查内存使用
    try:
        memory = psutil.virtual_memory()
        print(f"内存使用率: {memory.percent}%")
        print(f"可用内存: {memory.available / (1024**3):.1f} GB")
    except Exception as e:
        print(f"❌ 检查内存使用失败: {e}")

def main():
    """主函数"""
    print("开始检查录制器状态...\n")
    
    # 检查进程
    process_running = check_recorder_process()
    
    # 检查配置
    check_recorder_config()
    
    # 检查日志
    check_recorder_logs()
    
    # 检查系统资源
    check_system_resources()
    
    print("\n=== 总结 ===")
    if process_running:
        print("✅ 录制器进程正在运行")
    else:
        print("❌ 录制器进程未运行")
    
    print("\n建议检查:")
    print("1. 确认录制器配置中的 enabled 设置为 true")
    print("2. 检查截图目录权限")
    print("3. 查看详细日志文件")
    print("4. 确认系统资源充足")

if __name__ == '__main__':
    main()