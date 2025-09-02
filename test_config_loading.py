#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置加载和心跳设置
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config

def test_config_loading():
    """测试配置加载"""
    print("=== LifeTrace 配置加载测试 ===")
    print(f"配置文件路径: {config.config_path}")
    print(f"配置文件是否存在: {Path(config.config_path).exists()}")
    print()
    
    print("=== 心跳监控配置 ===")
    print(f"心跳监控启用: {config.heartbeat_enabled}")
    print(f"心跳记录间隔: {config.heartbeat_interval} 秒")
    print(f"心跳超时时间: {config.heartbeat_timeout} 秒")
    print(f"心跳检查间隔: {config.heartbeat_check_interval} 秒")
    print(f"心跳日志目录: {config.heartbeat_log_dir}")
    print()
    
    print("=== 自动重启配置 ===")
    print(f"自动重启启用: {config.heartbeat_auto_restart_enabled}")
    print(f"最大重启次数: {config.heartbeat_max_restart_attempts}")
    print(f"重启延迟: {config.heartbeat_restart_delay} 秒")
    print(f"重启计数重置间隔: {config.heartbeat_reset_count_interval} 秒")
    print()
    
    # 检查配置文件内容
    if Path(config.config_path).exists():
        print("=== 配置文件内容检查 ===")
        try:
            import yaml
            with open(config.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            heartbeat_config = config_data.get('heartbeat', {})
            print(f"配置文件中的心跳超时: {heartbeat_config.get('timeout', '未设置')}")
            print(f"配置文件中的检查间隔: {heartbeat_config.get('check_interval', '未设置')}")
            
        except Exception as e:
            print(f"读取配置文件失败: {e}")
    
    print("\n=== 问题诊断 ===")
    if config.heartbeat_timeout == 30:
        print("⚠️  警告: 心跳超时时间仍为默认值30秒，配置文件可能未正确加载")
    elif config.heartbeat_timeout == 180:
        print("✅ 心跳超时时间已正确设置为180秒")
    else:
        print(f"ℹ️  心跳超时时间为: {config.heartbeat_timeout}秒")

if __name__ == '__main__':
    test_config_loading()