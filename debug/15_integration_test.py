#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前后端集成功能
"""

import requests
import json
import time

def test_api():
    """测试API功能"""
    base_url = "http://127.0.0.1:8842/api"
    
    print("=== LifeTrace API 测试 ===")
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"健康检查通过: {data}")
        else:
            print(f"健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"无法连接到后端服务: {e}")
        print("请先启动后端服务: python -m lifetrace.server")
        return
    
    # 2. 获取统计信息
    print("\n2. 获取统计信息...")
    try:
        response = requests.get(f"{base_url}/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ 统计信息: {stats}")
        else:
            print(f"✗ 获取统计信息失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取统计信息错误: {e}")
    
    # 3. 测试传统搜索
    print("\n3. 测试传统搜索...")
    try:
        search_data = {"query": "test", "limit": 5}
        response = requests.post(f"{base_url}/search", json=search_data)
        if response.status_code == 200:
            results = response.json()
            print(f"✓ 传统搜索成功，找到 {len(results)} 个结果")
            if results:
                print(f"  示例结果: {results[0].get('window_title', 'N/A')}")
        else:
            print(f"✗ 传统搜索失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 传统搜索错误: {e}")
    
    # 4. 测试语义搜索
    print("\n4. 测试语义搜索...")
    try:
        semantic_data = {"query": "编程", "top_k": 5}
        response = requests.post(f"{base_url}/semantic-search", json=semantic_data)
        if response.status_code == 200:
            results = response.json()
            print(f"✓ 语义搜索成功，找到 {len(results)} 个结果")
            if results:
                print(f"  示例结果相关度: {results[0].get('score', 0):.3f}")
        else:
            print(f"✗ 语义搜索失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 语义搜索错误: {e}")
    
    # 5. 测试多模态搜索
    print("\n5. 测试多模态搜索...")
    try:
        multimodal_data = {"query": "代码", "top_k": 5}
        response = requests.post(f"{base_url}/multimodal-search", json=multimodal_data)
        if response.status_code == 200:
            results = response.json()
            print(f"✓ 多模态搜索成功，找到 {len(results)} 个结果")
            if results:
                result = results[0]
                print(f"  示例结果综合分数: {result.get('combined_score', 0):.3f}")
                print(f"  文本分数: {result.get('text_score', 0):.3f}")
                print(f"  图像分数: {result.get('image_score', 0):.3f}")
        else:
            print(f"✗ 多模态搜索失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"✗ 多模态搜索错误: {e}")
    
    # 6. 获取向量数据库状态
    print("\n6. 检查向量数据库状态...")
    try:
        response = requests.get(f"{base_url}/vector-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ 向量数据库状态: 启用={stats.get('enabled')}, 文档数={stats.get('document_count')}")
        else:
            print(f"✗ 获取向量数据库状态失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取向量数据库状态错误: {e}")
    
    # 7. 获取多模态状态
    print("\n7. 检查多模态功能状态...")
    try:
        response = requests.get(f"{base_url}/multimodal-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✓ 多模态功能状态: 启用={stats.get('enabled')}, 可用={stats.get('multimodal_available')}")
            print(f"  文本权重: {stats.get('text_weight')}, 图像权重: {stats.get('image_weight')}")
        else:
            print(f"✗ 获取多模态状态失败: {response.status_code}")
    except Exception as e:
        print(f"✗ 获取多模态状态错误: {e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_api()