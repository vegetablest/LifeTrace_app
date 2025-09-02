#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OCR日志器创建和文件写入
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.logging_config import setup_logging

def test_ocr_logger_creation():
    """测试OCR日志器创建"""
    print("=== 测试OCR日志器创建 ===")
    
    # 1. 初始化日志系统
    print("\n1. 初始化日志系统...")
    logger_manager = setup_logging(config)
    
    # 2. 获取OCR日志器
    print("\n2. 获取OCR日志器...")
    ocr_logger = logger_manager.get_ocr_logger()
    
    print(f"OCR日志器名称: {ocr_logger.name}")
    print(f"OCR日志级别: {ocr_logger.level}")
    print(f"OCR日志处理器数量: {len(ocr_logger.handlers)}")
    
    # 3. 检查日志处理器
    print("\n3. 检查日志处理器...")
    for i, handler in enumerate(ocr_logger.handlers):
        print(f"处理器 {i+1}: {type(handler).__name__}")
        if hasattr(handler, 'baseFilename'):
            print(f"  文件路径: {handler.baseFilename}")
            print(f"  文件存在: {os.path.exists(handler.baseFilename)}")
    
    # 4. 写入测试日志
    print("\n4. 写入测试日志...")
    ocr_logger.info("OCR日志器测试 - 信息日志")
    ocr_logger.warning("OCR日志器测试 - 警告日志")
    ocr_logger.error("OCR日志器测试 - 错误日志")
    
    # 5. 检查日志文件是否创建
    print("\n5. 检查日志文件...")
    expected_log_file = os.path.join(config.base_dir, 'logs', 'core', 'lifetrace_ocr.log')
    print(f"期望的日志文件路径: {expected_log_file}")
    print(f"日志文件存在: {os.path.exists(expected_log_file)}")
    
    if os.path.exists(expected_log_file):
        file_size = os.path.getsize(expected_log_file)
        print(f"日志文件大小: {file_size} 字节")
        
        # 读取日志内容
        try:
            with open(expected_log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n日志文件内容:")
                print(content)
        except Exception as e:
            print(f"读取日志文件失败: {e}")
    else:
        print("日志文件未创建，可能的原因:")
        print("1. 日志目录不存在")
        print("2. 权限问题")
        print("3. 日志配置问题")
        
        # 检查日志目录
        log_dir = os.path.join(config.base_dir, 'logs', 'core')
        print(f"\n日志目录: {log_dir}")
        print(f"日志目录存在: {os.path.exists(log_dir)}")
        
        if not os.path.exists(log_dir):
            print("尝试创建日志目录...")
            try:
                os.makedirs(log_dir, exist_ok=True)
                print("日志目录创建成功")
                
                # 重新写入日志
                ocr_logger.info("重新测试 - OCR日志器")
                print(f"重新检查日志文件: {os.path.exists(expected_log_file)}")
            except Exception as e:
                print(f"创建日志目录失败: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    test_ocr_logger_creation()