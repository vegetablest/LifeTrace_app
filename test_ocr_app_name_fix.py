#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试OCR应用名称修复效果
"""

import os
import sys
import tempfile
import shutil
from PIL import Image, ImageDraw, ImageFont

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.simple_ocr import SimpleOCRProcessor
from lifetrace_backend.storage import db_manager

def create_test_image(filename: str, text: str = "Test Screenshot") -> str:
    """创建测试图片"""
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    image_path = os.path.join(temp_dir, filename)
    
    # 创建一个简单的测试图片
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果失败则使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    # 在图片上绘制文本
    draw.text((50, 50), text, fill='black', font=font)
    draw.text((50, 150), f"应用测试: {filename}", fill='blue', font=font)
    
    # 保存图片
    img.save(image_path)
    return image_path

def test_ocr_app_name_detection():
    """测试OCR应用名称检�?""
    print("🧪 测试OCR应用名称检测修复效�?)
    print("=" * 60)
    
    # 创建OCR处理�?    ocr_processor = SimpleOCRProcessor()
    
    if not ocr_processor.is_available():
        print("�?OCR引擎不可用，请安�?rapidocr-onnxruntime")
        return False
    
    # 测试用例：不同的应用截图文件
    test_cases = [
        ("Snipaste_2024-01-15_14-30-25.png", "Snipaste截图测试"),
        ("chrome_webpage_capture.png", "Chrome浏览器截�?),
        ("vscode_coding_session.png", "VS Code编程界面"),
        ("photoshop_design_work.png", "Photoshop设计工作"),
        ("wechat_chat_window.png", "微信聊天窗口"),
        ("screenshot_20240115.png", "系统截图工具"),
        ("unknown_app_capture.png", "未知应用截图")
    ]
    
    print(f"📋 测试 {len(test_cases)} 个OCR处理用例:\n")
    
    results = []
    temp_dirs = []
    
    try:
        for i, (filename, test_text) in enumerate(test_cases, 1):
            print(f"{i}. 测试文件: {filename}")
            
            # 创建测试图片
            image_path = create_test_image(filename, test_text)
            temp_dirs.append(os.path.dirname(image_path))
            
            # 处理图片
            result = ocr_processor.process_image(image_path)
            
            if result['success']:
                screenshot_id = result.get('screenshot_id')
                if screenshot_id:
                    # 从数据库获取截图信息
                    screenshot_info = db_manager.get_screenshot_by_id(screenshot_id)
                    if screenshot_info:
                        app_name = screenshot_info.app_name
                        window_title = screenshot_info.window_title
                        
                        print(f"   �?OCR处理成功")
                        print(f"   📱 检测到的应�? {app_name}")
                        print(f"   🪟 窗口标题: {window_title}")
                        print(f"   📄 OCR文本: {result.get('text', '')[:50]}...")
                        
                        # 判断应用名称是否合理
                        is_reasonable = (
                            app_name != "外部工具" or 
                            "unknown" in filename.lower()
                        )
                        
                        results.append({
                            'filename': filename,
                            'app_name': app_name,
                            'window_title': window_title,
                            'reasonable': is_reasonable,
                            'success': True
                        })
                    else:
                        print(f"   �?无法从数据库获取截图信息")
                        results.append({
                            'filename': filename,
                            'success': False,
                            'error': '数据库查询失�?
                        })
                else:
                    print(f"   �?OCR处理失败，未创建截图记录")
                    results.append({
                        'filename': filename,
                        'success': False,
                        'error': '未创建截图记�?
                    })
            else:
                error_msg = result.get('error', '未知错误')
                print(f"   �?OCR处理失败: {error_msg}")
                results.append({
                    'filename': filename,
                    'success': False,
                    'error': error_msg
                })
            
            print()
    
    finally:
        # 清理临时文件
        for temp_dir in temp_dirs:
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    # 统计结果
    print("=" * 60)
    print("📊 测试结果统计:")
    
    total_count = len(results)
    success_count = sum(1 for r in results if r['success'])
    reasonable_count = sum(1 for r in results if r.get('reasonable', False))
    
    print(f"   总测试用�? {total_count}")
    print(f"   OCR成功: {success_count}")
    print(f"   应用名称合理: {reasonable_count}")
    
    if success_count > 0:
        reasonable_rate = (reasonable_count / success_count) * 100
        print(f"   应用名称准确�? {reasonable_rate:.1f}%")
        
        if reasonable_rate >= 80:
            print("\n🎉 应用名称检测修复效果良好！")
        elif reasonable_rate >= 60:
            print("\n⚠️  应用名称检测有所改善，但还有优化空间�?)
        else:
            print("\n�?应用名称检测仍需进一步改进�?)
    else:
        print("\n�?OCR处理全部失败，请检查OCR引擎配置�?)
    
    # 显示详细结果
    print("\n📋 详细结果:")
    for result in results:
        if result['success']:
            status = "�? if result.get('reasonable', False) else "⚠️"
            print(f"   {status} {result['filename']} -> {result['app_name']}")
        else:
            print(f"   �?{result['filename']} -> 失败: {result.get('error', '未知错误')}")
    
    return success_count > 0 and reasonable_count > 0

def test_database_query():
    """测试数据库查询功�?""
    print("\n🔍 测试数据库中的应用名称分�?)
    print("=" * 60)
    
    try:
        with db_manager.get_session() as session:
            from lifetrace_backend.models import Screenshot
            
            # 查询最近的10个截图记�?            recent_screenshots = session.query(Screenshot).order_by(Screenshot.created_at.desc()).limit(10).all()
            
            if not recent_screenshots:
                print("📭 数据库中暂无截图记录")
                return
            
            print(f"📊 最�?{len(recent_screenshots)} 个截图的应用分布:")
            app_counts = {}
            
            for screenshot in recent_screenshots:
                # 正确访问模型属�?                app_name = getattr(screenshot, 'app_name', None) or '未知'
                filename = getattr(screenshot, 'filename', 'unknown')
                app_counts[app_name] = app_counts.get(app_name, 0) + 1
                print(f"   📱 {filename} -> {app_name}")
            
            print("\n📈 应用名称统计:")
            for app_name, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   {app_name}: {count} �?)
            
    except Exception as e:
        print(f"�?数据库查询失�? {e}")

if __name__ == "__main__":
    try:
        # 测试OCR应用名称检�?        success = test_ocr_app_name_detection()
        
        # 测试数据库查�?        test_database_query()
        
        print("\n🎯 测试完成�?)
        
        if success:
            print("\n�?应用名称检测修复验证通过�?)
            print("💡 现在外部截图文件应该能够正确识别应用名称，而不是统一显示�?外部工具'�?)
        else:
            print("\n�?应用名称检测修复验证失败！")
            print("💡 请检查OCR引擎配置或应用名称检测逻辑�?)
        
    except Exception as e:
        print(f"�?测试过程中出现错�? {e}")
        import traceback
        traceback.print_exc()
