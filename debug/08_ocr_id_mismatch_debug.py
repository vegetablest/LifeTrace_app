#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试OCR ID不匹配问题
通过API检查文本和图像向量数据库中的OCR ID格式
"""

import requests
import json

def main():
    try:
        base_url = "http://localhost:8843"
        
        print("🔍 通过API检查多模态搜索结果...")
        
        # 测试不同权重的多模态搜索
        test_cases = [
            {"text_weight": 1.0, "image_weight": 0.0, "name": "纯文本搜索"},
            {"text_weight": 0.0, "image_weight": 1.0, "name": "纯图像搜索"},
            {"text_weight": 0.5, "image_weight": 0.5, "name": "平衡搜索"}
        ]
        
        for case in test_cases:
            print(f"\n📊 {case['name']} (text_weight={case['text_weight']}, image_weight={case['image_weight']}):")
            
            response = requests.post(f"{base_url}/api/multimodal-search", json={
                "query": "连接",
                "top_k": 5,
                "text_weight": case['text_weight'],
                "image_weight": case['image_weight']
            })
            
            if response.status_code == 200:
                results = response.json()
                print(f"  找到 {len(results)} 个结果")
                
                for i, result in enumerate(results[:3]):
                    print(f"  结果 {i+1}:")
                    print(f"    ID: {result.get('id')}")
                    print(f"    OCR结果ID: {result.get('ocr_result', {}).get('id')}")
                    print(f"    text_score: {result.get('text_score', 0):.3f}")
                    print(f"    image_score: {result.get('image_score', 0):.3f}")
                    print(f"    combined_score: {result.get('combined_score', 0):.3f}")
                    
                    # 检查元数据
                    metadata = result.get('metadata', {})
                    if metadata:
                        print(f"    元数据OCR ID: {metadata.get('ocr_result_id')} (类型: {type(metadata.get('ocr_result_id'))})")
                    print()
            else:
                print(f"  ❌ API调用失败: {response.status_code}")
        
        # 获取统计信息
        print("\n📊 获取多模态统计信息...")
        response = requests.get(f"{base_url}/api/multimodal-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"文本数据库文档数: {stats.get('text_db_count', 0)}")
            print(f"图像数据库文档数: {stats.get('image_db_count', 0)}")
        
        # 测试纯文本搜索
        print("\n🔍 测试纯文本向量搜索...")
        response = requests.post(f"{base_url}/api/search", json={
            "query": "连接",
            "top_k": 3
        })
        
        if response.status_code == 200:
            results = response.json()
            print(f"找到 {len(results)} 个文本搜索结果")
            for i, result in enumerate(results):
                print(f"  文本结果 {i+1}:")
                print(f"    ID: {result.get('id')}")
                print(f"    距离: {result.get('distance', 'N/A')}")
                metadata = result.get('metadata', {})
                print(f"    元数据OCR ID: {metadata.get('ocr_result_id')} (类型: {type(metadata.get('ocr_result_id'))})")
                print()
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()