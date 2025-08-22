#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面重置LifeTrace数据库脚�?清理所有数据库和相关文件，让系统从头开�?"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import shutil
import logging
from pathlib import Path
from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.multimodal_vector_service import MultimodalVectorService

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def confirm_reset():
    """确认用户真的要重置所有数�?""
    print("⚠️  警告：此操作将删除所有数据，包括�?)
    print("   - SQLite数据库中的所有记�?)
    print("   - 所有截图文�?)
    print("   - 向量数据库中的所有嵌�?)
    print("   - 多模态向量数据库")
    print("\n此操作不可逆！")
    
    response = input("\n确定要继续吗？请输入 'YES' 来确�? ")
    return response.strip() == 'YES'

def backup_current_data():
    """备份当前数据（可选）"""
    try:
        backup_dir = Path.home() / ".lifetrace_backup"
        backup_dir.mkdir(exist_ok=True)
        
        # 备份SQLite数据�?        db_path = Path.home() / ".lifetrace" / "lifetrace.db"
        if db_path.exists():
            backup_db_path = backup_dir / f"lifetrace_backup_{int(time.time())}.db"
            shutil.copy2(db_path, backup_db_path)
            logger.info(f"数据库已备份�? {backup_db_path}")
        
        # 备份向量数据库目�?        vector_dirs = [
            Path.home() / ".lifetrace" / "vector_db",
            Path.home() / ".lifetrace" / "vector_db_text", 
            Path.home() / ".lifetrace" / "vector_db_image"
        ]
        
        for vector_dir in vector_dirs:
            if vector_dir.exists():
                backup_vector_dir = backup_dir / f"{vector_dir.name}_backup_{int(time.time())}"
                shutil.copytree(vector_dir, backup_vector_dir)
                logger.info(f"向量数据库已备份�? {backup_vector_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"备份失败: {e}")
        return False

def reset_sqlite_database():
    """重置SQLite数据�?""
    try:
        logger.info("开始重置SQLite数据�?..")
        
        # 删除数据库文�?        db_path = Path.home() / ".lifetrace" / "lifetrace.db"
        if db_path.exists():
            db_path.unlink()
            logger.info(f"已删除数据库文件: {db_path}")
        
        # 删除可能的WAL和SHM文件
        wal_path = Path.home() / ".lifetrace" / "lifetrace.db-wal"
        shm_path = Path.home() / ".lifetrace" / "lifetrace.db-shm"
        
        if wal_path.exists():
            wal_path.unlink()
            logger.info(f"已删除WAL文件: {wal_path}")
            
        if shm_path.exists():
            shm_path.unlink()
            logger.info(f"已删除SHM文件: {shm_path}")
        
        logger.info("SQLite数据库重置完�?)
        return True
        
    except Exception as e:
        logger.error(f"重置SQLite数据库失�? {e}")
        return False

def reset_screenshot_files():
    """删除所有截图文�?""
    try:
        logger.info("开始删除截图文�?..")
        
        screenshots_dir = Path.home() / ".lifetrace" / "screenshots"
        if screenshots_dir.exists():
            # 删除所有截图文�?            for file_path in screenshots_dir.glob("*.png"):
                file_path.unlink()
                logger.debug(f"已删除截�? {file_path}")
            
            for file_path in screenshots_dir.glob("*.jpg"):
                file_path.unlink()
                logger.debug(f"已删除截�? {file_path}")
            
            logger.info("截图文件删除完成")
        
        return True
        
    except Exception as e:
        logger.error(f"删除截图文件失败: {e}")
        return False

def reset_vector_databases():
    """重置所有向量数据库"""
    try:
        logger.info("开始重置向量数据库...")
        
        # 要删除的向量数据库目�?        vector_dirs = [
            Path.home() / ".lifetrace" / "vector_db",
            Path.home() / ".lifetrace" / "vector_db_text",
            Path.home() / ".lifetrace" / "vector_db_image"
        ]
        
        for vector_dir in vector_dirs:
            if vector_dir.exists():
                shutil.rmtree(vector_dir)
                logger.info(f"已删除向量数据库目录: {vector_dir}")
        
        logger.info("向量数据库重置完�?)
        return True
        
    except Exception as e:
        logger.error(f"重置向量数据库失�? {e}")
        return False

def reset_logs():
    """清理日志文件"""
    try:
        logger.info("开始清理日志文�?..")
        
        # 清理项目日志目录
        logs_dir = Path("logs")
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                log_file.unlink()
                logger.debug(f"已删除日志文�? {log_file}")
        
        # 清理用户目录下的日志
        user_logs_dir = Path.home() / ".lifetrace" / "logs"
        if user_logs_dir.exists():
            for log_file in user_logs_dir.glob("*.log"):
                log_file.unlink()
                logger.debug(f"已删除日志文�? {log_file}")
        
        logger.info("日志文件清理完成")
        return True
        
    except Exception as e:
        logger.error(f"清理日志文件失败: {e}")
        return False

def verify_reset():
    """验证重置是否完成"""
    try:
        logger.info("验证重置结果...")
        
        # 检查数据库是否为空
        from lifetrace_backend.storage import DatabaseManager
        from lifetrace_backend.models import Screenshot, OCRResult
        
        new_db_manager = DatabaseManager()
        with new_db_manager.get_session() as session:
            screenshot_count = session.query(Screenshot).count()
            ocr_count = session.query(OCRResult).count()
            
            logger.info(f"数据库验证结�?")
            logger.info(f"  截图记录�? {screenshot_count}")
            logger.info(f"  OCR记录�? {ocr_count}")
            
            if screenshot_count == 0 and ocr_count == 0:
                logger.info("�?SQLite数据库重置成�?)
            else:
                logger.warning("⚠️ SQLite数据库可能未完全重置")
        
        # 检查向量数据库目录
        vector_dirs = [
            Path.home() / ".lifetrace" / "vector_db",
            Path.home() / ".lifetrace" / "vector_db_text",
            Path.home() / ".lifetrace" / "vector_db_image"
        ]
        
        for vector_dir in vector_dirs:
            if vector_dir.exists():
                logger.warning(f"⚠️ 向量数据库目录仍存在: {vector_dir}")
            else:
                logger.info(f"�?向量数据库目录已删除: {vector_dir.name}")
        
        # 检查截图目�?        screenshots_dir = Path.home() / ".lifetrace" / "screenshots"
        if screenshots_dir.exists():
            screenshot_files = list(screenshots_dir.glob("*.png")) + list(screenshots_dir.glob("*.jpg"))
            if len(screenshot_files) == 0:
                logger.info("�?截图文件已清�?)
            else:
                logger.warning(f"⚠️ 仍有 {len(screenshot_files)} 个截图文�?)
        
        logger.info("重置验证完成")
        return True
        
    except Exception as e:
        logger.error(f"验证重置失败: {e}")
        return False

def main():
    """主函�?""
    import time
    
    print("=== LifeTrace 数据库全面重置工�?===")
    print()
    
    # 直接开始重置，不需要确�?    print("开始重置所有数据库...")
    print("⚠️  将删除所有数据：SQLite数据库、截图文件、向量数据库")
    
    print("\n开始重置过�?..")
    
    # 不进行备份，直接重置
    logger.info("跳过备份，直接开始重�?)
    
    success_count = 0
    total_steps = 4
    
    # 1. 重置SQLite数据�?    if reset_sqlite_database():
        success_count += 1
    
    # 2. 删除截图文件
    if reset_screenshot_files():
        success_count += 1
    
    # 3. 重置向量数据�?    if reset_vector_databases():
        success_count += 1
    
    # 4. 清理日志文件
    if reset_logs():
        success_count += 1
    
    print(f"\n重置过程完成: {success_count}/{total_steps} 步骤成功")
    
    # 验证重置结果
    verify_reset()
    
    if success_count == total_steps:
        print("\n🎉 所有数据库重置成功�?)
        print("系统现在是全新状态，可以重新开始使用�?)
    else:
        print("\n⚠️ 部分重置步骤失败，请检查日志信息�?)
    
    print("\n重置完成后，建议重启LifeTrace服务�?)

if __name__ == "__main__":
    # 添加命令行参数支�?    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        # 强制模式，跳过所有确�?        main()
    else:
        # 交互模式
        if confirm_reset():
            main()
        else:
            print("操作已取�?)
