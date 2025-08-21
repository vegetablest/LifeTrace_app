#!/usr/bin/env python3
"""
多模态搜索问题诊断脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace.config import config
from lifetrace.storage import db_manager
from lifetrace.multimodal_vector_service import create_multimodal_vector_service
from lifetrace.multimodal_embedding import get_multimodal_embedding


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def test_multimodal_embedding():
    """测试多模态嵌入模块"""
    print("\n🔍 测试多模态嵌入模块...")
    
    try:
        # 测试嵌入器初始化
        embedding = get_multimodal_embedding()
        print(f"✓ 多模态嵌入器初始化成功")
        print(f"✓ 可用性: {embedding.is_available()}")
        
        if embedding.is_available():
            # 测试文本编码
            text_vector = embedding.encode_text("测试文本")
            if text_vector is not None:
                print(f"✓ 文本编码成功，向量维度: {text_vector.shape}")
            else:
                print("✗ 文本编码失败")
        
        return embedding.is_available()
        
    except Exception as e:
        print(f"✗ 多模态嵌入模块测试失败: {e}")
        return False


def test_multimodal_service():
    """测试多模态向量服务"""
    print("\n🔍 测试多模态向量服务...")
    
    try:
        # 创建多模态向量服务
        service = create_multimodal_vector_service(config, db_manager)
        print(f"✓ 多模态向量服务创建成功")
        print(f"✓ 服务启用状态: {service.is_enabled()}")
        
        if service.is_enabled():
            # 获取统计信息
            stats = service.get_stats()
            print(f"✓ 统计信息获取成功:")
            print(f"  - 多模态可用: {stats.get('multimodal_available')}")
            print(f"  - 文本权重: {stats.get('text_weight')}")
            print(f"  - 图像权重: {stats.get('image_weight')}")
            
            # 测试搜索功能
            try:
                results = service.multimodal_search(
                    query="测试查询",
                    top_k=5
                )
                print(f"✓ 多模态搜索测试成功，返回 {len(results)} 个结果")
            except Exception as search_error:
                print(f"✗ 多模态搜索测试失败: {search_error}")
        
        return service.is_enabled()
        
    except Exception as e:
        print(f"✗ 多模态向量服务测试失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n🔍 测试配置...")
    
    try:
        print(f"✓ 多模态启用: {config.get('multimodal.enabled')}")
        print(f"✓ 文本权重: {config.get('multimodal.text_weight')}")
        print(f"✓ 图像权重: {config.get('multimodal.image_weight')}")
        print(f"✓ 模型名称: {config.get('multimodal.model_name')}")
        print(f"✓ 向量数据库启用: {config.get('vector_db.enabled')}")
        
        return True
        
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False


def test_dependencies():
    """测试依赖包"""
    print("\n🔍 测试依赖包...")
    
    dependencies = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('clip', 'OpenAI CLIP'),
        ('PIL', 'Pillow'),
        ('numpy', 'NumPy')
    ]
    
    all_available = True
    
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✓ {name} 可用")
        except ImportError:
            print(f"✗ {name} 不可用")
            all_available = False
    
    return all_available


def main():
    """主函数"""
    setup_logging()
    
    print("🚀 LifeTrace 多模态搜索问题诊断")
    print("=" * 50)
    
    # 测试步骤
    tests = [
        ("依赖包", test_dependencies),
        ("配置", test_config),
        ("多模态嵌入", test_multimodal_embedding),
        ("多模态服务", test_multimodal_service)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 测试 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    all_passed = True
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有测试通过！多模态功能应该可以正常工作。")
    else:
        print("\n⚠️  存在问题，请检查失败的测试项。")
        print("\n💡 建议解决方案:")
        print("1. 确保安装了所有多模态依赖: pip install -r requirements_multimodal.txt")
        print("2. 检查配置文件中的多模态设置")
        print("3. 确保有足够的内存和存储空间")
        print("4. 检查网络连接（首次运行需要下载模型）")


if __name__ == '__main__':
    main()