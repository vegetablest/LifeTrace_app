#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试微信黑名单功能
"""

import os
import sys
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.recorder import ScreenRecorder
from lifetrace_backend.utils import get_active_window_info
from lifetrace_backend.logging_config import setup_logging

# 设置日志
setup_logging()

def test_weixin_blacklist():
    """测试微信黑名单功能"""
    print("=== 微信黑名单功能测试 ===")
    
    # 获取当前窗口信息
    app_name, window_title = get_active_window_info()
    print(f"当前应用: {app_name}")
    print(f"当前窗口: {window_title}")
    
    if app_name != 'Weixin.exe':
        print("\n警告: 当前不是微信应用，请切换到微信窗口后再运行此测试")
        print("等待5秒后继续测试...")
        time.sleep(5)
        
        # 重新获取窗口信息
        app_name, window_title = get_active_window_info()
        print(f"\n重新检测 - 当前应用: {app_name}")
        print(f"重新检测 - 当前窗口: {window_title}")
    
    # 创建录制器并测试黑名单
    recorder = ScreenRecorder()
    
    # 检查黑名单
    is_blacklisted = recorder._is_app_blacklisted(app_name, window_title)
    print(f"\n黑名单检查结果: {'✓ 已拦截' if is_blacklisted else '✗ 未拦截'}")
    
    # 测试截图
    print("\n开始截图测试...")
    start_time = time.time()
    
    captured_files = recorder.capture_all_screens()
    
    elapsed = time.time() - start_time
    print(f"截图完成，耗时: {elapsed:.2f}秒")
    print(f"截取文件数: {len(captured_files)}")
    
    if captured_files:
        print("\n❌ 测试失败: 微信应用应该被黑名单拦截，但仍然进行了截图")
        print("截取的文件:")
        for file_path in captured_files:
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"  {file_path} ({file_size} bytes)")
        return False
    else:
        print("\n✅ 测试成功: 微信应用被黑名单正确拦截，没有进行截图")
        return True

def main():
    """主函数"""
    print("请确保当前窗口是微信应用，然后按回车键开始测试...")
    input()
    
    success = test_weixin_blacklist()
    
    if success:
        print("\n🎉 微信黑名单功能测试通过！")
    else:
        print("\n❌ 微信黑名单功能测试失败！")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)