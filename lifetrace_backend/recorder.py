import os
import time
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import mss
from PIL import Image
import imagehash

from .config import config
from .utils import ensure_dir, get_active_window_info, get_screenshot_filename
from .storage import db_manager


class ScreenRecorder:
    """屏幕录制器"""
    
    def __init__(self):
        self.config = config
        self.screenshots_dir = self.config.screenshots_dir
        self.interval = self.config.get('record.interval', 1)
        self.screens = self._get_screen_list()
        self.hash_threshold = self.config.get('storage.hash_threshold', 5)
        self.deduplicate = self.config.get('storage.deduplicate', True)
        
        # 初始化截图目录
        ensure_dir(self.screenshots_dir)
        
        # 上一张截图的哈希值（用于去重）
        self.last_hashes = {}
        
        logging.info(f"屏幕录制器初始化完成，监控屏幕: {self.screens}")
    
    def _get_screen_list(self) -> List[int]:
        """获取要截图的屏幕列表"""
        screens_config = self.config.get('record.screens', 'all')
        print(screens_config)
        with mss.mss() as sct:
            monitor_count = len(sct.monitors) - 1  # 减1因为第0个是所有屏幕的组合
            
            if screens_config == 'all':
                return list(range(1, monitor_count + 1))
            elif isinstance(screens_config, list):
                return [s for s in screens_config if 1 <= s <= monitor_count]
            else:
                return [1] if monitor_count > 0 else []
    
    def _calculate_image_hash(self, image_path: str) -> str:
        """计算图像感知哈希值"""
        try:
            with Image.open(image_path) as img:
                return str(imagehash.phash(img))
        except Exception as e:
            logging.error(f"计算图像哈希失败 {image_path}: {e}")
            return ""
    
    def _is_duplicate(self, screen_id: int, image_hash: str) -> bool:
        """检查是否为重复图像"""
        if not self.deduplicate:
            return False
            
        if screen_id not in self.last_hashes:
            return False
            
        last_hash = self.last_hashes[screen_id]
        try:
            # 计算汉明距离
            current = imagehash.hex_to_hash(image_hash)
            previous = imagehash.hex_to_hash(last_hash)
            distance = current - previous
            
            return distance <= self.hash_threshold
        except Exception as e:
            logging.error(f"比较图像哈希失败: {e}")
            return False
    
    def _capture_screen(self, screen_id: int) -> Optional[str]:
        """截取指定屏幕"""
        try:
            with mss.mss() as sct:
                if screen_id >= len(sct.monitors):
                    logging.warning(f"屏幕ID {screen_id} 不存在")
                    return None
                
                monitor = sct.monitors[screen_id]
                screenshot = sct.grab(monitor)
                
                # 生成文件名
                timestamp = datetime.now()
                filename = get_screenshot_filename(screen_id, timestamp)
                file_path = os.path.join(self.screenshots_dir, filename)
                
                # 保存截图
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=file_path)
                
                # 计算图像哈希
                image_hash = self._calculate_image_hash(file_path)
                
                # 检查是否重复
                if self._is_duplicate(screen_id, image_hash):
                    # 删除重复图像
                    os.remove(file_path)
                    logging.debug(f"删除重复截图: {filename}")
                    return None
                
                # 更新哈希记录
                self.last_hashes[screen_id] = image_hash
                
                # 获取窗口信息
                app_name, window_title = get_active_window_info()
                
                # 获取图像尺寸
                try:
                    with Image.open(file_path) as img:
                        width, height = img.size
                except Exception:
                    width, height = 0, 0
                
                # 计算文件哈希
                import hashlib
                with open(file_path, 'rb') as f:
                    file_hash = hashlib.md5(f.read()).hexdigest()
                
                # 保存截图信息到数据库
                try:
                    screenshot_id = db_manager.add_screenshot(
                        file_path=file_path,
                        file_hash=file_hash,
                        width=width,
                        height=height,
                        screen_id=screen_id,
                        app_name=app_name or "未知应用",
                        window_title=window_title or "未知窗口"
                    )
                    logging.debug(f"截图记录已保存到数据库: {screenshot_id}")
                except Exception as e:
                    logging.error(f"保存截图记录到数据库失败: {e}")
                
                file_size = os.path.getsize(file_path)
                
                logging.info(f"截图保存: {filename} ({file_size} bytes) - {app_name}")
                
                return file_path
                
        except Exception as e:
            logging.error(f"截图失败 (屏幕 {screen_id}): {e}")
            return None
    
    def capture_all_screens(self) -> List[str]:
        """截取所有屏幕"""
        captured_files = []
        
        for screen_id in self.screens:
            file_path = self._capture_screen(screen_id)
            if file_path:
                captured_files.append(file_path)
        
        return captured_files
    
    def start_recording(self):
        """开始录制"""
        logging.info("开始屏幕录制...")
        
        try:
            while True:
                start_time = time.time()
                
                # 截图
                captured_files = self.capture_all_screens()
                
                if captured_files:
                    logging.debug(f"本次截取了 {len(captured_files)} 张截图")
                
                # 计算下次截图时间
                elapsed = time.time() - start_time
                sleep_time = max(0, self.interval - elapsed)
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    logging.warning(f"截图处理时间 ({elapsed:.2f}s) 超过间隔时间 ({self.interval}s)")
                    
        except KeyboardInterrupt:
            logging.info("收到停止信号，结束录制")
        except Exception as e:
            logging.error(f"录制过程中发生错误: {e}")
            raise

def main():
    """主函数 - 命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LifeTrace Screen Recorder')
    parser.add_argument('--config', help='配置文件路径')
    parser.add_argument('--interval', type=int, help='截图间隔（秒）')
    parser.add_argument('--screens', help='要截图的屏幕，用逗号分隔或使用"all"')
    parser.add_argument('--debug', action='store_true', help='启用调试日志')
    
    args = parser.parse_args()
    
    # 设置日志级别
    log_level = "DEBUG" if args.debug else "INFO"
    from .utils import setup_logging
    setup_logging(os.path.join(config.base_dir, 'logs'), log_level)
    
    # 更新配置
    if args.interval:
        config.set('record.interval', args.interval)
    
    if args.screens:
        if args.screens.lower() == 'all':
            config.set('record.screens', 'all')
        else:
            screens = [int(s.strip()) for s in args.screens.split(',')]
            config.set('record.screens', screens)
    
    # 创建并启动录制器
    recorder = ScreenRecorder()
    recorder.start_recording()

if __name__ == '__main__':
    main()