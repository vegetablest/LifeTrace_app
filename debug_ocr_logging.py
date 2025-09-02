#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OCR日志文件创建问题
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.logging_config import setup_logging, LifeTraceLogger

def debug_ocr_logging():
    """调试OCR日志问题"""
    print("=== 调试OCR日志文件创建问题 ===")
    
    # 1. 检查配置
    print("\n1. 检查配置...")
    print(f"项目根目录: {config.base_dir}")
    print(f"配置文件路径: {config.config_path}")
    
    logging_config = config.get('logging', {})
    print(f"文件日志启用: {logging_config.get('enable_file_logging', False)}")
    print(f"OCR日志级别: {logging_config.get('ocr_log_level', 'INFO')}")
    
    # 2. 检查日志目录
    print("\n2. 检查日志目录...")
    log_base_dir = os.path.join(config.base_dir, 'logs')
    log_core_dir = os.path.join(log_base_dir, 'core')
    
    print(f"日志基础目录: {log_base_dir}")
    print(f"日志基础目录存在: {os.path.exists(log_base_dir)}")
    print(f"Core日志目录: {log_core_dir}")
    print(f"Core日志目录存在: {os.path.exists(log_core_dir)}")
    
    # 3. 手动创建日志管理器
    print("\n3. 创建日志管理器...")
    logger_manager = LifeTraceLogger(config)
    
    print(f"日志管理器基础目录: {logger_manager.log_dir}")
    print(f"日志管理器配置: {logger_manager.config}")
    
    # 4. 手动创建OCR日志器
    print("\n4. 创建OCR日志器...")
    
    # 确保目录存在
    os.makedirs(log_core_dir, exist_ok=True)
    print(f"Core目录创建后存在: {os.path.exists(log_core_dir)}")
    
    # 获取OCR日志器
    ocr_logger = logger_manager.get_ocr_logger()
    
    print(f"OCR日志器: {ocr_logger}")
    print(f"OCR日志器名称: {ocr_logger.name}")
    print(f"OCR日志器级别: {ocr_logger.level}")
    print(f"OCR日志器处理器数量: {len(ocr_logger.handlers)}")
    
    # 5. 检查处理器详情
    print("\n5. 检查日志处理器...")
    for i, handler in enumerate(ocr_logger.handlers):
        print(f"处理器 {i+1}: {type(handler).__name__}")
        print(f"  级别: {handler.level}")
        print(f"  格式器: {handler.formatter}")
        
        if hasattr(handler, 'baseFilename'):
            print(f"  文件路径: {handler.baseFilename}")
            print(f"  文件目录: {os.path.dirname(handler.baseFilename)}")
            print(f"  目录存在: {os.path.exists(os.path.dirname(handler.baseFilename))}")
            print(f"  文件存在: {os.path.exists(handler.baseFilename)}")
            
            # 尝试写入测试
            try:
                with open(handler.baseFilename, 'a', encoding='utf-8') as f:
                    f.write("# 手动测试写入\n")
                print(f"  手动写入成功")
                print(f"  写入后文件存在: {os.path.exists(handler.baseFilename)}")
            except Exception as e:
                print(f"  手动写入失败: {e}")
    
    # 6. 测试日志写入
    print("\n6. 测试日志写入...")
    test_messages = [
        ("info", "测试信息日志"),
        ("warning", "测试警告日志"),
        ("error", "测试错误日志")
    ]
    
    for level, message in test_messages:
        try:
            getattr(ocr_logger, level)(message)
            print(f"  {level.upper()} 日志写入成功")
        except Exception as e:
            print(f"  {level.upper()} 日志写入失败: {e}")
    
    # 7. 强制刷新处理器
    print("\n7. 强制刷新处理器...")
    for handler in ocr_logger.handlers:
        try:
            handler.flush()
            print(f"  {type(handler).__name__} 刷新成功")
        except Exception as e:
            print(f"  {type(handler).__name__} 刷新失败: {e}")
    
    # 8. 最终检查
    print("\n8. 最终检查...")
    expected_log_file = os.path.join(log_core_dir, 'lifetrace_ocr.log')
    print(f"期望日志文件: {expected_log_file}")
    print(f"文件存在: {os.path.exists(expected_log_file)}")
    
    if os.path.exists(expected_log_file):
        file_size = os.path.getsize(expected_log_file)
        print(f"文件大小: {file_size} 字节")
        
        if file_size > 0:
            try:
                with open(expected_log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"\n文件内容:")
                    print(content)
            except Exception as e:
                print(f"读取文件失败: {e}")
    
    # 9. 列出所有日志文件
    print("\n9. 列出所有日志文件...")
    for root, dirs, files in os.walk(log_base_dir):
        for file in files:
            if file.endswith('.log'):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                print(f"  {file_path} ({file_size} 字节)")
    
    print("\n=== 调试完成 ===")

if __name__ == '__main__':
    debug_ocr_logging()