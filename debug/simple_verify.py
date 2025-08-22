#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的LifeTrace重置验证脚本
"""

import os
from pathlib import Path

def check_reset_status():
    """检查重置状�?""
    print("=== LifeTrace 重置状态检�?===")
    print()
    
    lifetrace_dir = Path.home() / ".lifetrace"
    print(f"LifeTrace目录: {lifetrace_dir}")
    
    if lifetrace_dir.exists():
        print("�?LifeTrace目录存在")
    else:
        print("📁 LifeTrace目录不存�?)
    
    # 检查数据库文件
    print("\n=== 数据库文件检�?===")
    db_files = [
        "lifetrace.db",
        "lifetrace.db-wal", 
        "lifetrace.db-shm",
        "lifetrace.db-journal"
    ]
    
    for db_file in db_files:
        db_path = lifetrace_dir / db_file
        if db_path.exists():
            print(f"⚠️ {db_file} 仍存�?)
        else:
            print(f"�?{db_file} 已删�?)
    
    # 检查向量数据库目录
    print("\n=== 向量数据库目录检�?===")
    vector_dirs = [
        "vector_db",
        "vector_db_text",
        "vector_db_image"
    ]
    
    for vector_dir in vector_dirs:
        vector_path = lifetrace_dir / vector_dir
        if vector_path.exists():
            print(f"⚠️ {vector_dir} 目录仍存�?)
        else:
            print(f"�?{vector_dir} 目录已删�?)
    
    # 检查截图目�?    print("\n=== 截图文件检�?===")
    screenshots_dir = lifetrace_dir / "screenshots"
    if screenshots_dir.exists():
        png_files = list(screenshots_dir.glob("*.png"))
        jpg_files = list(screenshots_dir.glob("*.jpg"))
        total_files = len(png_files) + len(jpg_files)
        
        if total_files == 0:
            print("�?截图目录为空")
        else:
            print(f"⚠️ 截图目录中仍�?{total_files} 个文�?)
    else:
        print("�?截图目录不存�?)
    
    # 检查日志目�?    print("\n=== 日志文件检�?===")
    
    # 项目日志
    project_logs = Path("logs")
    if project_logs.exists():
        log_files = list(project_logs.glob("*.log"))
        if len(log_files) == 0:
            print("�?项目日志目录为空")
        else:
            print(f"ℹ️ 项目日志目录中有 {len(log_files)} 个文�?)
    else:
        print("�?项目日志目录不存�?)
    
    # 用户日志
    user_logs = lifetrace_dir / "logs"
    if user_logs.exists():
        log_files = list(user_logs.glob("*.log"))
        if len(log_files) == 0:
            print("�?用户日志目录为空")
        else:
            print(f"ℹ️ 用户日志目录中有 {len(log_files)} 个文�?)
    else:
        print("�?用户日志目录不存�?)
    
    print("\n=== 重置状态总结 ===")
    
    # 检查关键文件是否都已删�?    critical_files_deleted = True
    
    for db_file in db_files[:3]:  # 只检查主要的数据库文�?        if (lifetrace_dir / db_file).exists():
            critical_files_deleted = False
            break
    
    for vector_dir in vector_dirs:
        if (lifetrace_dir / vector_dir).exists():
            critical_files_deleted = False
            break
    
    if critical_files_deleted:
        print("🎉 重置成功�?)
        print("�?所有关键数据库文件和目录已删除")
        print("�?系统已恢复到初始状�?)
        print("\n现在可以重新启动LifeTrace服务开始使用�?)
    else:
        print("⚠️ 重置不完�?)
        print("部分文件或目录仍然存在，可能需要手动清理�?)
    
    print("\n建议�?)
    print("1. 重启LifeTrace服务")
    print("2. 检查服务是否正常启�?)
    print("3. 验证新的数据库是否正确创�?)

if __name__ == "__main__":
    try:
        check_reset_status()
    except Exception as e:
        print(f"检查过程中发生错误: {e}")
