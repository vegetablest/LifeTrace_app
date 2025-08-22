#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础同步功能测试脚本

简单测试文件监控和一致性检查的基本功能。
"""

import os
import sys
import time
from pathlib import Path
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace.config import config
from lifetrace.sync_service import sync_service_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def test_sync_service_status():
    """测试同步服务状态"""
    logger.info("=== 测试同步服务状态 ===")
    
    try:
        # 获取服务状态
        status = sync_service_manager.get_status()
        
        logger.info(f"同步服务管理器状态:")
        logger.info(f"  运行状态: {status.get('manager_running', False)}")
        logger.info(f"  启动时间: {status.get('start_time', 'N/A')}")
        logger.info(f"  统计信息: {status.get('stats', {})}")
        
        # 显示各个服务状态
        services = status.get('services', {})
        logger.info(f"  服务数量: {len(services)}")
        
        for service_name, service_status in services.items():
            logger.info(f"  {service_name}: {service_status.get('running', False)}")
        
        return True
        
    except Exception as e:
        logger.error(f"获取同步服务状态失败: {e}")
        return False

def test_force_consistency_check():
    """测试强制一致性检查"""
    logger.info("\n=== 测试强制一致性检查 ===")
    
    try:
        # 执行强制一致性检查
        result = sync_service_manager.force_consistency_check()
        
        logger.info(f"一致性检查结果:")
        if 'success' in result:
            logger.info(f"  执行状态: {'成功' if result['success'] else '失败'}")
        
        if 'result' in result:
            check_result = result['result']
            logger.info(f"  检查时间: {check_result.get('check_time', 'N/A')}")
            logger.info(f"  孤立数据库记录: {check_result.get('orphaned_db_records', 0)}")
            logger.info(f"  孤立文件: {check_result.get('orphaned_files', 0)}")
            logger.info(f"  清理记录数: {check_result.get('cleaned_records', 0)}")
        
        if 'error' in result:
            logger.warning(f"  错误信息: {result['error']}")
        
        return True
        
    except Exception as e:
        logger.error(f"强制一致性检查失败: {e}")
        return False

def test_config_values():
    """测试配置值"""
    logger.info("\n=== 测试配置值 ===")
    
    try:
        logger.info(f"配置信息:")
        logger.info(f"  基础目录: {config.base_dir}")
        logger.info(f"  截图目录: {config.screenshots_dir}")
        logger.info(f"  数据库路径: {config.database_path}")
        
        # 检查同步服务配置
        sync_configs = [
            ('enable_file_monitor', '文件监控启用'),
            ('enable_consistency_check', '一致性检查启用'),
            ('file_monitor_delay', '文件监控延迟'),
            ('consistency_check_interval', '一致性检查间隔'),
            ('sync_service_log_level', '日志级别')
        ]
        
        logger.info(f"  同步服务配置:")
        for attr_name, display_name in sync_configs:
            try:
                value = getattr(config, attr_name, 'N/A')
                logger.info(f"    {display_name}: {value}")
            except Exception as e:
                logger.warning(f"    {display_name}: 获取失败 ({e})")
        
        # 检查目录是否存在
        screenshots_dir = Path(config.screenshots_dir)
        logger.info(f"  截图目录存在: {screenshots_dir.exists()}")
        
        if screenshots_dir.exists():
            # 统计截图文件数量
            image_files = list(screenshots_dir.glob('*.png')) + \
                         list(screenshots_dir.glob('*.jpg')) + \
                         list(screenshots_dir.glob('*.jpeg'))
            logger.info(f"  截图文件数量: {len(image_files)}")
        
        return True
        
    except Exception as e:
        logger.error(f"测试配置值失败: {e}")
        return False

def test_service_restart():
    """测试服务重启功能"""
    logger.info("\n=== 测试服务重启功能 ===")
    
    try:
        # 获取当前状态
        status_before = sync_service_manager.get_status()
        logger.info(f"重启前状态: {status_before.get('manager_running', False)}")
        
        if status_before.get('manager_running', False):
            # 尝试重启所有服务
            logger.info("尝试重启同步服务...")
            sync_service_manager.restart_all()
            
            # 等待重启完成
            time.sleep(2)
            
            # 获取重启后状态
            status_after = sync_service_manager.get_status()
            logger.info(f"重启后状态: {status_after.get('manager_running', False)}")
            
            # 比较统计信息
            stats_before = status_before.get('stats', {})
            stats_after = status_after.get('stats', {})
            
            logger.info(f"统计信息变化:")
            logger.info(f"  操作次数: {stats_before.get('total_operations', 0)} -> {stats_after.get('total_operations', 0)}")
            logger.info(f"  错误次数: {stats_before.get('errors', 0)} -> {stats_after.get('errors', 0)}")
            
        else:
            logger.info("同步服务未运行，跳过重启测试")
        
        return True
        
    except Exception as e:
        logger.error(f"测试服务重启失败: {e}")
        return False

def main():
    """主函数"""
    print("开始基础同步功能测试")
    logger.info("开始基础同步功能测试")
    
    tests = [
        ("配置值测试", test_config_values),
        ("同步服务状态测试", test_sync_service_status),
        ("强制一致性检查测试", test_force_consistency_check),
        ("服务重启测试", test_service_restart)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n开始执行: {test_name}")
        logger.info(f"\n开始执行: {test_name}")
        try:
            if test_func():
                print(f"✓ {test_name} 通过")
                logger.info(f"✓ {test_name} 通过")
                passed += 1
            else:
                print(f"✗ {test_name} 失败")
                logger.error(f"✗ {test_name} 失败")
        except Exception as e:
            print(f"✗ {test_name} 异常: {e}")
            logger.error(f"✗ {test_name} 异常: {e}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    logger.info(f"\n=== 测试结果 ===")
    logger.info(f"通过: {passed}/{total}")
    
    if passed == total:
        print("所有测试通过！")
        logger.info("所有测试通过！")
        return 0
    else:
        print(f"有 {total - passed} 个测试失败")
        logger.warning(f"有 {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())