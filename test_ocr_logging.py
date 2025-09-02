#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR日志配置测试脚本
验证OCR服务的日志记录是否正常工作
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.logging_config import setup_logging
from lifetrace_backend.simple_ocr import SimpleOCRProcessor

def test_ocr_logging():
    """测试OCR日志配置"""
    print("=== OCR日志配置测试 ===")
    
    # 1. 测试日志系统初始化
    print("\n1. 初始化日志系统...")
    logger_manager = setup_logging(config)
    ocr_logger = logger_manager.get_ocr_logger()
    
    print(f"OCR日志器名称: {ocr_logger.name}")
    print(f"OCR日志级别: {ocr_logger.level}")
    print(f"OCR日志处理器数量: {len(ocr_logger.handlers)}")
    
    # 2. 测试日志输出
    print("\n2. 测试日志输出...")
    ocr_logger.info("这是一条OCR信息日志")
    ocr_logger.warning("这是一条OCR警告日志")
    ocr_logger.error("这是一条OCR错误日志")
    ocr_logger.debug("这是一条OCR调试日志")
    
    # 3. 检查日志文件
    print("\n3. 检查日志文件...")
    log_dir = os.path.join(config.base_dir, 'logs', 'core')
    ocr_log_file = os.path.join(log_dir, 'lifetrace_ocr.log')
    
    print(f"日志目录: {log_dir}")
    print(f"OCR日志文件: {ocr_log_file}")
    print(f"日志文件存在: {os.path.exists(ocr_log_file)}")
    
    if os.path.exists(ocr_log_file):
        file_size = os.path.getsize(ocr_log_file)
        print(f"日志文件大小: {file_size} 字节")
        
        # 读取最后几行日志
        try:
            with open(ocr_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"\n最近的日志记录 (最后{min(5, len(lines))}行):")
                    for line in lines[-5:]:
                        print(f"  {line.strip()}")
                else:
                    print("日志文件为空")
        except Exception as e:
            print(f"读取日志文件失败: {e}")
    
    # 4. 测试OCR处理器日志
    print("\n4. 测试OCR处理器日志...")
    ocr_processor = SimpleOCRProcessor()
    
    # 模拟一些OCR处理日志
    ocr_logger.info("开始OCR处理测试")
    ocr_logger.info(f"OCR引擎可用: {ocr_processor.is_available()}")
    ocr_logger.info("OCR处理测试完成")
    
    # 5. 检查日志配置
    print("\n5. 检查日志配置...")
    print(f"配置文件路径: {config.config_path}")
    
    # 检查日志相关配置
    log_config = config.get('logging', {})
    print(f"日志配置: {log_config}")
    
    ocr_log_level = config.get('logging.ocr_log_level', 'INFO')
    print(f"OCR日志级别配置: {ocr_log_level}")
    
    print("\n=== 测试完成 ===")
    print("\n建议:")
    print("1. 检查日志文件是否有新的记录")
    print("2. 如果没有日志输出，检查日志级别配置")
    print("3. 确保OCR服务使用了正确的logger实例")

if __name__ == '__main__':
    test_ocr_logging()