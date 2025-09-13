#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试跨平台应用名称映射功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.app_mapping import AppMapper, expand_blacklist_apps
from lifetrace_backend.config import config
from lifetrace_backend.recorder import ScreenRecorder
from lifetrace_backend.utils import get_active_window_info

def test_app_mapping():
    """测试应用名称映射功能"""
    print("=== 测试应用名称映射功能 ===")
    
    # 测试映射字典
    mapper = AppMapper()
    print(f"支持的应用映射: {mapper.get_supported_apps()}")
    
    # 测试获取进程名
    test_apps = ["微信", "QQ", "钉钉", "记事本", "计算器", "不存在的应用"]
    for app in test_apps:
        processes = mapper.get_process_names(app)
        print(f"应用 '{app}' -> 进程名: {processes}")
    
    # 测试扩展黑名单
    print("\n=== 测试黑名单扩展功能 ===")
    friendly_blacklist = ["微信", "QQ", "计算器", "不存在的应用"]
    expanded_blacklist = expand_blacklist_apps(friendly_blacklist)
    print(f"友好黑名单: {friendly_blacklist}")
    print(f"扩展后黑名单: {expanded_blacklist}")
    
    # 测试配置文件中的黑名单
    print("\n=== 测试配置文件黑名单 ===")
    blacklist_enabled = config.get('record.blacklist.enabled', False)
    config_blacklist = config.get('record.blacklist.apps', [])
    print(f"黑名单启用状态: {blacklist_enabled}")
    print(f"配置文件黑名单: {config_blacklist}")
    
    if config_blacklist:
        expanded_config_blacklist = expand_blacklist_apps(config_blacklist)
        print(f"配置文件扩展后黑名单: {expanded_config_blacklist}")
    
    # 测试当前窗口是否被拦截
    print("\n=== 测试当前窗口拦截 ===")
    try:
        app_name, window_title = get_active_window_info()
        print(f"当前应用: {app_name}")
        print(f"当前窗口标题: {window_title}")
        
        if blacklist_enabled and config_blacklist:
            recorder = ScreenRecorder()
            is_blacklisted = recorder._is_app_blacklisted(app_name, window_title)
            print(f"当前窗口是否被拦截: {is_blacklisted}")
        else:
            print("黑名单功能未启用")
    except Exception as e:
        print(f"获取当前窗口信息失败: {e}")

def test_specific_apps():
    """测试特定应用的映射"""
    print("\n=== 测试特定应用映射 ===")
    
    # 模拟不同的应用名称测试
    test_cases = [
        ("Weixin.exe", "微信"),
        ("QQ.exe", "微信"),  # 应该不匹配
        ("WeChat.exe", "微信"),
        ("notepad.exe", "记事本"),
        ("calc.exe", "计算器"),
        ("Calculator.exe", "计算器"),
    ]
    
    mapper = AppMapper()
    for process_name, friendly_name in test_cases:
        processes = mapper.get_process_names(friendly_name)
        is_match = process_name.lower() in [p.lower() for p in processes]
        print(f"进程 '{process_name}' 是否匹配应用 '{friendly_name}': {is_match}")
        if is_match:
            print(f"  匹配的进程列表: {processes}")

if __name__ == "__main__":
    test_app_mapping()
    test_specific_apps()
    print("\n测试完成！")