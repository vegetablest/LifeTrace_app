#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心跳检查修复验证脚本
测试修复后的心跳文件路径是否正确
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config

def test_heartbeat_file_paths():
    """测试心跳文件路径映射"""
    print("🔍 测试心跳文件路径映射")
    print("=" * 40)
    
    # 模拟ServiceManager的映射逻辑
    heartbeat_mapping = {
        "录制器": "recorder",
        "处理器": "processor", 
        "OCR服务": "ocr",
        "Web服务": "server"
    }
    
    heartbeat_dir = config.heartbeat_log_dir
    print(f"心跳日志目录: {heartbeat_dir}")
    
    print("\n📋 服务名称映射测试:")
    for service_name, expected_name in heartbeat_mapping.items():
        heartbeat_file_name = heartbeat_mapping.get(service_name, service_name.lower())
        heartbeat_file = os.path.join(heartbeat_dir, f"{heartbeat_file_name}_heartbeat.log")
        
        exists = os.path.exists(heartbeat_file)
        status = "✅ 存在" if exists else "❌ 不存在"
        
        print(f"  {service_name}:")
        print(f"    映射名称: {heartbeat_file_name}")
        print(f"    文件路径: {heartbeat_file}")
        print(f"    文件状态: {status}")
        
        if exists:
            try:
                # 读取最后一行心跳
                with open(heartbeat_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if last_line:
                            import json
                            heartbeat = json.loads(last_line)
                            heartbeat_time = datetime.fromisoformat(heartbeat['timestamp'])
                            current_time = datetime.now()
                            time_diff = (current_time - heartbeat_time).total_seconds()
                            
                            print(f"    最新心跳: {heartbeat['timestamp']}")
                            print(f"    时间差: {time_diff:.1f} 秒")
                            print(f"    PID: {heartbeat.get('pid', 'N/A')}")
                            print(f"    状态: {heartbeat.get('status', 'N/A')}")
            except Exception as e:
                print(f"    ❌ 读取失败: {e}")
        
        print()
    
    print("\n📁 实际心跳文件列表:")
    if os.path.exists(heartbeat_dir):
        for file in os.listdir(heartbeat_dir):
            if file.endswith('_heartbeat.log'):
                file_path = os.path.join(heartbeat_dir, file)
                size = os.path.getsize(file_path)
                print(f"  {file} ({size} bytes)")
    else:
        print(f"  心跳目录不存在: {heartbeat_dir}")

if __name__ == '__main__':
    test_heartbeat_file_paths()