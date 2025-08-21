#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本与图像相似度计算程序演示脚本

展示程序的各种功能和使用场景。
"""

import sys
import os
import time
from typing import List, Dict, Any

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_to_image_similarity import TextImageSimilarityCalculator


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)


def print_separator():
    """打印分隔符"""
    print("-" * 60)


def demo_basic_search(calculator: TextImageSimilarityCalculator):
    """演示基本搜索功能"""
    print_header("基本搜索功能演示")
    
    queries = [
        "电脑",
        "网页",
        "浏览器",
        "文档"
    ]
    
    for query in queries:
        print(f"\n🔍 搜索: '{query}'")
        print_separator()
        
        results = calculator.calculate_similarities(query, limit=3)
        
        if results:
            for i, result in enumerate(results, 1):
                similarity = result['similarity']
                ocr_id = result['ocr_result_id']
                text_content = result.get('text_content', '')[:50]
                app_name = result.get('application', 'N/A')
                
                print(f"{i}. OCR ID: {ocr_id} | 相似度: {similarity:.4f} | 应用: {app_name}")
                if text_content:
                    print(f"   文本: {text_content}{'...' if len(result.get('text_content', '')) > 50 else ''}")
        else:
            print("❌ 没有找到相关结果")
        
        time.sleep(1)  # 短暂暂停


def demo_similarity_analysis(calculator: TextImageSimilarityCalculator):
    """演示相似度分析"""
    print_header("相似度分析演示")
    
    query = "电脑"
    print(f"\n📊 分析查询 '{query}' 的相似度分布")
    print_separator()
    
    results = calculator.calculate_similarities(query, limit=10)
    
    if not results:
        print("❌ 没有找到结果")
        return
    
    # 统计相似度分布
    high_sim = [r for r in results if r['similarity'] >= 0.7]
    medium_sim = [r for r in results if 0.5 <= r['similarity'] < 0.7]
    low_sim = [r for r in results if 0.3 <= r['similarity'] < 0.5]
    very_low_sim = [r for r in results if r['similarity'] < 0.3]
    
    print(f"📈 相似度分布统计:")
    print(f"🟢 高相似度 (≥0.7):   {len(high_sim)} 个")
    print(f"🟡 中等相似度 (0.5-0.7): {len(medium_sim)} 个")
    print(f"🟠 低相似度 (0.3-0.5):   {len(low_sim)} 个")
    print(f"🔴 很低相似度 (<0.3):   {len(very_low_sim)} 个")
    
    print(f"\n📋 详细结果:")
    for i, result in enumerate(results, 1):
        similarity = result['similarity']
        distance = result['distance']
        
        if similarity >= 0.7:
            level = "🟢"
        elif similarity >= 0.5:
            level = "🟡"
        elif similarity >= 0.3:
            level = "🟠"
        else:
            level = "🔴"
        
        print(f"{i:2d}. {level} 相似度: {similarity:.4f} (距离: {distance:.4f})")


def demo_application_analysis(calculator: TextImageSimilarityCalculator):
    """演示应用程序分析"""
    print_header("应用程序分析演示")
    
    query = "软件"
    print(f"\n🔍 搜索 '{query}' 并按应用程序分类")
    print_separator()
    
    results = calculator.calculate_similarities(query, limit=20)
    
    if not results:
        print("❌ 没有找到结果")
        return
    
    # 按应用程序分组
    app_groups = {}
    for result in results:
        app_name = result.get('application', 'Unknown')
        if app_name not in app_groups:
            app_groups[app_name] = []
        app_groups[app_name].append(result)
    
    print(f"📱 发现 {len(app_groups)} 个不同的应用程序:")
    
    for app_name, app_results in sorted(app_groups.items()):
        avg_similarity = sum(r['similarity'] for r in app_results) / len(app_results)
        print(f"\n🔸 {app_name} ({len(app_results)} 个结果, 平均相似度: {avg_similarity:.4f})")
        
        # 显示该应用的前3个结果
        for i, result in enumerate(sorted(app_results, key=lambda x: x['similarity'], reverse=True)[:3], 1):
            similarity = result['similarity']
            text_content = result.get('text_content', '')[:40]
            print(f"  {i}. 相似度: {similarity:.4f} | 文本: {text_content}{'...' if len(result.get('text_content', '')) > 40 else ''}")


def demo_text_content_analysis(calculator: TextImageSimilarityCalculator):
    """演示文本内容分析"""
    print_header("文本内容分析演示")
    
    queries = [
        "错误",
        "连接",
        "网页"
    ]
    
    for query in queries:
        print(f"\n🔍 搜索包含 '{query}' 相关内容的图像")
        print_separator()
        
        results = calculator.calculate_similarities(query, limit=5)
        
        if results:
            for i, result in enumerate(results, 1):
                similarity = result['similarity']
                text_content = result.get('text_content', '')
                
                # 高亮显示查询词
                highlighted_text = text_content
                if query in text_content:
                    highlighted_text = text_content.replace(query, f"**{query}**")
                
                print(f"{i}. 相似度: {similarity:.4f}")
                print(f"   文本: {highlighted_text[:100]}{'...' if len(text_content) > 100 else ''}")
        else:
            print("❌ 没有找到相关结果")
        
        time.sleep(0.5)


def demo_performance_test(calculator: TextImageSimilarityCalculator):
    """演示性能测试"""
    print_header("性能测试演示")
    
    queries = ["电脑", "网页", "文档", "软件", "浏览器"]
    
    print("⏱️ 测试多个查询的响应时间")
    print_separator()
    
    total_time = 0
    total_results = 0
    
    for i, query in enumerate(queries, 1):
        start_time = time.time()
        results = calculator.calculate_similarities(query, limit=5)
        end_time = time.time()
        
        query_time = end_time - start_time
        total_time += query_time
        total_results += len(results)
        
        print(f"{i}. 查询: '{query}' | 时间: {query_time:.3f}s | 结果: {len(results)} 个")
    
    avg_time = total_time / len(queries)
    print(f"\n📊 性能统计:")
    print(f"总查询时间: {total_time:.3f}s")
    print(f"平均查询时间: {avg_time:.3f}s")
    print(f"总结果数: {total_results} 个")
    print(f"平均结果数: {total_results / len(queries):.1f} 个/查询")


def demo_database_stats(calculator: TextImageSimilarityCalculator):
    """演示数据库统计"""
    print_header("数据库统计信息")
    
    try:
        # 图像向量数据库统计
        if calculator.multimodal_service.image_vector_db:
            collection = calculator.multimodal_service.image_vector_db.collection
            total_images = collection.count()
            print(f"📷 图像向量数据库: {total_images} 个图像")
        else:
            print("📷 图像向量数据库: 未初始化")
        
        # 关系数据库统计
        with calculator.db_manager.get_session() as session:
            from lifetrace.models import OCRResult, Screenshot
            ocr_count = session.query(OCRResult).count()
            screenshot_count = session.query(Screenshot).count()
            
            print(f"📝 OCR结果记录: {ocr_count} 条")
            print(f"📸 截图记录: {screenshot_count} 条")
            
            # 语言分布
            from sqlalchemy import func
            language_stats = session.query(
                OCRResult.language, 
                func.count(OCRResult.id)
            ).group_by(OCRResult.language).all()
            
            print(f"\n🌐 语言分布:")
            for lang, count in language_stats:
                lang_name = lang or 'unknown'
                print(f"  {lang_name}: {count} 条")
            
            # 应用程序分布
            app_stats = session.query(
                Screenshot.app_name,
                func.count(Screenshot.id)
            ).group_by(Screenshot.app_name).limit(10).all()
            
            print(f"\n📱 主要应用程序 (前10):")
            for app, count in app_stats:
                app_name = app or 'unknown'
                print(f"  {app_name}: {count} 个截图")
                
    except Exception as e:
        print(f"❌ 获取统计信息失败: {e}")


def main():
    """主演示函数"""
    print("🚀 LifeTrace 文本与图像相似度计算程序演示")
    print("正在初始化...")
    
    try:
        calculator = TextImageSimilarityCalculator()
        print("✓ 初始化完成！")
        
        # 运行各种演示
        demo_database_stats(calculator)
        demo_basic_search(calculator)
        demo_similarity_analysis(calculator)
        demo_application_analysis(calculator)
        demo_text_content_analysis(calculator)
        demo_performance_test(calculator)
        
        print_header("演示完成")
        print("🎉 所有演示已完成！")
        print("\n📚 使用说明:")
        print("• 运行 'python text_to_image_similarity.py \"查询文本\"' 进行单次查询")
        print("• 运行 'python interactive_image_similarity.py' 进入交互模式")
        print("• 查看 'text_to_image_similarity_usage.md' 了解详细用法")
        
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()