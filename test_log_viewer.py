#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志查看器功能
验证是否能正确读取用户主目录下的日志文件
"""

import requests
import json
from pathlib import Path

def test_log_viewer():
    """测试日志查看器API"""
    base_url = "http://localhost:8840"
    
    print("=== 测试日志查看器功能 ===")
    
    # 1. 测试获取日志文件列表
    print("\n1. 测试获取日志文件列表...")
    try:
        response = requests.get(f"{base_url}/api/logs/files")
        if response.status_code == 200:
            files = response.json()
            print(f"找到 {len(files)} 个日志文件:")
            for file in files:
                print(f"  - {file['name']} ({file['size']}) - 类别: {file['category']}")
                
            # 检查是否包含OCR日志
            ocr_files = [f for f in files if 'ocr' in f['name'].lower()]
            if ocr_files:
                print(f"\n找到 {len(ocr_files)} 个OCR相关日志文件:")
                for file in ocr_files:
                    print(f"  - {file['name']} ({file['size']})")
            else:
                print("\n未找到OCR相关日志文件")
        else:
            print(f"获取文件列表失败: {response.status_code}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 2. 测试读取OCR日志内容
    print("\n2. 测试读取OCR日志内容...")
    try:
        # 尝试读取core/lifetrace_ocr.log
        response = requests.get(f"{base_url}/api/logs/content?file=core/lifetrace_ocr.log")
        if response.status_code == 200:
            content = response.text
            lines = content.split('\n')
            print(f"OCR日志文件包含 {len(lines)} 行")
            if lines:
                print("最后几行内容:")
                for line in lines[-5:]:
                    if line.strip():
                        print(f"  {line}")
        else:
            print(f"读取OCR日志失败: {response.status_code}")
    except Exception as e:
        print(f"读取OCR日志失败: {e}")
    
    # 3. 检查用户主目录日志路径
    print("\n3. 检查日志路径...")
    user_logs_dir = Path.home() / ".lifetrace" / "logs"
    project_logs_dir = Path("logs")
    
    print(f"用户主目录日志路径: {user_logs_dir}")
    print(f"用户主目录日志存在: {user_logs_dir.exists()}")
    
    if user_logs_dir.exists():
        core_dir = user_logs_dir / "core"
        if core_dir.exists():
            log_files = list(core_dir.glob("*.log"))
            print(f"Core目录下的日志文件: {[f.name for f in log_files]}")
    
    print(f"\n项目日志路径: {project_logs_dir.absolute()}")
    print(f"项目日志存在: {project_logs_dir.exists()}")
    
    # 4. 测试日志查看器页面
    print("\n4. 测试日志查看器页面...")
    try:
        response = requests.get(f"{base_url}/logs")
        if response.status_code == 200:
            print("日志查看器页面访问成功")
            print(f"页面大小: {len(response.text)} 字符")
            
            # 检查页面是否包含自动刷新功能
            if "自动刷新 (1秒)" in response.text:
                print("✓ 页面包含1秒自动刷新功能")
            else:
                print("✗ 页面未包含1秒自动刷新功能")
                
            if "checked" in response.text:
                print("✓ 自动刷新默认启用")
            else:
                print("✗ 自动刷新未默认启用")
        else:
            print(f"访问日志查看器页面失败: {response.status_code}")
    except Exception as e:
        print(f"访问页面失败: {e}")
    
    print("\n=== 测试完成 ===")
    print("\n建议:")
    print("1. 在浏览器中访问 http://localhost:8840/logs")
    print("2. 检查是否能看到用户主目录下的日志文件")
    print("3. 验证自动刷新功能是否正常工作")
    print("4. 选择OCR日志文件查看内容")

if __name__ == '__main__':
    test_log_viewer()