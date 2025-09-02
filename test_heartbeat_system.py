#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心跳系统测试脚本

测试心跳记录、监控和自动重启功能
"""

import os
import sys
import time
import threading
import subprocess
from pathlib import Path
import json
from datetime import datetime, timedelta

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.heartbeat import HeartbeatLogger, HeartbeatMonitor
from lifetrace_backend.config import config


class HeartbeatSystemTester:
    """心跳系统测试器"""
    
    def __init__(self):
        self.test_results = []
        self.test_service_name = "test_service"
        self.heartbeat_logger = None
        self.heartbeat_monitor = None
        
    def log_test_result(self, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {test_name}: {message}")
    
    def test_heartbeat_logger_creation(self):
        """测试心跳记录器创建"""
        try:
            self.heartbeat_logger = HeartbeatLogger(self.test_service_name)
            
            # 检查日志目录是否创建
            log_dir_exists = self.heartbeat_logger.log_dir.exists()
            
            # 检查配置是否正确加载
            config_loaded = (
                self.heartbeat_logger.heartbeat_interval == config.heartbeat_interval and
                self.heartbeat_logger.max_log_size == config.heartbeat_log_max_size_mb * 1024 * 1024
            )
            
            if log_dir_exists and config_loaded:
                self.log_test_result("心跳记录器创建", True, "成功创建并加载配置")
            else:
                self.log_test_result("心跳记录器创建", False, f"目录存在: {log_dir_exists}, 配置加载: {config_loaded}")
                
        except Exception as e:
            self.log_test_result("心跳记录器创建", False, f"异常: {str(e)}")
    
    def test_heartbeat_recording(self):
        """测试心跳记录功能"""
        try:
            if not self.heartbeat_logger:
                self.log_test_result("心跳记录", False, "心跳记录器未初始化")
                return
            
            # 记录几次心跳
            test_data = {'status': 'testing', 'count': 1}
            self.heartbeat_logger.record_heartbeat(test_data)
            
            time.sleep(1)
            
            test_data['count'] = 2
            self.heartbeat_logger.record_heartbeat(test_data)
            
            # 检查日志文件是否存在且有内容
            log_file = self.heartbeat_logger.heartbeat_file
            if log_file.exists() and log_file.stat().st_size > 0:
                self.log_test_result("心跳记录", True, f"成功记录心跳到 {log_file}")
            else:
                self.log_test_result("心跳记录", False, "心跳日志文件不存在或为空")
                
        except Exception as e:
            self.log_test_result("心跳记录", False, f"异常: {str(e)}")
    
    def test_heartbeat_auto_recording(self):
        """测试自动心跳记录"""
        try:
            if not self.heartbeat_logger:
                self.log_test_result("自动心跳记录", False, "心跳记录器未初始化")
                return
            
            # 启动自动心跳
            self.heartbeat_logger.start_heartbeat()
            
            # 等待几秒让心跳记录
            time.sleep(3)
            
            # 停止心跳
            self.heartbeat_logger.stop_heartbeat()
            
            # 检查日志文件内容
            log_file = self.heartbeat_logger.heartbeat_file
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 应该有多行心跳记录
                    lines = content.strip().split('\n')
                    if len(lines) >= 2:  # 至少应该有2-3次心跳
                        self.log_test_result("自动心跳记录", True, f"记录了 {len(lines)} 次心跳")
                    else:
                        self.log_test_result("自动心跳记录", False, f"心跳记录次数不足: {len(lines)}")
            else:
                self.log_test_result("自动心跳记录", False, "心跳日志文件不存在")
                
        except Exception as e:
            self.log_test_result("自动心跳记录", False, f"异常: {str(e)}")
    
    def test_heartbeat_monitor_creation(self):
        """测试心跳监控器创建"""
        try:
            self.heartbeat_monitor = HeartbeatMonitor()
            
            # 检查配置是否正确加载
            config_loaded = (
                self.heartbeat_monitor.heartbeat_timeout == config.heartbeat_timeout and
                self.heartbeat_monitor.check_interval == config.heartbeat_check_interval
            )
            
            if config_loaded:
                self.log_test_result("心跳监控器创建", True, "成功创建并加载配置")
            else:
                self.log_test_result("心跳监控器创建", False, "配置加载失败")
                
        except Exception as e:
            self.log_test_result("心跳监控器创建", False, f"异常: {str(e)}")
    
    def test_heartbeat_monitoring(self):
        """测试心跳监控功能"""
        try:
            if not self.heartbeat_monitor:
                self.log_test_result("心跳监控", False, "心跳监控器未初始化")
                return
            
            # 创建一个测试服务的心跳
            test_logger = HeartbeatLogger("monitor_test_service")
            test_logger.record_heartbeat({'status': 'running'})
            
            # 启动监控
            self.heartbeat_monitor.start_monitoring()
            
            # 等待监控器完成至少一次检查循环，但不超过心跳超时时间
            wait_time = min(5, self.heartbeat_monitor.check_interval + 1)
            time.sleep(wait_time)
            
            # 手动触发一次检查以确保状态更新
            self.heartbeat_monitor._check_all_services()
            
            # 检查服务状态
            is_alive = self.heartbeat_monitor.is_service_alive("monitor_test_service")
            
            # 停止监控
            self.heartbeat_monitor.stop_monitoring()
            
            if is_alive:
                self.log_test_result("心跳监控", True, "成功检测到服务心跳")
            else:
                # 获取详细状态信息用于调试
                status = self.heartbeat_monitor.get_service_status("monitor_test_service")
                self.log_test_result("心跳监控", False, f"未能检测到服务心跳，状态: {status}")
                
        except Exception as e:
            self.log_test_result("心跳监控", False, f"异常: {str(e)}")
    
    def test_log_rotation(self):
        """测试日志轮转功能"""
        try:
            if not self.heartbeat_logger:
                self.log_test_result("日志轮转", False, "心跳记录器未初始化")
                return
            
            # 获取当前日志信息
            log_info_before = self.heartbeat_logger.get_log_info()
            
            # 强制轮转日志
            self.heartbeat_logger._rotate_logs()
            
            # 记录新的心跳
            self.heartbeat_logger.record_heartbeat({'status': 'after_rotation'})
            
            # 获取轮转后的日志信息
            log_info_after = self.heartbeat_logger.get_log_info()
            
            # 检查是否有备份文件
            backup_files = log_info_after.get('backup_files', [])
            
            if len(backup_files) > 0:
                self.log_test_result("日志轮转", True, f"成功创建备份文件: {backup_files}")
            else:
                self.log_test_result("日志轮转", False, "未创建备份文件")
                
        except Exception as e:
            self.log_test_result("日志轮转", False, f"异常: {str(e)}")
    
    def test_config_loading(self):
        """测试配置加载"""
        try:
            # 检查心跳配置是否正确加载
            config_checks = [
                (config.heartbeat_enabled, "心跳启用"),
                (config.heartbeat_interval > 0, "心跳间隔"),
                (config.heartbeat_timeout > 0, "心跳超时"),
                (config.heartbeat_log_dir, "日志目录"),
                (config.heartbeat_log_max_size_mb > 0, "日志最大大小"),
                (config.heartbeat_max_restart_attempts > 0, "最大重启次数")
            ]
            
            failed_checks = []
            for check, name in config_checks:
                if not check:
                    failed_checks.append(name)
            
            if not failed_checks:
                self.log_test_result("配置加载", True, "所有心跳配置正确加载")
            else:
                self.log_test_result("配置加载", False, f"配置检查失败: {', '.join(failed_checks)}")
                
        except Exception as e:
            self.log_test_result("配置加载", False, f"异常: {str(e)}")
    
    def cleanup(self):
        """清理测试资源"""
        try:
            # 停止心跳记录器
            if self.heartbeat_logger:
                self.heartbeat_logger.stop_heartbeat()
            
            # 停止心跳监控器
            if self.heartbeat_monitor:
                self.heartbeat_monitor.stop_monitoring()
            
            # 清理测试日志文件
            test_log_dir = Path(config.heartbeat_log_dir)
            if test_log_dir.exists():
                for log_file in test_log_dir.glob(f"{self.test_service_name}*"):
                    try:
                        log_file.unlink()
                    except:
                        pass
                
                for log_file in test_log_dir.glob("monitor_test_service*"):
                    try:
                        log_file.unlink()
                    except:
                        pass
            
            print("\n🧹 测试资源清理完成")
            
        except Exception as e:
            print(f"⚠️ 清理过程中出现异常: {e}")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始心跳系统测试...\n")
        
        # 运行测试
        self.test_config_loading()
        self.test_heartbeat_logger_creation()
        self.test_heartbeat_recording()
        self.test_heartbeat_auto_recording()
        self.test_heartbeat_monitor_creation()
        self.test_heartbeat_monitoring()
        self.test_log_rotation()
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"\n📊 测试结果统计:")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        # 清理资源
        self.cleanup()
        
        return failed_tests == 0


def main():
    """主函数"""
    print("心跳系统测试脚本")
    print("=" * 50)
    
    tester = HeartbeatSystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 所有测试通过！心跳系统工作正常。")
            return 0
        else:
            print("\n💥 部分测试失败，请检查心跳系统配置。")
            return 1
            
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        tester.cleanup()
        return 1
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        tester.cleanup()
        return 1


if __name__ == '__main__':
    exit(main())