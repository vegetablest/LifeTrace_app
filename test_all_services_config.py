#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有服务模块的配置加载情况
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_config_in_modules():
    """测试各个模块中的配置加载"""
    print("=== LifeTrace 所有服务模块配置加载测试 ===")
    print()
    
    # 测试基础配置模块
    print("🔧 测试基础配置模块...")
    try:
        from lifetrace_backend.config import config
        print(f"✅ 配置模块加载成功")
        print(f"   配置文件路径: {config.config_path}")
        print(f"   配置文件存在: {Path(config.config_path).exists()}")
        print(f"   心跳超时时间: {config.heartbeat_timeout} 秒")
        print(f"   心跳检查间隔: {config.heartbeat_check_interval} 秒")
    except Exception as e:
        print(f"❌ 配置模块加载失败: {e}")
        return False
    
    print()
    
    # 测试各个服务模块
    modules_to_test = [
        ('recorder', 'lifetrace_backend.recorder'),
        ('processor', 'lifetrace_backend.processor'), 
        ('server', 'lifetrace_backend.server'),
        ('sync_service', 'lifetrace_backend.sync_service'),
        ('heartbeat', 'lifetrace_backend.heartbeat'),
        ('file_monitor', 'lifetrace_backend.file_monitor'),
        ('logging_config', 'lifetrace_backend.logging_config'),
        ('commands', 'lifetrace_backend.commands')
    ]
    
    config_issues = []
    
    for module_name, module_path in modules_to_test:
        print(f"🔍 测试 {module_name} 模块...")
        try:
            # 动态导入模块
            module = __import__(module_path, fromlist=[''])
            
            # 检查模块是否有config引用
            if hasattr(module, 'config'):
                module_config = getattr(module, 'config')
                print(f"   ✅ {module_name} 模块配置加载成功")
                print(f"      配置文件路径: {module_config.config_path}")
                print(f"      心跳超时: {module_config.heartbeat_timeout} 秒")
                
                # 检查是否使用了正确的配置文件
                if 'default_config.yaml' not in module_config.config_path:
                    config_issues.append(f"{module_name}: 使用了错误的配置文件路径")
                elif module_config.heartbeat_timeout != 180:
                    config_issues.append(f"{module_name}: 心跳超时时间不正确 ({module_config.heartbeat_timeout}秒)")
            else:
                print(f"   ℹ️  {module_name} 模块未直接使用config对象")
                
        except ImportError as e:
            print(f"   ⚠️  {module_name} 模块导入失败: {e}")
        except Exception as e:
            print(f"   ❌ {module_name} 模块测试失败: {e}")
            config_issues.append(f"{module_name}: 配置测试异常 - {e}")
    
    print()
    print("=== 配置问题汇总 ===")
    if config_issues:
        print("❌ 发现以下配置问题:")
        for issue in config_issues:
            print(f"   • {issue}")
    else:
        print("✅ 所有模块配置加载正常")
    
    print()
    print("=== 详细配置信息 ===")
    print(f"当前使用的配置文件: {config.config_path}")
    print(f"心跳监控配置:")
    print(f"  - 启用状态: {config.heartbeat_enabled}")
    print(f"  - 记录间隔: {config.heartbeat_interval} 秒")
    print(f"  - 超时时间: {config.heartbeat_timeout} 秒")
    print(f"  - 检查间隔: {config.heartbeat_check_interval} 秒")
    print(f"  - 日志目录: {config.heartbeat_log_dir}")
    print(f"自动重启配置:")
    print(f"  - 启用状态: {config.heartbeat_auto_restart_enabled}")
    print(f"  - 最大重试: {config.heartbeat_max_restart_attempts} 次")
    print(f"  - 重启延迟: {config.heartbeat_restart_delay} 秒")
    
    print()
    print("=== 修复建议 ===")
    if config_issues:
        print("🔧 需要执行以下操作:")
        print("1. 重启所有正在运行的服务进程")
        print("2. 确保所有服务使用更新后的配置")
        print("3. 验证心跳超时时间为180秒")
    else:
        print("✅ 配置已正确加载，如有服务在运行请重启以应用新配置")
    
    return len(config_issues) == 0

def check_running_processes():
    """检查当前运行的相关进程"""
    print("\n=== 检查运行中的进程 ===")
    try:
        import psutil
        python_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info['cmdline'] or []
                    cmdline_str = ' '.join(cmdline)
                    
                    # 检查是否是LifeTrace相关进程
                    if any(keyword in cmdline_str for keyword in 
                          ['start_all_services', 'recorder', 'processor', 'server', 'lifetrace']):
                        python_processes.append({
                            'pid': proc.info['pid'],
                            'cmdline': cmdline_str
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if python_processes:
            print("🔍 发现以下LifeTrace相关进程:")
            for proc in python_processes:
                print(f"   PID {proc['pid']}: {proc['cmdline']}")
            print("\n⚠️  建议重启这些进程以应用新配置")
        else:
            print("✅ 未发现运行中的LifeTrace进程")
            
    except ImportError:
        print("⚠️  psutil模块未安装，无法检查进程状态")
    except Exception as e:
        print(f"❌ 检查进程时出错: {e}")

if __name__ == '__main__':
    success = test_config_in_modules()
    check_running_processes()
    
    print("\n" + "="*50)
    if success:
        print("✅ 配置测试完成，所有模块配置正常")
    else:
        print("❌ 配置测试发现问题，请查看上述详情")