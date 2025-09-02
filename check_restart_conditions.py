#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
心跳监控重启条件检查脚本
显示当前的心跳监控配置和重启条件
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config

def show_restart_conditions():
    """显示当前的重启条件和配置"""
    print("🔍 LifeTrace 心跳监控重启条件分析")
    print("=" * 50)
    
    print("\n📋 当前配置参数:")
    print(f"  • 心跳记录间隔: {config.heartbeat_interval} 秒")
    print(f"  • 心跳超时时间: {config.heartbeat_timeout} 秒")
    print(f"  • 心跳检查间隔: {config.heartbeat_check_interval} 秒")
    print(f"  • 最大重启次数: {config.heartbeat_max_restart_attempts} 次")
    print(f"  • 重启延迟时间: {config.heartbeat_restart_delay} 秒")
    print(f"  • 重启计数重置: {config.heartbeat_reset_count_interval} 秒")
    
    print("\n⚠️  重启触发条件:")
    print(f"  1. 服务心跳超时 (超过 {config.heartbeat_timeout} 秒无心跳)")
    print(f"  2. 服务进程意外停止")
    print(f"  3. 心跳文件解析失败或格式错误")
    
    print("\n🔄 重启机制说明:")
    print(f"  • 每 {config.heartbeat_check_interval} 秒检查一次所有服务心跳")
    print(f"  • 发现异常后立即尝试重启")
    print(f"  • 每个服务最多重启 {config.heartbeat_max_restart_attempts} 次")
    print(f"  • 重启间隔 {config.heartbeat_restart_delay} 秒")
    print(f"  • 每 {config.heartbeat_reset_count_interval/3600:.1f} 小时重置重启计数")
    
    print("\n💡 为什么服务容易重启:")
    print(f"  • 心跳超时时间较短 ({config.heartbeat_timeout} 秒)")
    print(f"  • 检查频率较高 (每 {config.heartbeat_check_interval} 秒)")
    print(f"  • 任何心跳异常都会触发重启")
    
    print("\n🛠️  优化建议:")
    if config.heartbeat_timeout <= 30:
        print(f"  • 考虑增加心跳超时时间 (当前 {config.heartbeat_timeout} 秒，建议 60-120 秒)")
    if config.heartbeat_check_interval <= 30:
        print(f"  • 考虑增加检查间隔 (当前 {config.heartbeat_check_interval} 秒，建议 60-300 秒)")
    
    print("\n📝 修改配置方法:")
    print("  编辑 config/default_config.yaml 文件中的 heartbeat 部分:")
    print("  ```yaml")
    print("  heartbeat:")
    print("    timeout: 60      # 增加超时时间")
    print("    check_interval: 120  # 增加检查间隔")
    print("  ```")
    
    print("\n" + "=" * 50)

if __name__ == '__main__':
    show_restart_conditions()