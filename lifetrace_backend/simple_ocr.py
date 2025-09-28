#!/usr/bin/env python3
"""
LifeTrace 简化OCR处理器
参考 pad_ocr.py 设计，提供简单高效的OCR功能
"""

import os
import sys
import time
import logging
from pathlib import Path

# 添加项目根目录到Python路径，以便直接运行此文件
if __name__ == '__main__':
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))

try:
    from rapidocr_onnxruntime import RapidOCR
    from PIL import Image
    import numpy as np
    RAPIDOCR_AVAILABLE = True
except ImportError:
    RAPIDOCR_AVAILABLE = False
    print("错误: RapidOCR未安装，请运行: pip install rapidocr-onnxruntime")
    exit(1)

from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.vector_service import create_vector_service
from lifetrace_backend.simple_heartbeat import SimpleHeartbeatSender


class SimpleOCRProcessor:
    """简化的OCR处理器类"""
    
    def __init__(self):
        self.ocr = None
        self.vector_service = None
        self.is_running = False
        
    def is_available(self):
        """检查OCR引擎是否可用"""
        return RAPIDOCR_AVAILABLE
        
    def start(self):
        """启动OCR处理服务"""
        self.is_running = True
        # 注意：这里不应该调用main()，因为main()会启动独立的服务进程
        # 如果需要在server中使用OCR功能，应该直接调用process_image方法
        
    def stop(self):
        """停止OCR处理服务"""
        self.is_running = False
        
    def get_statistics(self):
        """获取OCR处理统计信息"""
        try:
            from lifetrace_backend.models import Screenshot, OCRResult
            with db_manager.get_session() as session:
                total_screenshots = session.query(Screenshot).count()
                ocr_results = session.query(OCRResult).count()
                unprocessed = total_screenshots - ocr_results
                
                return {
                    'status': 'running' if self.is_running else 'stopped',
                    'total_screenshots': total_screenshots,
                    'processed': ocr_results,
                    'unprocessed': unprocessed,
                    'check_interval': config.get('ocr.check_interval', 0.5)
                }
        except Exception as e:
            logging.error(f"获取OCR统计信息失败: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
            
    def process_image(self, image_path):
        """处理单个图像文件"""
        try:
            # 初始化OCR引擎（如果还没有初始化）
            if self.ocr is None:
                self.ocr = RapidOCR()
                
            # 记录开始时间
            start_time = time.time()
            
            # 图像预处理
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                img_array = np.array(img)
            
            # 执行OCR
            result, _ = self.ocr(img_array)
            
            # 计算处理时间
            processing_time = time.time() - start_time
            
            # 提取文本内容
            ocr_text = ""
            if result:
                for item in result:
                    if len(item) >= 3:
                        text = item[1]
                        confidence = float(item[2])
                        if text and text.strip() and confidence > 0.5:
                            ocr_text += text.strip() + "\n"
            
            # 保存到数据库
            ocr_result = {
                'text_content': ocr_text,
                'confidence': 0.8,
                'language': 'ch',
                'processing_time': processing_time
            }
            
            save_to_database(image_path, ocr_result, self.vector_service)
            
            return {
                'success': True,
                'text_content': ocr_text,
                'processing_time': processing_time
            }
            
        except Exception as e:
            logging.error(f"处理图像失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def save_to_database(image_path: str, ocr_result: dict, vector_service=None):
    """保存OCR结果到数据库"""
    try:
        # 查找对应的截图记录
        screenshot = db_manager.get_screenshot_by_path(image_path)
        if not screenshot:
            # 如果没有找到截图记录，为外部文件创建一个记录
            logging.info(f"为外部截图文件创建数据库记录: {image_path}")
            screenshot_id = create_screenshot_record(image_path)
            if not screenshot_id:
                logging.warning(f"无法为外部文件创建截图记录: {image_path}")
                return
        else:
            screenshot_id = screenshot['id']
        
        # 添加OCR结果到SQLite数据库
        ocr_result_id = db_manager.add_ocr_result(
            screenshot_id=screenshot_id,
            text_content=ocr_result['text_content'],
            confidence=ocr_result['confidence'],
            language=ocr_result.get('language', 'ch'),
            processing_time=ocr_result['processing_time']
        )
        
        # 更新截图状态
        db_manager.update_screenshot_processed(screenshot_id)
        
        # 添加到向量数据库
        if vector_service and vector_service.is_enabled() and ocr_result_id:
            try:
                # 获取完整的OCR结果对象
                with db_manager.get_session() as session:
                    from lifetrace_backend.models import OCRResult, Screenshot
                    ocr_obj = session.query(OCRResult).filter(OCRResult.id == ocr_result_id).first()
                    screenshot_obj = session.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
                    
                    if ocr_obj:
                        success = vector_service.add_ocr_result(ocr_obj, screenshot_obj)
                        if success:
                            logging.debug(f"OCR结果已添加到向量数据库: {ocr_result_id}")
                        else:
                            logging.warning(f"向量数据库添加失败: {ocr_result_id}")
                    # 同步事件文档（事件级）
                    if screenshot_obj and getattr(screenshot_obj, 'event_id', None):
                        try:
                            vector_service.upsert_event_document(screenshot_obj.event_id)
                        except Exception as _:
                            pass
            except Exception as ve:
                logging.error(f"向量数据库操作失败: {ve}")
        
    except Exception as e:
        logging.error(f"保存OCR结果到数据库失败: {e}")


def create_screenshot_record(image_path: str):
    """为外部截图文件创建数据库记录"""
    try:
        import hashlib
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            return None
        
        # 计算文件哈希
        with open(image_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        
        # 获取图像尺寸
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception:
            width, height = 0, 0
        
        # 从文件名推断应用信息
        filename = os.path.basename(image_path)
        app_name = "外部工具"
        window_title = filename
        
        # 如果是Snipaste文件，标记为Snipaste
        if filename.startswith('Snipaste_'):
            app_name = "Snipaste"
            window_title = f"Snipaste截图 - {filename}"
        
        # 添加截图记录
        screenshot_id = db_manager.add_screenshot(
            file_path=image_path,
            file_hash=file_hash,
            width=width,
            height=height,
            screen_id=0,  # 外部文件默认屏幕ID为0
            app_name=app_name,
            window_title=window_title
        )
        
        return screenshot_id
        
    except Exception as e:
        logging.error(f"创建外部截图记录失败: {e}")
        return None


# 日志配置已移至统一的logging_config.py中


def get_unprocessed_screenshots(logger=None, limit=50):
    """从数据库获取未处理OCR的截图记录
    
    Args:
        logger: 日志记录器
        limit: 限制返回的记录数量，避免内存溢出
    """
    # 如果没有传入logger，使用默认的logging
    if logger is None:
        import logging as default_logging
        logger = default_logging
        
    try:
        from lifetrace_backend.models import Screenshot, OCRResult
        with db_manager.get_session() as session:
            # 优化查询：使用NOT EXISTS子查询替代LEFT JOIN
            # 这种方式在大数据量时性能更好
            unprocessed = session.query(Screenshot).filter(
                ~session.query(OCRResult).filter(
                    OCRResult.screenshot_id == Screenshot.id
                ).exists()
            ).order_by(Screenshot.created_at.asc()).limit(limit).all()
            
            logger.info(f"查询到 {len(unprocessed)} 条未处理的截图记录")
            
            return [{
                'id': screenshot.id,
                'file_path': screenshot.file_path,
                'created_at': screenshot.created_at
            } for screenshot in unprocessed]
    except Exception as e:
        logger.error(f"查询未处理截图失败: {e}")
        return []


def process_screenshot_ocr(screenshot_info, ocr_engine, vector_service, logger=None):
    """处理单个截图的OCR"""
    screenshot_id = screenshot_info['id']
    file_path = screenshot_info['file_path']
    
    # 如果没有传入logger，使用默认的logging
    if logger is None:
        import logging as default_logging
        logger = default_logging
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"截图文件不存在，跳过处理: {file_path}")
            return False
        
        logger.info(f"开始处理截图 ID {screenshot_id}: {os.path.basename(file_path)}")
        
        # 记录开始时间
        start_time = time.time()
        
        # 图像预处理优化
        with Image.open(file_path) as img:
            img = img.convert("RGB")
            # 缩放图像以提高处理速度
            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            img_array = np.array(img)
        
        # 使用RapidOCR进行识别
        result, _ = ocr_engine(img_array)
        
        # 计算推理时间
        elapsed_time = time.time() - start_time
        
        # 提取RapidOCR识别结果
        ocr_text = ""
        if result:
            for item in result:
                if len(item) >= 3:
                    text = item[1]  # 文本内容
                    confidence = float(item[2])  # 置信度
                    if text and text.strip() and confidence > 0.5:  # 过滤低置信度结果
                        ocr_text += text.strip() + "\n"
        
        # 保存到数据库
        ocr_result = {
            'text_content': ocr_text,
            'confidence': 0.8,  # 简化版使用固定置信度
            'language': 'ch',
            'processing_time': elapsed_time
        }
        save_to_database(file_path, ocr_result, vector_service)
        
        logger.info(f'OCR处理完成 ID {screenshot_id}, 用时: {elapsed_time:.2f}秒')
        return True
        
    except Exception as e:
        logger.error(f"处理截图 {screenshot_id} 失败: {e}")
        return False


def main():
    """主函数 - 基于数据库驱动的OCR处理"""
    print("LifeTrace 简化OCR处理器启动...")
    
    # 设置日志
    from lifetrace_backend.logging_config import setup_logging
    logger_manager = setup_logging(config)
    logger = logger_manager.get_ocr_logger()
    
    # 初始化UDP心跳发送器
    heartbeat_sender = SimpleHeartbeatSender('ocr')
    
    # 检查配置
    if not os.path.exists(config.database_path):
        print(f"错误: 数据库未初始化，请先运行: lifetrace init")
        return
    
    # 初始化RapidOCR
    print("正在初始化RapidOCR引擎...")
    logger.info("正在初始化RapidOCR引擎...")
    try:
        ocr = RapidOCR()
        print("RapidOCR引擎初始化成功")
        logger.info("RapidOCR引擎初始化成功")
    except Exception as e:
        print(f"RapidOCR初始化失败: {e}")
        logger.error(f"RapidOCR初始化失败: {e}")
        return
    
    # 初始化向量数据库服务
    print("正在初始化向量数据库服务...")
    logger.info("正在初始化向量数据库服务...")
    vector_service = create_vector_service(config, db_manager)
    if vector_service.is_enabled():
        print("向量数据库服务已启用")
        logger.info("向量数据库服务已启用")
    else:
        print("向量数据库服务未启用或不可用")
        logger.info("向量数据库服务未启用或不可用")
    
    # 获取检查间隔配置
    check_interval = config.get('ocr.check_interval', 5)  # 默认5秒检查一次
    print(f"数据库检查间隔: {check_interval}秒")
    
    print("开始基于数据库的OCR处理...")
    print("按 Ctrl+C 停止服务")
    logger.info(f"OCR服务启动完成，检查间隔: {check_interval}秒")
    
    # 启动UDP心跳发送
    heartbeat_sender.start(interval=1.0)
    processed_count = 0
    
    try:
        while True:
            start_time = time.time()
            
            # 发送心跳（包含处理状态信息）
            heartbeat_sender.send_heartbeat({
                'status': 'running',
                'processed_count': processed_count,
                'check_interval': check_interval
            })
            
            # 从数据库获取未处理的截图
            unprocessed_screenshots = get_unprocessed_screenshots(logger)
            
            if unprocessed_screenshots:
                logger.info(f"发现 {len(unprocessed_screenshots)} 个未处理的截图")
                
                # 按创建时间排序，优先处理最新的
                unprocessed_screenshots.sort(key=lambda x: x['created_at'], reverse=True)
                
                # 处理每个未处理的截图
                for screenshot_info in unprocessed_screenshots:
                    success = process_screenshot_ocr(screenshot_info, ocr, vector_service, logger)
                    if success:
                        processed_count += 1
                        # 处理成功后稍作停顿，避免过度占用资源
                        time.sleep(0.1)
            else:
                # 没有未处理的截图，等待一段时间再检查
                time.sleep(check_interval)
                
    except KeyboardInterrupt:
        print("\n收到停止信号，正在退出...")
        logger.info("收到停止信号，结束OCR处理")
        heartbeat_sender.send_heartbeat({'status': 'stopped', 'reason': 'keyboard_interrupt'})
    except Exception as e:
        print(f"服务异常: {e}")
        logger.error(f"OCR处理过程中发生错误: {e}")
        heartbeat_sender.send_heartbeat({'status': 'error', 'error': str(e)})
        raise
    finally:
        print("OCR服务已停止")
        heartbeat_sender.stop()


if __name__ == '__main__':
    main()