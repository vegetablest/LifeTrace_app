#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互式文本与图像相似度计算程序

提供友好的交互界面，支持连续查询而无需重新加载模型。
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from text_to_image_similarity import TextImageSimilarityCalculator


class InteractiveImageSimilarity:
    """交互式图像相似度计算器"""
    
    def __init__(self):
        """初始化计算器"""
        print("正在初始化多模态搜索引擎...")
        try:
            self.calculator = TextImageSimilarityCalculator()
            print("✓ 初始化完成！")
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            sys.exit(1)
    
    def run(self):
        """运行交互式界面"""
        self.print_welcome()
        
        while True:
            try:
                # 获取用户输入
                query = input("\n请输入查询文本 (输入 'quit' 或 'exit' 退出): ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("再见！")
                    break
                
                if query.lower() in ['help', 'h', '?']:
                    self.print_help()
                    continue
                
                if query.lower() in ['stats', 'status']:
                    self.print_stats()
                    continue
                
                # 处理查询
                self.process_query(query)
                
            except KeyboardInterrupt:
                print("\n\n程序被用户中断")
                break
            except Exception as e:
                print(f"处理查询时出错: {e}")
    
    def process_query(self, query: str):
        """处理查询"""
        print(f"\n🔍 搜索: {query}")
        print("-" * 50)
        
        # 获取结果数量设置
        limit = self.get_result_limit()
        
        # 计算相似度
        results = self.calculator.calculate_similarities(query, limit)
        
        if not results:
            print("❌ 没有找到相关图像")
            return
        
        # 显示结果
        self.display_results(results, query)
    
    def get_result_limit(self) -> int:
        """获取结果数量限制"""
        try:
            limit_input = input("显示多少个结果？(默认5个，按回车使用默认值): ").strip()
            if not limit_input:
                return 5
            limit = int(limit_input)
            return max(1, min(limit, 50))  # 限制在1-50之间
        except ValueError:
            print("输入无效，使用默认值5")
            return 5
    
    def display_results(self, results: List[Dict[str, Any]], query: str):
        """显示搜索结果"""
        print(f"\n📊 找到 {len(results)} 个相关图像:\n")
        
        for i, result in enumerate(results, 1):
            similarity = result['similarity']
            distance = result['distance']
            ocr_id = result['ocr_result_id']
            image_path = result.get('image_path', 'N/A')
            text_content = result.get('text_content', '')[:80]  # 限制文本长度
            app_name = result.get('application', 'N/A')
            window_title = result.get('window_title', 'N/A')[:50]  # 限制标题长度
            
            # 相似度等级
            if similarity >= 0.7:
                level = "🟢 高"
            elif similarity >= 0.5:
                level = "🟡 中"
            elif similarity >= 0.3:
                level = "🟠 低"
            else:
                level = "🔴 很低"
            
            print(f"{i:2d}. 📷 OCR ID: {ocr_id}")
            print(f"    相似度: {similarity:.4f} {level}")
            print(f"    应用: {app_name}")
            if window_title != 'N/A':
                print(f"    窗口: {window_title}{'...' if len(result.get('window_title', '')) > 50 else ''}")
            if text_content:
                print(f"    文本: {text_content}{'...' if len(result.get('text_content', '')) > 80 else ''}")
            print(f"    路径: {os.path.basename(image_path)}")
            print()
        
        # 询问是否查看详细信息
        if len(results) > 0:
            detail_input = input("查看某个结果的详细信息？输入序号(1-{})，或按回车跳过: ".format(len(results))).strip()
            if detail_input.isdigit():
                idx = int(detail_input) - 1
                if 0 <= idx < len(results):
                    self.display_detailed_result(results[idx], idx + 1)
    
    def display_detailed_result(self, result: Dict[str, Any], index: int):
        """显示详细结果信息"""
        print(f"\n📋 详细信息 - 结果 #{index}")
        print("=" * 60)
        
        print(f"OCR ID: {result['ocr_result_id']}")
        print(f"相似度: {result['similarity']:.6f}")
        print(f"距离: {result['distance']:.6f}")
        print(f"图像路径: {result.get('image_path', 'N/A')}")
        print(f"应用程序: {result.get('application', 'N/A')}")
        print(f"窗口标题: {result.get('window_title', 'N/A')}")
        print(f"创建时间: {result.get('created_at', 'N/A')}")
        print(f"置信度: {result.get('confidence', 'N/A')}")
        print(f"语言: {result.get('language', 'N/A')}")
        print(f"截图ID: {result.get('screenshot_id', 'N/A')}")
        
        text_content = result.get('text_content', '')
        if text_content:
            print(f"\n📝 完整文本内容:")
            print("-" * 40)
            print(text_content)
        
        print("=" * 60)
    
    def print_stats(self):
        """显示统计信息"""
        print("\n📈 系统统计信息")
        print("-" * 30)
        
        try:
            # 获取图像数据库统计
            if self.calculator.multimodal_service.image_vector_db:
                collection = self.calculator.multimodal_service.image_vector_db.collection
                total_images = collection.count()
                print(f"图像数据库: {total_images} 个图像")
            else:
                print("图像数据库: 未初始化")
            
            # 获取数据库统计
            with self.calculator.db_manager.get_session() as session:
                from lifetrace.models import OCRResult, Screenshot
                ocr_count = session.query(OCRResult).count()
                screenshot_count = session.query(Screenshot).count()
                print(f"OCR结果: {ocr_count} 条")
                print(f"截图记录: {screenshot_count} 条")
                
        except Exception as e:
            print(f"获取统计信息失败: {e}")
    
    def print_welcome(self):
        """打印欢迎信息"""
        print("\n" + "=" * 60)
        print("🔍 LifeTrace 交互式图像相似度搜索")
        print("=" * 60)
        print("功能说明:")
        print("• 输入任意文本，搜索相似的图像")
        print("• 支持中英文查询")
        print("• 基于CLIP多模态模型的语义搜索")
        print("\n可用命令:")
        print("• help/h/?     - 显示帮助信息")
        print("• stats/status - 显示系统统计")
        print("• quit/exit/q  - 退出程序")
        print("=" * 60)
    
    def print_help(self):
        """打印帮助信息"""
        print("\n📖 帮助信息")
        print("-" * 30)
        print("查询示例:")
        print("• 电脑")
        print("• 网页浏览器")
        print("• 代码编辑器")
        print("• 文档")
        print("• 聊天软件")
        print("\n相似度等级:")
        print("• 🟢 高 (≥0.7)   - 非常相关")
        print("• 🟡 中 (≥0.5)   - 比较相关")
        print("• 🟠 低 (≥0.3)   - 有些相关")
        print("• 🔴 很低 (<0.3) - 相关性较低")
        print("\n提示:")
        print("• 使用具体的描述词获得更好的结果")
        print("• 可以描述图像内容、应用程序或功能")
        print("• 支持中英文混合查询")


def main():
    """主函数"""
    # 配置日志（减少输出）
    logging.basicConfig(
        level=logging.WARNING,
        format='%(levelname)s: %(message)s'
    )
    
    try:
        app = InteractiveImageSimilarity()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()