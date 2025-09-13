#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
路径规范验证脚本
验证所有路径配置是否符合规范
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.logging_config import setup_logging

def verify_path_compliance():
    """验证路径规范符合性"""
    print("=== LifeTrace 路径规范验证 ===")
    print()
    
    # 1. 验证配置文件路径
    print("1. 配置文件路径规范检查:")
    config_path = config.config_path
    print(f"   配置文件路径: {config_path}")
    config_compliant = 'config' + os.sep + 'config.yaml' in config_path
    print(f"   符合规范: {config_compliant} ✓" if config_compliant else f"   符合规范: {config_compliant} ✗")
    print()
    
    # 2. 验证数据文件路径
    print("2. 数据文件路径规范检查:")
    base_dir = config.base_dir
    database_path = config.database_path
    print(f"   基础目录: {base_dir}")
    print(f"   数据库路径: {database_path}")
    data_compliant = base_dir.endswith('data') and ('data' + os.sep + 'lifetrace.db' in database_path or 'data/lifetrace.db' in database_path)
    print(f"   符合规范: {data_compliant} ✓" if data_compliant else f"   符合规范: {data_compliant} ✗")
    print()
    
    # 3. 验证截图目录路径
    print("3. 截图目录路径规范检查:")
    screenshots_dir = config.screenshots_dir
    print(f"   截图目录: {screenshots_dir}")
    screenshots_compliant = 'data' + os.sep + 'screenshots' in screenshots_dir or 'data/screenshots' in screenshots_dir
    print(f"   符合规范: {screenshots_compliant} ✓" if screenshots_compliant else f"   符合规范: {screenshots_compliant} ✗")
    print()
    
    # 4. 验证日志目录路径
    print("4. 日志目录路径规范检查:")
    heartbeat_log_dir = config.heartbeat_log_dir
    print(f"   心跳日志目录: {heartbeat_log_dir}")
    log_compliant = 'data' + os.sep + 'logs' in heartbeat_log_dir or 'data/logs' in heartbeat_log_dir
    print(f"   符合规范: {log_compliant} ✓" if log_compliant else f"   符合规范: {log_compliant} ✗")
    print()
    
    # 5. 测试日志系统目录创建
    print("5. 日志系统目录创建测试:")
    try:
        logger_manager = setup_logging(config)
        status = logger_manager.get_log_status()
        log_dir = status['log_directory']
        print(f"   日志目录: {log_dir}")
        print(f"   目录存在: {os.path.exists(log_dir)} ✓" if os.path.exists(log_dir) else f"   目录存在: {os.path.exists(log_dir)} ✗")
        
        if os.path.exists(log_dir):
            subdirs = [d for d in os.listdir(log_dir) if os.path.isdir(os.path.join(log_dir, d))]
            print(f"   子目录: {subdirs}")
            expected_subdirs = ['core', 'sync', 'debug']
            subdirs_compliant = all(subdir in subdirs for subdir in expected_subdirs)
            print(f"   子目录完整: {subdirs_compliant} ✓" if subdirs_compliant else f"   子目录完整: {subdirs_compliant} ✗")
    except Exception as e:
        print(f"   日志系统测试失败: {e} ✗")
    print()
    
    # 总结
    all_compliant = config_compliant and data_compliant and screenshots_compliant and log_compliant
    print("=== 验证结果总结 ===")
    print(f"所有路径规范检查: {'通过 ✓' if all_compliant else '失败 ✗'}")
    
    if all_compliant:
        print("\n🎉 恭喜！所有路径配置都符合规范要求：")
        print("   ✓ 配置文件从 config/ 目录读取")
        print("   ✓ 数据文件存储在 data/ 目录")
        print("   ✓ 日志文件存储在 data/logs/ 目录")
        print("   ✓ 截图文件存储在 data/screenshots/ 目录")
    else:
        print("\n❌ 仍有部分路径配置不符合规范，请检查上述详细信息。")
    
    return all_compliant

if __name__ == '__main__':
    verify_path_compliance()