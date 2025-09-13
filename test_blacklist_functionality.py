#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
黑名单功能测试脚本
测试录制器的黑名单过滤功能是否正常工作
"""

import os
import sys
import time
import logging
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.config import config
from lifetrace_backend.recorder import ScreenRecorder
from lifetrace_backend.utils import get_active_window_info
from lifetrace_backend.logging_config import setup_logging

# 设置日志
setup_logging()
logger = logging.getLogger(__name__)

def test_window_info():
    """测试获取当前窗口信息"""
    print("\n=== 测试获取当前窗口信息 ===")
    
    app_name, window_title = get_active_window_info()
    print(f"当前应用: {app_name}")
    print(f"窗口标题: {window_title}")
    
    return app_name, window_title

def test_blacklist_config():
    """测试黑名单配置读取"""
    print("\n=== 测试黑名单配置读取 ===")
    
    blacklist_enabled = config.get('record.blacklist.enabled', False)
    blacklist_apps = config.get('record.blacklist.apps', [])
    blacklist_windows = config.get('record.blacklist.windows', [])
    
    print(f"黑名单功能启用: {blacklist_enabled}")
    print(f"黑名单应用列表: {blacklist_apps}")
    print(f"黑名单窗口列表: {blacklist_windows}")
    
    return blacklist_enabled, blacklist_apps, blacklist_windows

def test_blacklist_check():
    """测试黑名单检查功能"""
    print("\n=== 测试黑名单检查功能 ===")
    
    recorder = ScreenRecorder()
    
    # 获取当前窗口信息
    app_name, window_title = get_active_window_info()
    print(f"当前应用: {app_name}")
    print(f"当前窗口: {window_title}")
    
    # 测试黑名单检查
    is_blacklisted = recorder._is_app_blacklisted(app_name, window_title)
    print(f"是否在黑名单中: {is_blacklisted}")
    
    return is_blacklisted

def test_with_sample_blacklist():
    """使用示例黑名单进行测试"""
    print("\n=== 使用示例黑名单进行测试 ===")
    
    # 临时设置黑名单配置
    original_enabled = config.get('record.blacklist.enabled', False)
    original_apps = config.get('record.blacklist.apps', [])
    original_windows = config.get('record.blacklist.windows', [])
    
    try:
        # 设置测试黑名单
        config.set('record.blacklist.enabled', True)
        config.set('record.blacklist.apps', ['notepad.exe', 'calculator.exe', 'cmd.exe'])
        config.set('record.blacklist.windows', ['记事本', '计算器', '命令提示符'])
        
        print("已设置测试黑名单:")
        print(f"  应用: {config.get('record.blacklist.apps')}")
        print(f"  窗口: {config.get('record.blacklist.windows')}")
        
        recorder = ScreenRecorder()
        
        # 测试不同的应用和窗口
        test_cases = [
            ('notepad.exe', '无标题 - 记事本'),
            ('chrome.exe', 'Google Chrome'),
            ('calculator.exe', '计算器'),
            ('explorer.exe', '文件资源管理器'),
            ('cmd.exe', '命令提示符'),
        ]
        
        for app, window in test_cases:
            is_blacklisted = recorder._is_app_blacklisted(app, window)
            status = "✓ 已拦截" if is_blacklisted else "✗ 未拦截"
            print(f"  {app} - {window}: {status}")
        
    finally:
        # 恢复原始配置
        config.set('record.blacklist.enabled', original_enabled)
        config.set('record.blacklist.apps', original_apps)
        config.set('record.blacklist.windows', original_windows)

def test_screenshot_with_blacklist():
    """测试带黑名单的截图功能"""
    print("\n=== 测试带黑名单的截图功能 ===")
    
    # 获取当前窗口信息
    app_name, window_title = get_active_window_info()
    print(f"当前应用: {app_name}")
    print(f"当前窗口: {window_title}")
    
    recorder = ScreenRecorder()
    
    # 测试截图
    print("\n开始测试截图...")
    start_time = time.time()
    
    captured_files = recorder.capture_all_screens()
    
    elapsed = time.time() - start_time
    print(f"截图完成，耗时: {elapsed:.2f}秒")
    print(f"截取文件数: {len(captured_files)}")
    
    if captured_files:
        print("截取的文件:")
        for file_path in captured_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  {file_path} ({file_size} bytes)")
            else:
                print(f"  {file_path} (文件不存在)")
    else:
        print("没有截取任何文件（可能被黑名单拦截）")

def main():
    """主测试函数"""
    print("黑名单功能测试开始")
    print("=" * 50)
    
    try:
        # 1. 测试窗口信息获取
        test_window_info()
        
        # 2. 测试黑名单配置读取
        test_blacklist_config()
        
        # 3. 测试黑名单检查功能
        test_blacklist_check()
        
        # 4. 使用示例黑名单进行测试
        test_with_sample_blacklist()
        
        # 5. 测试带黑名单的截图功能
        test_screenshot_with_blacklist()
        
        print("\n=== 测试完成 ===")
        print("黑名单功能测试成功完成！")
        
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
        logger.error(f"黑名单功能测试失败: {e}", exc_info=True)
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)