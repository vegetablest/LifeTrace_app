#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心跳系统演示脚本

展示如何在实际应用中使用心跳监控和自动重启功能
"""

import os
import sys
import time
import threading
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.heartbeat import HeartbeatLogger, HeartbeatMonitor
from lifetrace_backend.config import config


class DemoService:
    """演示服务类"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.heartbeat_logger = HeartbeatLogger(service_name)
        self.running = False
        self.work_thread = None
        
    def start(self):
        """启动服务"""
        if self.running:
            return
            
        print(f"🚀 启动服务: {self.service_name}")
        self.running = True
        
        # 启动心跳记录
        self.heartbeat_logger.start_heartbeat()
        
        # 启动工作线程
        self.work_thread = threading.Thread(target=self._work_loop, daemon=True)
        self.work_thread.start()
        
    def stop(self):
        """停止服务"""
        if not self.running:
            return
            
        print(f"🛑 停止服务: {self.service_name}")
        self.running = False
        
        # 停止心跳记录
        self.heartbeat_logger.stop_heartbeat()
        
        # 等待工作线程结束
        if self.work_thread and self.work_thread.is_alive():
            self.work_thread.join(timeout=2)
    
    def _work_loop(self):
        """工作循环"""
        work_count = 0
        while self.running:
            try:
                # 模拟工作
                work_count += 1
                
                # 记录带有工作状态的心跳
                self.heartbeat_logger.record_heartbeat({
                    'work_count': work_count,
                    'status': 'working',
                    'memory_usage': f"{os.getpid()}"
                })
                
                # 模拟工作耗时
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ 服务 {self.service_name} 工作异常: {e}")
                # 记录错误状态的心跳
                self.heartbeat_logger.record_heartbeat({
                    'status': 'error',
                    'error': str(e)
                })
                time.sleep(1)


class ServiceMonitorDemo:
    """服务监控演示类"""
    
    def __init__(self):
        self.monitor = HeartbeatMonitor()
        self.services = {}
        
        # 设置回调函数
        self.monitor.on_service_timeout = self._on_service_timeout
        self.monitor.on_service_recovered = self._on_service_recovered
        
    def start_monitoring(self):
        """启动监控"""
        print("🔍 启动心跳监控")
        self.monitor.start_monitoring()
        
    def stop_monitoring(self):
        """停止监控"""
        print("🔍 停止心跳监控")
        self.monitor.stop_monitoring()
        
    def add_service(self, service_name: str):
        """添加服务"""
        if service_name not in self.services:
            service = DemoService(service_name)
            self.services[service_name] = service
            service.start()
            print(f"➕ 添加服务: {service_name}")
        
    def remove_service(self, service_name: str):
        """移除服务"""
        if service_name in self.services:
            service = self.services.pop(service_name)
            service.stop()
            print(f"➖ 移除服务: {service_name}")
    
    def _on_service_timeout(self, service_name: str, timeout_duration: float):
        """服务超时回调"""
        print(f"⚠️ 服务超时: {service_name} (超时 {timeout_duration:.1f} 秒)")
        
        # 尝试重启服务
        if service_name in self.services:
            print(f"🔄 尝试重启服务: {service_name}")
            service = self.services[service_name]
            service.stop()
            time.sleep(1)
            service.start()
    
    def _on_service_recovered(self, service_name: str):
        """服务恢复回调"""
        print(f"✅ 服务恢复: {service_name}")
    
    def get_status_report(self):
        """获取状态报告"""
        print("\n📊 服务状态报告:")
        print("=" * 50)
        
        all_status = self.monitor.get_all_status()
        
        if not all_status:
            print("没有检测到任何服务")
            return
            
        for service_name, status in all_status.items():
            status_emoji = {
                'alive': '✅',
                'timeout': '❌',
                'no_heartbeat': '⚪'
            }.get(status['status'], '❓')
            
            print(f"{status_emoji} {service_name}: {status['status']}")
            
            if status['last_heartbeat']:
                print(f"   最后心跳: {status['last_heartbeat'].strftime('%H:%M:%S')}")
            
            if status['timeout_duration'] > 0:
                print(f"   超时时长: {status['timeout_duration']:.1f} 秒")
            
            print()
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        
        # 停止所有服务
        for service_name in list(self.services.keys()):
            self.remove_service(service_name)
        
        # 停止监控
        self.stop_monitoring()


def main():
    """主演示函数"""
    print("心跳系统演示")
    print("=" * 50)
    print(f"心跳间隔: {config.heartbeat_interval} 秒")
    print(f"心跳超时: {config.heartbeat_timeout} 秒")
    print(f"检查间隔: {config.heartbeat_check_interval} 秒")
    print()
    
    demo = ServiceMonitorDemo()
    
    try:
        # 启动监控
        demo.start_monitoring()
        
        # 添加一些演示服务
        demo.add_service("demo_service_1")
        demo.add_service("demo_service_2")
        
        print("\n⏰ 运行 30 秒，观察心跳状态...")
        
        # 运行一段时间，观察心跳状态
        for i in range(6):
            time.sleep(5)
            demo.get_status_report()
        
        # 模拟服务故障
        print("\n💥 模拟服务故障 - 停止 demo_service_1")
        demo.remove_service("demo_service_1")
        
        print("\n⏰ 等待 40 秒，观察超时检测...")
        for i in range(8):
            time.sleep(5)
            demo.get_status_report()
        
    except KeyboardInterrupt:
        print("\n⚠️ 演示被用户中断")
    
    finally:
        demo.cleanup()
        print("\n🎉 演示结束")


if __name__ == '__main__':
    main()