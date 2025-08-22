#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动同步功能测试脚本

测试文件监控和一致性检查功能，验证数据库与文件系统的同步机制�?"""

import os
import sys
import time
import shutil
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.config import config
from lifetrace_backend.database import get_db_connection
from lifetrace_backend.sync_service import sync_service_manager
from lifetrace_backend.file_monitor import FileMonitorService
from lifetrace_backend.consistency_checker import ConsistencyChecker

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoSyncTester:
    """自动同步功能测试�?""
    
    def __init__(self):
        self.test_dir = None
        self.original_screenshots_dir = config.screenshots_dir
        self.test_files = []
        self.file_monitor = None
        self.consistency_checker = None
        
    def setup_test_environment(self):
        """设置测试环境"""
        logger.info("设置测试环境...")
        
        # 创建临时测试目录
        self.test_dir = tempfile.mkdtemp(prefix="lifetrace_test_")
        logger.info(f"测试目录: {self.test_dir}")
        
        # 临时修改配置
        config.screenshots_dir = self.test_dir
        
        # 创建一些测试文�?        self._create_test_files()
        
        # 创建对应的数据库记录
        self._create_test_database_records()
        
        logger.info("测试环境设置完成")
    
    def _create_test_files(self):
        """创建测试文件"""
        test_files = [
            "test_screenshot_1.png",
            "test_screenshot_2.jpg",
            "test_screenshot_3.jpeg",
            "orphan_file.png"  # 这个文件不会有数据库记录
        ]
        
        for filename in test_files:
            file_path = Path(self.test_dir) / filename
            # 创建一个简单的测试文件
            with open(file_path, 'wb') as f:
                f.write(b'test image data')
            self.test_files.append(filename)
            logger.info(f"创建测试文件: {filename}")
    
    def _create_test_database_records(self):
        """创建测试数据库记�?""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 为前3个文件创建数据库记录
                for i, filename in enumerate(self.test_files[:3], 1):
                    # 插入截图记录
                    cursor.execute(
                        "INSERT INTO screenshots (filename, timestamp, file_path) VALUES (?, ?, ?)",
                        (filename, datetime.now().isoformat(), str(Path(self.test_dir) / filename))
                    )
                    screenshot_id = cursor.lastrowid
                    
                    # 插入OCR结果
                    cursor.execute(
                        "INSERT INTO ocr_results (screenshot_id, text, confidence) VALUES (?, ?, ?)",
                        (screenshot_id, f"Test OCR text for {filename}", 0.95)
                    )
                    
                    # 插入搜索索引
                    cursor.execute(
                        "INSERT INTO search_index (screenshot_id, content) VALUES (?, ?)",
                        (screenshot_id, f"Test content for {filename}")
                    )
                    
                    logger.info(f"创建数据库记�? {filename} (ID: {screenshot_id})")
                
                # 创建一个孤立的数据库记录（文件不存在）
                cursor.execute(
                    "INSERT INTO screenshots (filename, timestamp, file_path) VALUES (?, ?, ?)",
                    ("orphan_record.png", datetime.now().isoformat(), str(Path(self.test_dir) / "orphan_record.png"))
                )
                orphan_id = cursor.lastrowid
                
                cursor.execute(
                    "INSERT INTO ocr_results (screenshot_id, text, confidence) VALUES (?, ?, ?)",
                    (orphan_id, "Orphan OCR text", 0.90)
                )
                
                logger.info(f"创建孤立数据库记�? orphan_record.png (ID: {orphan_id})")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"创建测试数据库记录失�? {e}")
            raise
    
    def test_file_monitor(self):
        """测试文件监控功能"""
        logger.info("\n=== 测试文件监控功能 ===")
        
        try:
            # 启动文件监控服务
            self.file_monitor = FileMonitorService(delay=1)  # 1秒延迟用于测�?            self.file_monitor.start()
            logger.info("文件监控服务已启�?)
            
            # 等待服务启动
            time.sleep(2)
            
            # 删除一个测试文�?            test_file = Path(self.test_dir) / "test_screenshot_1.png"
            if test_file.exists():
                test_file.unlink()
                logger.info(f"删除文件: {test_file.name}")
                
                # 等待文件监控处理
                time.sleep(3)
                
                # 检查数据库记录是否被清�?                self._check_database_cleanup("test_screenshot_1.png")
            
            # 移动一个文件（模拟重命名）
            old_file = Path(self.test_dir) / "test_screenshot_2.jpg"
            new_file = Path(self.test_dir) / "moved_screenshot.jpg"
            if old_file.exists():
                old_file.rename(new_file)
                logger.info(f"移动文件: {old_file.name} -> {new_file.name}")
                
                # 等待文件监控处理
                time.sleep(3)
                
                # 检查数据库记录是否被清�?                self._check_database_cleanup("test_screenshot_2.jpg")
            
            logger.info("文件监控测试完成")
            
        except Exception as e:
            logger.error(f"文件监控测试失败: {e}")
            raise
        finally:
            if self.file_monitor:
                self.file_monitor.stop()
                logger.info("文件监控服务已停�?)
    
    def test_consistency_checker(self):
        """测试一致性检查功�?""
        logger.info("\n=== 测试一致性检查功�?===")
        
        try:
            # 创建一致性检查器
            self.consistency_checker = ConsistencyChecker(check_interval=10)
            
            # 执行一致性检�?            result = self.consistency_checker.perform_consistency_check()
            
            logger.info(f"一致性检查结�? {result}")
            
            # 验证结果
            if 'orphaned_db_records' in result:
                logger.info(f"发现孤立数据库记�? {result['orphaned_db_records']}")
            
            if 'orphaned_files' in result:
                logger.info(f"发现孤立文件: {result['orphaned_files']}")
            
            if 'cleaned_records' in result:
                logger.info(f"清理的记录数: {result['cleaned_records']}")
            
            logger.info("一致性检查测试完�?)
            
        except Exception as e:
            logger.error(f"一致性检查测试失�? {e}")
            raise
    
    def test_sync_service_manager(self):
        """测试同步服务管理�?""
        logger.info("\n=== 测试同步服务管理�?===")
        
        try:
            # 获取服务状�?            status = sync_service_manager.get_status()
            logger.info(f"同步服务状�? {status}")
            
            # 强制执行一致性检�?            if sync_service_manager.running:
                result = sync_service_manager.force_consistency_check()
                logger.info(f"强制一致性检查结�? {result}")
            
            logger.info("同步服务管理器测试完�?)
            
        except Exception as e:
            logger.error(f"同步服务管理器测试失�? {e}")
            raise
    
    def _check_database_cleanup(self, filename):
        """检查数据库清理结果"""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 检查截图记�?                cursor.execute("SELECT COUNT(*) FROM screenshots WHERE filename = ?", (filename,))
                screenshot_count = cursor.fetchone()[0]
                
                if screenshot_count == 0:
                    logger.info(f"�?文件 {filename} 的数据库记录已被正确清理")
                else:
                    logger.warning(f"�?文件 {filename} 的数据库记录未被清理 (剩余: {screenshot_count})")
                
                # 检查相关记�?                cursor.execute(
                    "SELECT COUNT(*) FROM ocr_results WHERE screenshot_id IN "
                    "(SELECT id FROM screenshots WHERE filename = ?)",
                    (filename,)
                )
                ocr_count = cursor.fetchone()[0]
                
                cursor.execute(
                    "SELECT COUNT(*) FROM search_index WHERE screenshot_id IN "
                    "(SELECT id FROM screenshots WHERE filename = ?)",
                    (filename,)
                )
                index_count = cursor.fetchone()[0]
                
                logger.info(f"  关联记录 - OCR: {ocr_count}, 搜索索引: {index_count}")
                
        except Exception as e:
            logger.error(f"检查数据库清理结果失败: {e}")
    
    def cleanup_test_environment(self):
        """清理测试环境"""
        logger.info("清理测试环境...")
        
        try:
            # 恢复原始配置
            config.screenshots_dir = self.original_screenshots_dir
            
            # 清理测试数据库记�?            self._cleanup_test_database_records()
            
            # 删除测试目录
            if self.test_dir and os.path.exists(self.test_dir):
                shutil.rmtree(self.test_dir)
                logger.info(f"删除测试目录: {self.test_dir}")
            
            logger.info("测试环境清理完成")
            
        except Exception as e:
            logger.error(f"清理测试环境失败: {e}")
    
    def _cleanup_test_database_records(self):
        """清理测试数据库记�?""
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                
                # 删除测试相关的记�?                test_patterns = ['test_screenshot_%', 'orphan_%', 'moved_%']
                
                for pattern in test_patterns:
                    # 获取要删除的截图ID
                    cursor.execute("SELECT id FROM screenshots WHERE filename LIKE ?", (pattern,))
                    screenshot_ids = [row[0] for row in cursor.fetchall()]
                    
                    if screenshot_ids:
                        # 删除相关记录
                        placeholders = ','.join('?' * len(screenshot_ids))
                        
                        cursor.execute(
                            f"DELETE FROM search_index WHERE screenshot_id IN ({placeholders})",
                            screenshot_ids
                        )
                        cursor.execute(
                            f"DELETE FROM ocr_results WHERE screenshot_id IN ({placeholders})",
                            screenshot_ids
                        )
                        cursor.execute(
                            f"DELETE FROM processing_queue WHERE screenshot_id IN ({placeholders})",
                            screenshot_ids
                        )
                        cursor.execute(
                            f"DELETE FROM screenshots WHERE id IN ({placeholders})",
                            screenshot_ids
                        )
                        
                        logger.info(f"清理测试记录: {pattern} ({len(screenshot_ids)} �?")
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"清理测试数据库记录失�? {e}")
    
    def run_all_tests(self):
        """运行所有测�?""
        logger.info("开始自动同步功能测�?)
        
        try:
            self.setup_test_environment()
            
            # 运行各项测试
            self.test_consistency_checker()
            self.test_file_monitor()
            self.test_sync_service_manager()
            
            logger.info("\n=== 所有测试完�?===")
            logger.info("�?自动同步功能测试通过")
            
        except Exception as e:
            logger.error(f"测试失败: {e}")
            raise
        finally:
            self.cleanup_test_environment()

def main():
    """主函�?""
    tester = AutoSyncTester()
    
    try:
        tester.run_all_tests()
        print("\n测试成功完成�?)
        return 0
    except Exception as e:
        print(f"\n测试失败: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
