#!/usr/bin/env python3
"""
测试语义搜索修复效果
"""

import os
import sys
import time
import logging
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace.config import config


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def test_server_running(base_url="http://localhost:8840"):
    """测试服务器是否运行"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ LifeTrace 服务器正在运行")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {e}")
        return False


def test_vector_database_status(base_url="http://localhost:8840"):
    """测试向量数据库状态"""
    try:
        response = requests.get(f"{base_url}/api/vector-stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 向量数据库状态: {stats}")
            
            if stats.get('enabled'):
                print(f"  - 状态: 已启用")
                print(f"  - 文档数量: {stats.get('document_count', 0)}")
                print(f"  - 集合名称: {stats.get('collection_name', 'N/A')}")
                return True
            else:
                print(f"  - 状态: 未启用")
                print(f"  - 错误: {stats.get('error', '无')}")
                return False
        else:
            print(f"❌ 向量数据库状态获取失败: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 向量数据库状态请求失败: {e}")
        return False


def test_semantic_search_api(base_url="http://localhost:8840"):
    """测试语义搜索API"""
    test_queries = [
        "代码编程",
        "文件管理",
        "浏览器",
        "设置配置"
    ]
    
    print("\n🔍 测试语义搜索API...")
    
    for query in test_queries:
        print(f"\n测试查询: '{query}'")
        
        try:
            payload = {
                "query": query,
                "top_k": 5,
                "use_rerank": True,
                "retrieve_k": 15
            }
            
            response = requests.post(
                f"{base_url}/api/semantic-search",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"  ✅ 找到 {len(results)} 个结果")
                
                for i, result in enumerate(results[:3]):  # 只显示前3个
                    score = result.get('score', 0)
                    text = result.get('text', '')[:50]
                    metadata = result.get('metadata', {})
                    app_name = metadata.get('application', 'Unknown')
                    
                    print(f"    {i+1}. [{app_name}] 分数: {score:.3f} - {text}...")
                    
            elif response.status_code == 503:
                print(f"  ❌ 向量数据库服务不可用")
                return False
            else:
                print(f"  ❌ 搜索失败: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ 搜索请求失败: {e}")
            return False
    
    return True


def test_traditional_search_api(base_url="http://localhost:8840"):
    """测试传统搜索API（对比）"""
    print("\n🔍 测试传统搜索API...")
    
    try:
        payload = {
            "query": "代码",
            "limit": 5
        }
        
        response = requests.post(
            f"{base_url}/api/search",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"  ✅ 传统搜索找到 {len(results)} 个结果")
            return True
        else:
            print(f"  ❌ 传统搜索失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 传统搜索请求失败: {e}")
        return False


def test_vector_sync(base_url="http://localhost:8840"):
    """测试向量数据库同步"""
    print("\n🔄 测试向量数据库同步...")
    
    try:
        response = requests.post(
            f"{base_url}/api/vector-sync",
            json={"limit": 10},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            synced_count = result.get('synced_count', 0)
            print(f"  ✅ 同步成功，处理了 {synced_count} 条记录")
            return True
        else:
            print(f"  ❌ 同步失败: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ 同步请求失败: {e}")
        return False


def test_web_interface(base_url="http://localhost:8840"):
    """测试Web界面"""
    print("\n🌐 测试Web界面...")
    
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            
            # 检查关键元素
            checks = [
                ("搜索类型切换", "search-type-btn" in html_content),
                ("语义搜索选项", "semantic-options" in html_content),
                ("向量数据库状态", "vector-status" in html_content),
                ("分数显示", "score-badge" in html_content),
                ("语义搜索函数", "performSemanticSearch" in html_content),
                ("向量状态加载", "loadVectorStatus" in html_content)
            ]
            
            print("  检查Web界面组件:")
            all_passed = True
            for check_name, passed in checks:
                status = "✅" if passed else "❌"
                print(f"    {status} {check_name}")
                if not passed:
                    all_passed = False
            
            return all_passed
        else:
            print(f"  ❌ Web界面访问失败: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Web界面请求失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 LifeTrace 语义搜索修复效果测试")
    print("=" * 50)
    
    setup_logging()
    
    base_url = "http://localhost:8840"
    
    # 测试序列
    tests = [
        ("服务器连接", test_server_running),
        ("向量数据库状态", test_vector_database_status),
        ("Web界面组件", test_web_interface),
        ("传统搜索API", test_traditional_search_api),
        ("向量数据库同步", test_vector_sync),
        ("语义搜索API", test_semantic_search_api),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func(base_url)
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name} - 通过")
            else:
                print(f"❌ {test_name} - 失败")
                
        except Exception as e:
            print(f"❌ {test_name} - 异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print(f"\n{'='*50}")
    print("📊 测试总结:")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！语义搜索功能修复成功！")
        print("\n📋 使用指南:")
        print("1. 打开浏览器访问: http://localhost:8840")
        print("2. 点击页面上的 '语义搜索' 按钮")
        print("3. 输入搜索关键词，例如: '代码', '文件', '浏览器'")
        print("4. 查看带有相关性分数的搜索结果")
        print("5. 语义搜索结果会显示 'AI' 标记和相关度分数")
    else:
        print("⚠️  部分测试失败，请检查:")
        print("1. 确保LifeTrace服务正在运行: lifetrace start")
        print("2. 确保向量数据库依赖已安装: pip install -r requirements_vector.txt")
        print("3. 确保数据库已初始化: lifetrace init")
        print("4. 检查配置文件中 vector_db.enabled = true")


if __name__ == '__main__':
    main()