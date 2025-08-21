import os
import time
import json
import logging
from pathlib import Path
from PIL import Image
import numpy as np
from rapidocr_onnxruntime import RapidOCR

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 最大缩略图尺寸，用于优化性能
MAX_THUMBNAIL_SIZE = (1920, 1920)

class RapidOCRProcessor:
    def __init__(self, screenshots_dir=None):
        # 初始化RapidOCR，使用优化配置
        config_params = {
            "Global.width_height_ratio": 40,
        }
        self.ocr = RapidOCR(params=config_params)
        
        # 设置截图目录
        if screenshots_dir is None:
            # 使用默认路径
            home_dir = Path.home()
            self.screenshots_dir = home_dir / ".lifetrace" / "screenshots"
        else:
            self.screenshots_dir = Path(screenshots_dir)
            
        # 确保目录存在
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"监控目录: {self.screenshots_dir}")
        logger.info("RapidOCR 初始化完成")
        
        # 记录已处理的文件
        self.processed_files = set()
        
    def convert_ocr_results(self, results):
        """转换OCR结果格式"""
        if results is None:
            return []
        
        converted = []
        for result in results:
            item = {
                "dt_boxes": result[0].tolist() if hasattr(result[0], 'tolist') else result[0],
                "rec_txt": result[1],
                "score": float(result[2])
            }
            converted.append(item)
        return converted
    
    def process_image(self, image_path):
        """处理单个图像文件"""
        try:
            start_time = time.time()
            
            # 打开并优化图像
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                # 缩放图像以提高处理速度
                img.thumbnail(MAX_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
                img_array = np.array(img)
            
            # 执行OCR
            results, _ = self.ocr(img_array)
            
            # 转换结果格式
            converted_results = self.convert_ocr_results(results)
            
            # 过滤低置信度结果
            filtered_results = [r for r in converted_results if r['score'] > 0.5]
            
            # 保存结果到文件
            output_path = self.save_ocr_result(image_path, converted_results)
            
            end_time = time.time()
            inference_time = end_time - start_time
            
            # 记录处理结果
            total_results = len(converted_results)
            high_conf_results = len(filtered_results)
            
            logger.info(f"处理完成: {image_path.name}")
            logger.info(f"推理时间: {inference_time:.2f}秒")
            logger.info(f"识别结果: {high_conf_results}/{total_results} (置信度>0.5)")
            
            if filtered_results:
                # 显示前几个高置信度结果
                preview_texts = [f"{r['rec_txt']}({r['score']:.2f})" for r in filtered_results[:5]]
                logger.info(f"识别文本预览: {', '.join(preview_texts)}")
            
            return converted_results
            
        except Exception as e:
            logger.error(f"处理图像 {image_path} 时出错: {str(e)}")
            return None
    
    def save_ocr_result(self, image_path, ocr_results):
        """保存OCR结果到文件"""
        # 生成输出文件名
        image_path = Path(image_path)
        output_filename = f"ocr_{image_path.stem}.txt"
        output_path = image_path.parent / output_filename
        
        try:
            # 保存为JSON格式，便于后续处理
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(ocr_results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"OCR结果已保存到: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"保存OCR结果时出错: {str(e)}")
            return None
    
    def get_latest_image(self):
        """获取最新的图像文件"""
        try:
            # 支持的图像格式
            image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
            
            # 查找所有图像文件
            image_files = []
            for ext in image_extensions:
                image_files.extend(self.screenshots_dir.glob(f'*{ext}'))
                image_files.extend(self.screenshots_dir.glob(f'*{ext.upper()}'))
            
            if not image_files:
                return None
            
            # 按修改时间排序，获取最新的
            latest_file = max(image_files, key=lambda f: f.stat().st_mtime)
            
            # 检查是否已处理过
            if latest_file in self.processed_files:
                return None
                
            return latest_file
            
        except Exception as e:
            logger.error(f"获取最新图像时出错: {str(e)}")
            return None
    
    def run_continuous(self, check_interval=0.5):
        """持续监控模式"""
        logger.info("开始持续监控模式...")
        logger.info(f"检查间隔: {check_interval}秒")
        
        try:
            while True:
                latest_image = self.get_latest_image()
                
                if latest_image:
                    logger.info(f"发现新图像: {latest_image.name}")
                    result = self.process_image(latest_image)
                    
                    if result is not None:
                        # 标记为已处理
                        self.processed_files.add(latest_image)
                    
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("收到停止信号，退出监控...")
        except Exception as e:
            logger.error(f"监控过程中出错: {str(e)}")
    
    def process_single_file(self, file_path):
        """处理单个文件"""
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return None
            
        logger.info(f"处理单个文件: {file_path}")
        return self.process_image(file_path)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='RapidOCR 图像文字识别工具')
    parser.add_argument('--dir', type=str, help='截图目录路径')
    parser.add_argument('--file', type=str, help='处理单个文件')
    parser.add_argument('--interval', type=float, default=0.5, help='监控检查间隔(秒)')
    
    args = parser.parse_args()
    
    # 创建OCR处理器
    processor = RapidOCRProcessor(screenshots_dir=args.dir)
    
    if args.file:
        # 处理单个文件
        processor.process_single_file(args.file)
    else:
        # 持续监控模式
        processor.run_continuous(check_interval=args.interval)

if __name__ == "__main__":
    main()