#!/usr/bin/env python3
"""
测试多模态搜索修复效�?"""

import os
import sys
import requests
import json
import time
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_server_status(base_url):
    """测试服务器状�?""
    print("\n🔍 测试服务器状�?..")
    try:
        response = requests.get(f"{base_url}/api/stats", timeout=5)
        if response.status_code == 200:
            print("�?服务器运行正�?)
            return True
        else:
            print(f"�?服务器响应异�? {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"�?无法连接到服务器: {e}")
        return False


def test_multimodal_stats(base_url):
    """测试多模态统计信�?""
    print("\n🔍 测试多模态统计信�?..")
    try:
        response = requests.get(f"{base_url}/api/multimodal-stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print("�?多模态统计信息获取成�?")
            print(f"  - 启用状�? {stats.get('enabled')}")
            print(f"  - 多模态可�? {stats.get('multimodal_available')}")
            print(f"  - 文本权重: {stats.get('text_weight')}")
            print(f"  - 图像权重: {stats.get('image_weight')}")
            
            text_db = stats.get('text_database', {})
            image_db = stats.get('image_database', {})
            print(f"  - 文本数据库文档数: {text_db.get('document_count', 0)}")
            print(f"  - 图像数据库文档数: {image_db.get('document_count', 0)}")
            
            if stats.get('error'):
                print(f"  - 错误: {stats.get('error')}")
                return False
            
            return stats.get('enabled', False) and stats.get('multimodal_available', False)
        else:
            print(f"�?获取多模态统计信息失�? {response.status_code}")
            if response.text:
                print(f"  错误详情: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"�?请求多模态统计信息失�? {e}")
        return False


def test_multimodal_search(base_url):
    """测试多模态搜索API"""
    print("\n🔍 测试多模态搜索API...")
    
    test_queries = [
        "测试查询",
        "文档",
        "图片",
        "screenshot",
        "application"
    ]
    
    success_count = 0
    
    for query in test_queries:
        try:
            payload = {
                "query": query,
                "top_k": 5,
                "text_weight": 0.6,
                "image_weight": 0.4
            }
            
            response = requests.post(
                f"{base_url}/api/multimodal-search",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"�?查询 '{query}' 成功，返�?{len(results)} 个结�?)
                
                # 显示第一个结果的详细信息（如果有�?                if results:
                    first_result = results[0]
                    print(f"  - 第一个结果综合得�? {first_result.get('combined_score', 0):.4f}")
                    print(f"  - 文本得分: {first_result.get('text_score', 0):.4f}")
                    print(f"  - 图像得分: {first_result.get('image_score', 0):.4f}")
                    text_preview = first_result.get('text', '')[:100]
                    if text_preview:
                        print(f"  - 文本预览: {text_preview}...")
                
                success_count += 1
            else:
                print(f"�?查询 '{query}' 失败: {response.status_code}")
                if response.text:
                    print(f"  错误详情: {response.text}")
                    
        except requests.exceptions.RequestException as e:
            print(f"�?查询 '{query}' 请求失败: {e}")
        except Exception as e:
            print(f"�?查询 '{query}' 处理失败: {e}")
    
    print(f"\n📊 多模态搜索测试结�? {success_count}/{len(test_queries)} 成功")
    return success_count == len(test_queries)


def test_semantic_search_comparison(base_url):
    """对比语义搜索和多模态搜�?""
    print("\n🔍 对比语义搜索和多模态搜�?..")
    
    query = "测试文档"
    
    try:
        # 测试语义搜索
        semantic_payload = {
            "query": query,
            "top_k": 5
        }
        
        semantic_response = requests.post(
            f"{base_url}/api/semantic-search",
            json=semantic_payload,
            timeout=10
        )
        
        # 测试多模态搜�?        multimodal_payload = {
            "query": query,
            "top_k": 5,
            "text_weight": 0.6,
            "image_weight": 0.4
        }
        
        multimodal_response = requests.post(
            f"{base_url}/api/multimodal-search",
            json=multimodal_payload,
            timeout=15
        )
        
        semantic_success = semantic_response.status_code == 200
        multimodal_success = multimodal_response.status_code == 200
        
        print(f"�?语义搜索: {'成功' if semantic_success else '失败'}")
        print(f"�?多模态搜�? {'成功' if multimodal_success else '失败'}")
        
        if semantic_success and multimodal_success:
            semantic_results = semantic_response.json()
            multimodal_results = multimodal_response.json()
            
            print(f"  - 语义搜索结果�? {len(semantic_results)}")
            print(f"  - 多模态搜索结果数: {len(multimodal_results)}")
            
            return True
        
        return False
        
    except Exception as e:
        print(f"�?对比测试失败: {e}")
        return False


def main():
    """主函�?""
    print("🚀 LifeTrace 多模态搜索修复验�?)
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8843"
    
    # 测试步骤
    tests = [
        ("服务器状�?, lambda: test_server_status(base_url)),
        ("多模态统�?, lambda: test_multimodal_stats(base_url)),
        ("多模态搜�?, lambda: test_multimodal_search(base_url)),
        ("搜索对比", lambda: test_semantic_search_comparison(base_url))
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 测试 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"�?{test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    all_passed = True
    for test_name, result in results:
        status = "�?通过" if result else "�?失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！多模态搜索修复成功�?)
        print("\n�?现在可以正常使用多模态搜索功能了�?)
    else:
        print("\n⚠️  部分测试失败，请检查：")
        print("1. 确保 LifeTrace 服务器正在运�?)
        print("2. 检查服务器日志中的错误信息")
        print("3. 确保多模态依赖已正确安装")


if __name__ == '__main__':
    main()
