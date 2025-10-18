#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置热重载功能测试脚本

用法：
    conda activate laptop_showcase
    python test_config_hot_reload.py
"""

import os
import sys
import time
import yaml
import shutil
from pathlib import Path

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config

def print_section(title):
    """打印分节标题"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_config_reload():
    """测试配置重载功能"""
    print_section("测试1: 配置重载基本功能")
    
    # 备份原配置
    config_path = config.config_path
    backup_path = f"{config_path}.backup"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    shutil.copy2(config_path, backup_path)
    print(f"✓ 已备份配置文件到: {backup_path}")
    
    try:
        # 读取当前配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        original_interval = config.get('record.interval', 1)
        print(f"✓ 当前截图间隔: {original_interval}s")
        
        # 修改配置
        new_interval = original_interval + 1
        if 'record' not in config_data:
            config_data['record'] = {}
        config_data['record']['interval'] = new_interval
        
        # 写入配置文件
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
        print(f"✓ 已修改配置，新间隔: {new_interval}s")
        
        # 手动触发重载
        print("  等待1秒...")
        time.sleep(1)
        
        success = config.reload()
        if success:
            print("✓ 配置重载成功")
        else:
            print("❌ 配置重载失败")
            return False
        
        # 验证配置已更新
        current_interval = config.get('record.interval', 1)
        if current_interval == new_interval:
            print(f"✓ 配置已更新: {current_interval}s")
            return True
        else:
            print(f"❌ 配置未更新，仍为: {current_interval}s")
            return False
            
    finally:
        # 恢复原配置
        shutil.move(backup_path, config_path)
        config.reload()
        print(f"✓ 已恢复原配置文件")

def test_callback_mechanism():
    """测试回调机制"""
    print_section("测试2: 配置变更回调机制")
    
    config_path = config.config_path
    backup_path = f"{config_path}.backup.callback"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    shutil.copy2(config_path, backup_path)
    
    callback_triggered = [False]
    old_config_received = [None]
    new_config_received = [None]
    
    def test_callback(old_config, new_config):
        """测试回调函数"""
        callback_triggered[0] = True
        old_config_received[0] = old_config
        new_config_received[0] = new_config
        print("✓ 回调函数被触发")
    
    try:
        # 注册回调
        config.register_callback(test_callback)
        print("✓ 已注册回调函数")
        
        # 修改配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        original_interval = config_data.get('record', {}).get('interval', 1)
        new_interval = original_interval + 10
        
        if 'record' not in config_data:
            config_data['record'] = {}
        config_data['record']['interval'] = new_interval
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, allow_unicode=True, sort_keys=False)
        print(f"✓ 已修改配置: {original_interval}s -> {new_interval}s")
        
        # 触发重载
        time.sleep(0.1)
        config.reload()
        
        # 检查回调是否被触发
        if callback_triggered[0]:
            print("✓ 回调机制工作正常")
            result = True
        else:
            print("❌ 回调未被触发")
            result = False
        
        # 取消注册
        config.unregister_callback(test_callback)
        print("✓ 已取消注册回调函数")
        
        return result
        
    finally:
        # 恢复原配置
        shutil.move(backup_path, config_path)
        config.reload()
        print("✓ 已恢复原配置文件")

def test_file_watching():
    """测试文件监听功能"""
    print_section("测试3: 文件监听功能")
    
    # 检查watchdog是否可用
    try:
        from watchdog.observers import Observer
        print("✓ watchdog库可用")
    except ImportError:
        print("❌ watchdog库不可用，请安装: pip install watchdog")
        return False
    
    # 启动监听
    success = config.start_watching()
    if success:
        print("✓ 配置文件监听已启动")
    else:
        print("❌ 启动配置文件监听失败")
        return False
    
    # 等待监听就绪
    time.sleep(1)
    
    # 停止监听
    config.stop_watching()
    print("✓ 配置文件监听已停止")
    
    return True

def test_thread_safety():
    """测试线程安全性"""
    print_section("测试4: 线程安全性")
    
    import threading
    
    errors = []
    
    def reload_config():
        """在线程中重载配置"""
        try:
            for _ in range(10):
                config.reload()
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    def read_config():
        """在线程中读取配置"""
        try:
            for _ in range(10):
                _ = config.get('record.interval', 1)
                time.sleep(0.01)
        except Exception as e:
            errors.append(e)
    
    # 创建多个线程
    threads = []
    for _ in range(3):
        threads.append(threading.Thread(target=reload_config))
        threads.append(threading.Thread(target=read_config))
    
    # 启动所有线程
    print("  启动多个线程进行并发测试...")
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    if errors:
        print(f"❌ 发现 {len(errors)} 个线程安全错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ 线程安全性测试通过")
        return True

def test_error_handling():
    """测试错误处理"""
    print_section("测试5: 错误处理")
    
    config_path = config.config_path
    backup_path = f"{config_path}.backup"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    shutil.copy2(config_path, backup_path)
    
    try:
        # 创建无效的YAML
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid: [yaml syntax\n")
        print("✓ 已写入无效的YAML配置")
        
        # 尝试重载
        success = config.reload()
        if not success:
            print("✓ 错误处理正常：保留了旧配置")
            return True
        else:
            print("❌ 错误处理异常：应该失败但成功了")
            return False
            
    finally:
        # 恢复原配置
        shutil.move(backup_path, config_path)
        config.reload()
        print("✓ 已恢复原配置文件")

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("  LifeTrace 配置热重载功能测试")
    print("="*60)
    print(f"\n配置文件路径: {config.config_path}")
    
    results = {}
    
    # 运行测试
    results['配置重载'] = test_config_reload()
    results['回调机制'] = test_callback_mechanism()
    results['文件监听'] = test_file_watching()
    results['线程安全'] = test_thread_safety()
    results['错误处理'] = test_error_handling()
    
    # 输出测试结果
    print_section("测试结果汇总")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！配置热重载功能工作正常。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查。")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

