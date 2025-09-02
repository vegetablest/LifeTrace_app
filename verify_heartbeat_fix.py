#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证心跳超时修复
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config

def verify_heartbeat_fix():
    """验证心跳超时修复"""
    print("=== LifeTrace 心跳超时问题修复验证 ===")
    print()
    
    print("🔍 问题分析:")
    print("用户反映OCR服务在38.5秒时就被重启，但配置文件设置的是180秒")
    print()
    
    print("🛠️  修复内容:")
    print("1. 修改了配置文件加载逻辑，优先从项目目录加载配置")
    print("2. 之前配置加载路径: ~/.lifetrace/config.yaml")
    print("3. 现在配置加载路径: 项目目录/config/default_config.yaml")
    print()
    
    print("📋 当前配置状态:")
    print(f"配置文件路径: {config.config_path}")
    print(f"配置文件存在: {Path(config.config_path).exists()}")
    print(f"心跳超时时间: {config.heartbeat_timeout} 秒")
    print(f"心跳检查间隔: {config.heartbeat_check_interval} 秒")
    print()
    
    print("✅ 修复验证:")
    if config.heartbeat_timeout == 180:
        print("✅ 心跳超时时间已正确设置为180秒")
        print("✅ 配置文件加载正常")
    else:
        print(f"❌ 心跳超时时间异常: {config.heartbeat_timeout}秒")
        return False
    
    if config.heartbeat_check_interval == 180:
        print("✅ 心跳检查间隔已正确设置为180秒")
    else:
        print(f"❌ 心跳检查间隔异常: {config.heartbeat_check_interval}秒")
        return False
    
    print()
    print("🚀 下一步操作:")
    print("1. 如果ServiceManager正在运行，需要重启它以应用新配置")
    print("2. 重启命令: python start_all_services.py")
    print("3. 重启后，OCR服务将按照180秒的超时时间进行监控")
    print()
    
    print("📝 问题原因总结:")
    print("之前出现38.5秒重启的原因是:")
    print("- 配置加载逻辑错误，没有读取到项目目录下的配置文件")
    print("- 系统使用了默认的30秒超时时间")
    print("- 当心跳文件读取出现问题时，触发了重启机制")
    print("- 现在已修复配置加载问题，将使用正确的180秒超时")
    
    return True

if __name__ == '__main__':
    verify_heartbeat_fix()