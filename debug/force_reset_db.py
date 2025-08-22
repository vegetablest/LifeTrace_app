#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强制重置LifeTrace数据库脚�?使用系统命令强制删除被占用的文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import subprocess
import shutil
import logging
from pathlib import Path
import time

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def force_delete_file(file_path):
    """强制删除文件，即使被占用"""
    try:
        if not file_path.exists():
            return True
            
        # 首先尝试正常删除
        try:
            file_path.unlink()
            logger.info(f"正常删除文件: {file_path}")
            return True
        except PermissionError:
            pass
        
        # 使用Windows命令强制删除
        try:
            result = subprocess.run(
                ['cmd', '/c', 'del', '/f', '/q', str(file_path)],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"强制删除文件: {file_path}")
                return True
            else:
                logger.warning(f"删除文件失败: {file_path}, 错误: {result.stderr}")
        except Exception as e:
            logger.error(f"强制删除命令失败: {e}")
        
        # 最后尝试使用PowerShell
        try:
            result = subprocess.run(
                ['powershell', '-Command', f'Remove-Item -Path "{file_path}" -Force'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.info(f"PowerShell删除文件: {file_path}")
                return True
        except Exception as e:
            logger.error(f"PowerShell删除失败: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"删除文件时发生错�? {e}")
        return False

def force_delete_directory(dir_path):
    """强制删除目录"""
    try:
        if not dir_path.exists():
            return True
            
        # 首先尝试正常删除
        try:
            shutil.rmtree(dir_path)
            logger.info(f"正常删除目录: {dir_path}")
            return True
        except Exception:
            pass
        
        # 使用Windows命令强制删除
        try:
            result = subprocess.run(
                ['cmd', '/c', 'rmdir', '/s', '/q', str(dir_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                logger.info(f"强制删除目录: {dir_path}")
                return True
        except Exception as e:
            logger.error(f"强制删除目录失败: {e}")
        
        return False
        
    except Exception as e:
        logger.error(f"删除目录时发生错�? {e}")
        return False

def reset_sqlite_database_force():
    """强制重置SQLite数据�?""
    try:
        logger.info("开始强制重置SQLite数据�?..")
        
        lifetrace_dir = Path.home() / ".lifetrace"
        
        # 要删除的数据库文�?        db_files = [
            lifetrace_dir / "lifetrace.db",
            lifetrace_dir / "lifetrace.db-wal",
            lifetrace_dir / "lifetrace.db-shm",
            lifetrace_dir / "lifetrace.db-journal"
        ]
        
        success_count = 0
        for db_file in db_files:
            if force_delete_file(db_file):
                success_count += 1
            elif db_file.exists():
                logger.warning(f"无法删除文件: {db_file}")
        
        logger.info(f"SQLite数据库重置完成，成功删除 {success_count} 个文�?)
        return True
        
    except Exception as e:
        logger.error(f"强制重置SQLite数据库失�? {e}")
        return False

def reset_vector_databases_force():
    """强制重置向量数据�?""
    try:
        logger.info("开始强制重置向量数据库...")
        
        lifetrace_dir = Path.home() / ".lifetrace"
        
        # 要删除的向量数据库目�?        vector_dirs = [
            lifetrace_dir / "vector_db",
            lifetrace_dir / "vector_db_text",
            lifetrace_dir / "vector_db_image"
        ]
        
        success_count = 0
        for vector_dir in vector_dirs:
            if force_delete_directory(vector_dir):
                success_count += 1
            elif vector_dir.exists():
                logger.warning(f"无法删除目录: {vector_dir}")
        
        logger.info(f"向量数据库重置完成，成功删除 {success_count} 个目�?)
        return True
        
    except Exception as e:
        logger.error(f"强制重置向量数据库失�? {e}")
        return False

def reset_screenshots_force():
    """强制删除截图文件"""
    try:
        logger.info("开始强制删除截图文�?..")
        
        screenshots_dir = Path.home() / ".lifetrace" / "screenshots"
        if not screenshots_dir.exists():
            logger.info("截图目录不存�?)
            return True
        
        # 删除所有图片文�?        deleted_count = 0
        for pattern in ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.gif"]:
            for file_path in screenshots_dir.glob(pattern):
                if force_delete_file(file_path):
                    deleted_count += 1
        
        logger.info(f"截图文件删除完成，删除了 {deleted_count} 个文�?)
        return True
        
    except Exception as e:
        logger.error(f"强制删除截图文件失败: {e}")
        return False

def reset_logs_force():
    """强制清理日志文件"""
    try:
        logger.info("开始强制清理日志文�?..")
        
        # 清理项目日志目录
        logs_dir = Path("logs")
        deleted_count = 0
        
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                if force_delete_file(log_file):
                    deleted_count += 1
        
        # 清理用户目录下的日志
        user_logs_dir = Path.home() / ".lifetrace" / "logs"
        if user_logs_dir.exists():
            for log_file in user_logs_dir.glob("*.log"):
                if force_delete_file(log_file):
                    deleted_count += 1
        
        logger.info(f"日志文件清理完成，删除了 {deleted_count} 个文�?)
        return True
        
    except Exception as e:
        logger.error(f"强制清理日志文件失败: {e}")
        return False

def verify_reset():
    """验证重置结果"""
    try:
        logger.info("验证重置结果...")
        
        lifetrace_dir = Path.home() / ".lifetrace"
        
        # 检查数据库文件
        db_files = [
            lifetrace_dir / "lifetrace.db",
            lifetrace_dir / "lifetrace.db-wal",
            lifetrace_dir / "lifetrace.db-shm"
        ]
        
        for db_file in db_files:
            if db_file.exists():
                logger.warning(f"⚠️ 数据库文件仍存在: {db_file}")
            else:
                logger.info(f"�?数据库文件已删除: {db_file.name}")
        
        # 检查向量数据库目录
        vector_dirs = [
            lifetrace_dir / "vector_db",
            lifetrace_dir / "vector_db_text",
            lifetrace_dir / "vector_db_image"
        ]
        
        for vector_dir in vector_dirs:
            if vector_dir.exists():
                logger.warning(f"⚠️ 向量数据库目录仍存在: {vector_dir}")
            else:
                logger.info(f"�?向量数据库目录已删除: {vector_dir.name}")
        
        # 检查截图目�?        screenshots_dir = lifetrace_dir / "screenshots"
        if screenshots_dir.exists():
            screenshot_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
            if len(screenshot_files) == 0:
                logger.info("�?截图文件已清�?)
            else:
                logger.warning(f"⚠️ 仍有 {len(screenshot_files)} 个截图文�?)
        else:
            logger.info("�?截图目录不存�?)
        
        logger.info("重置验证完成")
        return True
        
    except Exception as e:
        logger.error(f"验证重置失败: {e}")
        return False

def main():
    """主函�?""
    print("=== LifeTrace 强制数据库重置工�?===")
    print("⚠️  强制删除所有数据，包括被占用的文件")
    print()
    
    logger.info("开始强制重置过�?..")
    
    success_count = 0
    total_steps = 4
    
    # 1. 强制重置SQLite数据�?    if reset_sqlite_database_force():
        success_count += 1
    
    # 2. 强制删除截图文件
    if reset_screenshots_force():
        success_count += 1
    
    # 3. 强制重置向量数据�?    if reset_vector_databases_force():
        success_count += 1
    
    # 4. 强制清理日志文件
    if reset_logs_force():
        success_count += 1
    
    print(f"\n强制重置过程完成: {success_count}/{total_steps} 步骤成功")
    
    # 验证重置结果
    verify_reset()
    
    if success_count == total_steps:
        print("\n🎉 所有数据库强制重置成功�?)
        print("系统现在是全新状态，可以重新开始使用�?)
    else:
        print("\n⚠️ 部分重置步骤失败，请检查日志信息�?)
    
    print("\n重置完成后，建议重启LifeTrace服务�?)

if __name__ == "__main__":
    main()
