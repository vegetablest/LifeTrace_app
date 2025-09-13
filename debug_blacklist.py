#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试黑名单匹配逻辑
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.config import config
from lifetrace_backend.utils import get_active_window_info

def debug_blacklist_matching():
    """调试黑名单匹配逻辑"""
    print("=== 调试黑名单匹配逻辑 ===")
    
    # 获取当前窗口信息
    app_name, window_title = get_active_window_info()
    print(f"当前应用: '{app_name}'")
    print(f"当前窗口: '{window_title}'")
    
    # 获取黑名单配置
    blacklist_enabled = config.get('record.blacklist.enabled', False)
    blacklist_apps = config.get('record.blacklist.apps', [])
    blacklist_windows = config.get('record.blacklist.windows', [])
    
    print(f"\n黑名单启用: {blacklist_enabled}")
    print(f"黑名单应用: {blacklist_apps}")
    print(f"黑名单窗口: {blacklist_windows}")
    
    if not blacklist_enabled:
        print("\n黑名单功能未启用")
        return
    
    # 检查应用名匹配
    print(f"\n=== 应用名匹配检查 ===")
    if app_name and blacklist_apps:
        app_name_lower = app_name.lower()
        print(f"应用名(小写): '{app_name_lower}'")
        
        for blacklist_app in blacklist_apps:
            blacklist_app_lower = blacklist_app.lower()
            exact_match = blacklist_app_lower == app_name_lower
            partial_match = blacklist_app_lower in app_name_lower
            
            print(f"  检查 '{blacklist_app}' ('{blacklist_app_lower}'):")
            print(f"    精确匹配: {exact_match}")
            print(f"    部分匹配: {partial_match}")
            print(f"    结果: {'匹配' if exact_match or partial_match else '不匹配'}")
    
    # 检查窗口标题匹配
    print(f"\n=== 窗口标题匹配检查 ===")
    if window_title and blacklist_windows:
        window_title_lower = window_title.lower()
        print(f"窗口标题(小写): '{window_title_lower}'")
        
        for blacklist_window in blacklist_windows:
            blacklist_window_lower = blacklist_window.lower()
            exact_match = blacklist_window_lower == window_title_lower
            partial_match = blacklist_window_lower in window_title_lower
            
            print(f"  检查 '{blacklist_window}' ('{blacklist_window_lower}'):")
            print(f"    精确匹配: {exact_match}")
            print(f"    部分匹配: {partial_match}")
            print(f"    结果: {'匹配' if exact_match or partial_match else '不匹配'}")

if __name__ == '__main__':
    debug_blacklist_matching()