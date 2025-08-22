#!/usr/bin/env python3
"""
LifeTrace 简化OCR处理器
参考 pad_ocr.py 设计，提供简单高效的OCR功能
"""

import os
import time
import logging
from pathlib import Path

try:
    from rapidocr_onnxruntime import RapidOCR
    from PIL import Image
    import numpy as np
    RAPIDOCR_AVAILABLE = True
except ImportError:
    RAPIDOCR_AVAILABLE = False
    print("错误: RapidOCR未安装，请运行: pip install rapidocr-onnxruntime")
    exit(1)

from .config import config
from .storage import db_manager
from .vector_service import create_vector_service


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
        main()
        
    def stop(self):
        """停止OCR处理服务"""
        self.is_running = False
        
    def get_statistics(self):
        """获取OCR处理统计信息"""
        try:
            from .models import Screenshot, OCRResult
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
                    from .models import OCRResult, Screenshot
                    ocr_obj = session.query(OCRResult).filter(OCRResult.id == ocr_result_id).first()
                    screenshot_obj = session.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
                    
                    if ocr_obj:
                        success = vector_service.add_ocr_result(ocr_obj, screenshot_obj)
                        if success:
                            logging.debug(f"OCR结果已添加到向量数据库: {ocr_result_id}")
                        else:
                            logging.warning(f"向量数据库添加失败: {ocr_result_id}")
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


def setup_logging():
    """设置日志"""
    log_dir = os.path.join(config.base_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'simple_ocr.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def main():
    """主函数"""
    print("LifeTrace 简化OCR处理器启动...")
    
    # 设置日志
    setup_logging()
    
    # 检查配置
    if not os.path.exists(config.database_path):
        print(f"错误: 数据库未初始化，请先运行: lifetrace init")
        return
    
    # 初始化RapidOCR
    print("正在初始化RapidOCR引擎...")
    try:
        ocr = RapidOCR()
        print("RapidOCR引擎初始化成功")
    except Exception as e:
        print(f"RapidOCR初始化失败: {e}")
        return
    
    # 初始化向量数据库服务
    print("正在初始化向量数据库服务...")
    vector_service = create_vector_service(config, db_manager)
    if vector_service.is_enabled():
        print("向量数据库服务已启用")
    else:
        print("向量数据库服务未启用或不可用")
    
    # 设置监控文件夹
    screenshot_dir = config.screenshots_dir
    print(f"监控目录: {screenshot_dir}")
    
    # 确保目录存在
    os.makedirs(screenshot_dir, exist_ok=True)
    
    # 已处理文件记录
    processed_files = set()
    
    print("开始监控截图文件...")
    print("按 Ctrl+C 停止服务")
    
    try:
        while True:
            try:
                # 获取文件夹下所有文件
                if not os.path.exists(screenshot_dir):
                    time.sleep(1)
                    continue
                
                files = os.listdir(screenshot_dir)
                
                # 只处理图片文件
                image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                
                if image_files:
                    # 找到最新的文件
                    latest_file = max(image_files, key=lambda f: os.path.getmtime(os.path.join(screenshot_dir, f)))
                    latest_file_path = os.path.join(screenshot_dir, latest_file)
                    
                    # 检查是否已处理过
                    if latest_file_path in processed_files:
                        time.sleep(0.5)
                        continue
                    
                    # 检查是否已有对应的txt文件
                    txt_file = 'ocr_' + os.path.splitext(latest_file)[0] + '.txt'
                    txt_file_path = os.path.join(screenshot_dir, txt_file)
                    
                    if txt_file in files:
                        # 已有OCR结果，标记为已处理
                        processed_files.add(latest_file_path)
                        continue
                    
                    # 进行OCR处理
                    if os.path.isfile(latest_file_path):
                        print(f"开始处理新截图: {latest_file}")
                        
                        # 记录开始时间
                        start_time = time.time()
                        
                        # 图像预处理优化（提高处理速度）
                        with Image.open(latest_file_path) as img:
                            img = img.convert("RGB")
                            # 缩放图像以提高处理速度
                            img.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
                            img_array = np.array(img)
                        
                        # 使用RapidOCR进行识别
                        result, _ = ocr(img_array)
                        
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
                        
                        # 保存结果到txt文件
                        with open(txt_file_path, 'w', encoding='utf-8') as f:
                            f.write(ocr_text)
                        
                        # 保存到数据库
                        ocr_result = {
                            'text_content': ocr_text,
                            'confidence': 0.8,  # 简化版使用固定置信度
                            'language': 'ch',
                            'processing_time': elapsed_time
                        }
                        save_to_database(latest_file_path, ocr_result, vector_service)
                        
                        # 标记为已处理
                        processed_files.add(latest_file_path)
                        
                        print(f'OCR处理完成: {txt_file}, 用时: {elapsed_time:.2f}秒')
                        
                        # 清理已处理文件记录（防止内存泄漏）
                        if len(processed_files) > 1000:
                            processed_files.clear()
                            print("清理已处理文件记录")
                
            except Exception as e:
                print(f'处理文件时出错: {str(e)}')
                logging.error(f'处理文件时出错: {str(e)}')
            
            # 每隔0.5秒检查一次
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n收到停止信号，正在退出...")
    except Exception as e:
        print(f"服务异常: {e}")
        logging.error(f"服务异常: {e}")
    finally:
        print("OCR服务已停止")


if __name__ == '__main__':
    main()