#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试超时机制

这个脚本用于测试recorder.py中新添加的超时机制是否正常工作。
"""

import os
import sys
import time
import tempfile
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from lifetrace_backend.recorder import ScreenRecorder, with_timeout
from lifetrace_backend.config import config
from lifetrace_backend.logging_config import setup_logging

# 设置日志
logger_manager = setup_logging(config)
logger = logger_manager.get_recorder_logger()

def test_timeout_decorator():
    """测试超时装饰器"""
    print("\n=== 测试超时装饰器 ===")
    
    @with_timeout(timeout_seconds=2, operation_name="快速操作")
    def fast_operation():
        time.sleep(1)
        return "快速操作完成"
    
    @with_timeout(timeout_seconds=2, operation_name="慢速操作")
    def slow_operation():
        time.sleep(5)  # 超过2秒超时
        return "慢速操作完成"
    
    # 测试快速操作
    print("测试快速操作（1秒，超时2秒）...")
    result = fast_operation()
    print(f"结果: {result}")
    
    # 测试慢速操作
    print("\n测试慢速操作（5秒，超时2秒）...")
    result = slow_operation()
    print(f"结果: {result}")

def test_recorder_timeout_config():
    """测试录制器超时配置"""
    print("\n=== 测试录制器超时配置 ===")
    
    # 创建录制器实例
    recorder = ScreenRecorder()
    
    print(f"文件I/O超时: {recorder.file_io_timeout}秒")
    print(f"数据库超时: {recorder.db_timeout}秒")
    print(f"窗口信息超时: {recorder.window_info_timeout}秒")

def test_file_operations():
    """测试文件操作超时"""
    print("\n=== 测试文件操作超时 ===")
    
    recorder = ScreenRecorder()
    
    # 创建临时文件进行测试
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
        tmp_path = tmp_file.name
    
    try:
        # 创建一个简单的PNG文件用于测试
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(tmp_path)
        
        print(f"测试文件: {tmp_path}")
        
        # 测试计算图像哈希
        print("测试计算图像哈希...")
        start_time = time.time()
        hash_result = recorder._calculate_image_hash(tmp_path)
        elapsed = time.time() - start_time
        print(f"哈希结果: {hash_result}, 耗时: {elapsed:.2f}秒")
        
        # 测试获取图像尺寸
        print("\n测试获取图像尺寸...")
        start_time = time.time()
        size_result = recorder._get_image_size(tmp_path)
        elapsed = time.time() - start_time
        print(f"尺寸结果: {size_result}, 耗时: {elapsed:.2f}秒")
        
        # 测试计算文件哈希
        print("\n测试计算文件哈希...")
        start_time = time.time()
        file_hash = recorder._calculate_file_hash(tmp_path)
        elapsed = time.time() - start_time
        print(f"文件哈希: {file_hash[:16]}..., 耗时: {elapsed:.2f}秒")
        
    finally:
        # 清理临时文件
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

def test_window_info():
    """测试窗口信息获取超时"""
    print("\n=== 测试窗口信息获取超时 ===")
    
    recorder = ScreenRecorder()
    
    print("测试获取窗口信息...")
    start_time = time.time()
    window_info = recorder._get_window_info()
    elapsed = time.time() - start_time
    print(f"窗口信息: {window_info}, 耗时: {elapsed:.2f}秒")

def main():
    """主函数"""
    print("LifeTrace 超时机制测试")
    print("=" * 50)
    
    try:
        # 测试超时装饰器
        test_timeout_decorator()
        
        # 测试录制器超时配置
        test_recorder_timeout_config()
        
        # 测试文件操作
        test_file_operations()
        
        # 测试窗口信息获取
        test_window_info()
        
        print("\n=== 测试完成 ===")
        print("请检查日志中是否有超时警告信息")
        
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()