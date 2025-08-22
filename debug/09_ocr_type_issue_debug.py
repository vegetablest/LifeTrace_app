#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OCR ID类型不匹配问�?检查文本和图像向量搜索结果中OCR ID的类�?"""

import requests
import json
from lifetrace_backend.multimodal_embedding import get_multimodal_embedding
from lifetrace_backend.multimodal_vector_service import MultimodalVectorService
from lifetrace_backend.config import config
from lifetrace_backend.storage import DatabaseManager

def main():
    try:
        print("🔍 调试OCR ID类型匹配问题...")
        
        # 获取数据库管理器和多模态向量服�?        db_manager = DatabaseManager(config)
        multimodal_service = MultimodalVectorService(config, db_manager)
        
        if not multimodal_service.is_enabled():
            print("�?多模态服务未启用")
            return
        
        # 获取多模态嵌入器
        embedder = multimodal_service.multimodal_embedding
        
        # 生成查询嵌入
        query = "连接"
        query_embedding = embedder.encode_text(query)
        
        print(f"\n📝 搜索查询: '{query}'")
        
        # 1. 直接搜索文本向量数据�?        print("\n🔍 直接搜索文本向量数据�?..")
        text_results = multimodal_service._search_text_with_embedding(query_embedding, 5)
        print(f"找到 {len(text_results)} 个文本结�?)
        
        text_ocr_ids = []
        for i, result in enumerate(text_results[:3]):
            metadata = result.get('metadata', {})
            ocr_id = metadata.get('ocr_result_id')
            text_ocr_ids.append(ocr_id)
            print(f"  文本结果 {i+1}:")
            print(f"    ID: {result.get('id')}")
            print(f"    OCR ID: {ocr_id} (类型: {type(ocr_id)})")
            print(f"    距离: {result.get('distance')}")
            print()
        
        # 2. 直接搜索图像向量数据�?        print("🖼�?直接搜索图像向量数据�?..")
        image_results = multimodal_service._search_image_with_text(query_embedding, 5)
        print(f"找到 {len(image_results)} 个图像结�?)
        
        image_ocr_ids = []
        for i, result in enumerate(image_results[:3]):
            metadata = result.get('metadata', {})
            ocr_id = metadata.get('ocr_result_id')
            image_ocr_ids.append(ocr_id)
            print(f"  图像结果 {i+1}:")
            print(f"    ID: {result.get('id')}")
            print(f"    OCR ID: {ocr_id} (类型: {type(ocr_id)})")
            print(f"    距离: {result.get('distance')}")
            print()
        
        # 3. 检查OCR ID匹配情况
        print("🔍 检查OCR ID匹配情况...")
        print(f"文本OCR IDs: {text_ocr_ids}")
        print(f"图像OCR IDs: {image_ocr_ids}")
        
        # 检查类型转换后的匹�?        text_ocr_ids_str = [str(x) if x is not None else None for x in text_ocr_ids]
        image_ocr_ids_str = [str(x) if x is not None else None for x in image_ocr_ids]
        
        print(f"文本OCR IDs (字符�?: {text_ocr_ids_str}")
        print(f"图像OCR IDs (字符�?: {image_ocr_ids_str}")
        
        # 找到匹配的ID
        matching_ids = set(text_ocr_ids_str) & set(image_ocr_ids_str)
        print(f"匹配的OCR IDs: {matching_ids}")
        
        # 4. 测试合并逻辑
        print("\n🔧 测试合并逻辑...")
        merged_results = multimodal_service._merge_multimodal_results(
            text_results, image_results, 0.5, 0.5, 5
        )
        
        print(f"合并后结果数: {len(merged_results)}")
        for i, result in enumerate(merged_results[:3]):
            print(f"  合并结果 {i+1}:")
            print(f"    OCR ID: {result.get('ocr_result_id')}")
            print(f"    文本分数: {result.get('text_score', 0):.3f}")
            print(f"    图像分数: {result.get('image_score', 0):.3f}")
            print(f"    综合分数: {result.get('combined_score', 0):.3f}")
            print()
        
        # 5. 模拟修复：统一OCR ID类型
        print("🛠�?测试修复方案：统一OCR ID类型...")
        
        # 修复文本结果
        fixed_text_results = []
        for result in text_results:
            fixed_result = result.copy()
            metadata = fixed_result.get('metadata', {}).copy()
            ocr_id = metadata.get('ocr_result_id')
            if ocr_id is not None:
                metadata['ocr_result_id'] = str(ocr_id)  # 统一转为字符�?            fixed_result['metadata'] = metadata
            fixed_text_results.append(fixed_result)
        
        # 修复图像结果
        fixed_image_results = []
        for result in image_results:
            fixed_result = result.copy()
            metadata = fixed_result.get('metadata', {}).copy()
            ocr_id = metadata.get('ocr_result_id')
            if ocr_id is not None:
                metadata['ocr_result_id'] = str(ocr_id)  # 统一转为字符�?            fixed_result['metadata'] = metadata
            fixed_image_results.append(fixed_result)
        
        # 重新合并
        fixed_merged_results = multimodal_service._merge_multimodal_results(
            fixed_text_results, fixed_image_results, 0.5, 0.5, 5
        )
        
        print(f"修复后合并结果数: {len(fixed_merged_results)}")
        for i, result in enumerate(fixed_merged_results[:3]):
            print(f"  修复后结�?{i+1}:")
            print(f"    OCR ID: {result.get('ocr_result_id')}")
            print(f"    文本分数: {result.get('text_score', 0):.3f}")
            print(f"    图像分数: {result.get('image_score', 0):.3f}")
            print(f"    综合分数: {result.get('combined_score', 0):.3f}")
            print()
        
    except Exception as e:
        print(f"�?错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
