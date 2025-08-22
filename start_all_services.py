#!/usr/bin/env python3
"""
启动所有LifeTrace服务
不依赖lifetrace命令行工具
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace_backend.config import config
from lifetrace_backend.sync_service import sync_service_manager


class ServiceManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        self.sync_service_started = False
    
    def start_service(self, name, module):
        """启动单个服务"""
        try:
            print(f"🚀 启动 {name} 服务...")
            
            cmd = [sys.executable, '-m', module]
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes[name] = process
            print(f"✅ {name} 服务已启动 (PID: {process.pid})")
            
            return True
            
        except Exception as e:
            print(f"❌ 启动 {name} 服务失败: {e}")
            return False
    
    def stop_all_services(self):
        """停止所有服务"""
        print(f"\n🛑 正在停止所有服务...")
        
        # 先停止同步服务
        if self.sync_service_started:
            try:
                sync_service_manager.stop_all()
                print(f"✅ 同步服务已停止")
                self.sync_service_started = False
            except Exception as e:
                print(f"❌ 停止同步服务失败: {e}")
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {name} 服务已停止")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"⚡ 强制停止 {name} 服务")
                except Exception as e:
                    print(f"❌ 停止 {name} 服务失败: {e}")
    
    def check_services(self):
        """检查服务状态"""
        running_services = []
        
        for name, process in self.processes.items():
            if process and process.poll() is None:
                running_services.append(f"{name} (PID: {process.pid})")
            else:
                print(f"❌ {name} 服务已停止")
        
        if running_services:
            print(f"✅ 运行中的服务: {', '.join(running_services)}")
        
        return len(running_services)
    
    def show_service_output(self):
        """显示服务输出"""
        for name, process in self.processes.items():
            if process and process.poll() is None:
                try:
                    # 非阻塞读取输出
                    stdout_data = process.stdout.read()
                    stderr_data = process.stderr.read()
                    
                    if stdout_data:
                        print(f"[{name} STDOUT] {stdout_data}")
                    if stderr_data:
                        print(f"[{name} STDERR] {stderr_data}")
                        
                except Exception:
                    pass


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    missing_deps = []
    
    try:
        import mss
        print("✅ mss (截图)")
    except ImportError:
        missing_deps.append("mss")
    
    try:
        import fastapi
        print("✅ fastapi (Web服务)")
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import rapidocr_onnxruntime
        print("✅ rapidocr-onnxruntime (OCR)")
    except ImportError:
        missing_deps.append("rapidocr-onnxruntime")
    
    try:
        import sqlalchemy
        print("✅ sqlalchemy (数据库)")
    except ImportError:
        missing_deps.append("sqlalchemy")
    
    if missing_deps:
        print(f"❌ 缺少依赖: {', '.join(missing_deps)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    return True


def check_database():
    """检查数据库"""
    print(f"\n🗄️ 检查数据库...")
    
    db_path = config.database_path
    if os.path.exists(db_path):
        print(f"✅ 数据库存在: {db_path}")
        return True
    else:
        print(f"❌ 数据库不存在: {db_path}")
        print("请先运行: python manual_reset.py")
        return False


def main():
    """主函数"""
    print("🚀 LifeTrace 服务启动器")
    print("=" * 40)
    
    # 检查依赖和数据库
    if not check_dependencies():
        return
    
    if not check_database():
        return
    
    # 创建服务管理器
    manager = ServiceManager()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print(f"\n⚠️  收到停止信号 ({signum})")
        manager.running = False
        manager.stop_all_services()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 启动服务
    services = [
        ("录制器", "lifetrace_backend.recorder"),
        ("处理器", "lifetrace_backend.processor"),
        ("OCR服务", "lifetrace_backend.simple_ocr"),
        ("Web服务", "lifetrace_backend.server")
    ]
    
    success_count = 0
    for name, module in services:
        if manager.start_service(name, module):
            success_count += 1
            time.sleep(2)  # 给服务启动时间
    
    if success_count == 0:
        print("❌ 没有服务启动成功")
        return
    
    print(f"\n✅ 成功启动 {success_count}/{len(services)} 个服务")
    
    # 启动同步服务
    if success_count > 0:
        try:
            print(f"\n🔄 启动同步服务...")
            sync_service_manager.start_all()
            manager.sync_service_started = True
            print(f"✅ 同步服务已启动")
        except Exception as e:
            print(f"❌ 启动同步服务失败: {e}")
    
    print(f"\n📱 Web界面: http://localhost:8840")
    print(f"💡 按 Ctrl+C 停止所有服务")
    
    # 监控服务
    try:
        while manager.running:
            time.sleep(10)
            running_count = manager.check_services()
            
            if running_count == 0:
                print("❌ 所有服务都已停止")
                break
                
    except KeyboardInterrupt:
        print(f"\n⚠️  用户中断")
    finally:
        manager.stop_all_services()
        print(f"\n👋 所有服务已停止")


if __name__ == '__main__':
    main()