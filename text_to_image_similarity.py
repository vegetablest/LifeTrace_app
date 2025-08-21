#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本与图像相似度计算程序

输入文本，返回与数据库中所有图像的相似度分数。
基于CLIP模型的多模态语义搜索实现。
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional
import argparse

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lifetrace.config import config
from lifetrace.storage import DatabaseManager
from lifetrace.multimodal_vector_service import MultimodalVectorService
from lifetrace.models import OCRResult, Screenshot


class TextImageSimilarityCalculator:
    """文本与图像相似度计算器"""
    
    def __init__(self):
        """初始化计算器"""
        self.logger = logging.getLogger(__name__)
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()
        
        # 初始化多模态向量服务
        self.multimodal_service = MultimodalVectorService(config, self.db_manager)
        
        # 确保服务已启用
        if not self.multimodal_service.is_enabled():
            raise RuntimeError("多模态向量服务未启用，请检查配置")
    
    def calculate_similarities(self, query_text: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """计算文本与所有图像的相似度
        
        Args:
            query_text: 查询文本
            limit: 限制返回结果数量，None表示返回所有结果
            
        Returns:
            相似度结果列表，按相似度降序排列
        """
        if not query_text or not query_text.strip():
            return []
        
        try:
            # 生成查询文本的嵌入
            query_embedding = self.multimodal_service.multimodal_embedding.encode_text(query_text)
            if query_embedding is None:
                self.logger.error("无法生成查询文本的嵌入")
                return []
            
            # 获取所有图像向量
            image_results = self._get_all_image_similarities(query_embedding, limit)
            
            # 增强结果数据
            enhanced_results = []
            for result in image_results:
                enhanced = self._enhance_image_result(result)
                if enhanced:
                    enhanced_results.append(enhanced)
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"计算相似度失败: {e}")
            return []
    
    def _get_all_image_similarities(self, query_embedding, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """获取与所有图像的相似度"""
        try:
            # 获取图像向量数据库
            if not self.multimodal_service.image_vector_db:
                self.logger.error("图像向量数据库未初始化")
                return []
            
            collection = self.multimodal_service.image_vector_db.collection
            
            # 获取数据库中的文档总数
            total_count = collection.count()
            if total_count == 0:
                self.logger.warning("图像向量数据库中没有数据")
                return []
            
            # 设置查询数量
            query_limit = min(limit or total_count, total_count)
            
            # 执行向量搜索
            results = collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=query_limit,
                include=['documents', 'metadatas', 'distances']
            )
            
            # 格式化结果
            formatted_results = []
            for i in range(len(results['ids'][0])):
                distance = results['distances'][0][i] if results['distances'] else 1.0
                # 使用倒数公式计算相似度
                similarity = 1.0 / (1.0 + distance)
                
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                    'distance': distance,
                    'similarity': similarity
                })
            
            # 按相似度降序排序
            formatted_results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"获取图像相似度失败: {e}")
            return []
    
    def _enhance_image_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """增强图像结果数据"""
        try:
            metadata = result.get('metadata', {})
            ocr_result_id = metadata.get('ocr_result_id')
            
            if not ocr_result_id:
                return None
            
            # 从数据库获取完整信息
            with self.db_manager.get_session() as session:
                ocr_result = session.query(OCRResult).filter(
                    OCRResult.id == ocr_result_id
                ).first()
                
                if not ocr_result:
                    return None
                
                screenshot = session.query(Screenshot).filter(
                    Screenshot.id == ocr_result.screenshot_id
                ).first()
                
                # 构建增强结果
                enhanced = {
                    'ocr_result_id': ocr_result_id,
                    'similarity': result['similarity'],
                    'distance': result['distance'],
                    'image_path': result.get('document', ''),
                    'text_content': ocr_result.text_content or '',
                    'confidence': ocr_result.confidence,
                    'language': ocr_result.language or 'unknown',
                    'created_at': ocr_result.created_at.isoformat() if ocr_result.created_at else None
                }
                
                if screenshot:
                    enhanced.update({
                        'screenshot_id': screenshot.id,
                        'screenshot_path': screenshot.file_path,
                        'screenshot_timestamp': screenshot.created_at.isoformat() if screenshot.created_at else None,
                        'application': screenshot.app_name,
                        'window_title': screenshot.window_title,
                        'width': screenshot.width,
                        'height': screenshot.height
                    })
                
                return enhanced
                
        except Exception as e:
            self.logger.error(f"增强图像结果失败: {e}")
            return None
    
    def print_results(self, results: List[Dict[str, Any]], show_details: bool = False):
        """打印结果"""
        if not results:
            print("没有找到相关图像")
            return
        
        print(f"\n找到 {len(results)} 个相关图像:\n")
        print("-" * 80)
        
        for i, result in enumerate(results, 1):
            similarity = result['similarity']
            distance = result['distance']
            ocr_id = result['ocr_result_id']
            image_path = result.get('image_path', 'N/A')
            text_content = result.get('text_content', '')[:100]  # 限制文本长度
            
            print(f"{i:3d}. OCR ID: {ocr_id}")
            print(f"     相似度: {similarity:.4f} (距离: {distance:.4f})")
            print(f"     图像路径: {image_path}")
            
            if text_content:
                print(f"     文本内容: {text_content}{'...' if len(result.get('text_content', '')) > 100 else ''}")
            
            if show_details:
                print(f"     应用程序: {result.get('application', 'N/A')}")
                print(f"     窗口标题: {result.get('window_title', 'N/A')}")
                print(f"     创建时间: {result.get('created_at', 'N/A')}")
                print(f"     置信度: {result.get('confidence', 'N/A')}")
                print(f"     语言: {result.get('language', 'N/A')}")
            
            print("-" * 80)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='计算文本与数据库中所有图像的相似度')
    parser.add_argument('query', help='查询文本')
    parser.add_argument('--limit', type=int, help='限制返回结果数量')
    parser.add_argument('--details', action='store_true', help='显示详细信息')
    parser.add_argument('--verbose', action='store_true', help='详细日志输出')
    
    args = parser.parse_args()
    
    # 配置日志
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # 创建计算器
        calculator = TextImageSimilarityCalculator()
        
        print(f"查询文本: {args.query}")
        
        # 计算相似度
        results = calculator.calculate_similarities(args.query, args.limit)
        
        # 打印结果
        calculator.print_results(results, args.details)
        
    except Exception as e:
        print(f"程序执行失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()