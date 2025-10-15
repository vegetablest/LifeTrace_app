#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试应用名称检测功�?"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.simple_ocr import SimpleOCRProcessor

def test_app_name_detection():
    """测试应用名称检测功�?""
    print("🧪 测试应用名称检测功�?)
    print("=" * 50)

    # 创建OCR处理器实�?    ocr_processor = SimpleOCRProcessor()

    # 测试用例：不同的文件路径和文件名
    test_cases = [
        # 截图工具
        ("C:\\Users\\User\\Desktop\\Snipaste_2024-01-15_10-30-45.png", "Snipaste_2024-01-15_10-30-45.png"),
        ("D:\\Screenshots\\ShareX_screenshot_001.png", "ShareX_screenshot_001.png"),
        ("E:\\Images\\lightshot_capture.png", "lightshot_capture.png"),

        # 浏览�?        ("C:\\Users\\User\\Downloads\\chrome_page_screenshot.png", "chrome_page_screenshot.png"),
        ("D:\\Temp\\firefox_capture.png", "firefox_capture.png"),
        ("E:\\Browser\\edge_screenshot.png", "edge_screenshot.png"),

        # 开发工�?        ("C:\\Projects\\vscode_debug_screenshot.png", "vscode_debug_screenshot.png"),
        ("D:\\Code\\pycharm_interface.png", "pycharm_interface.png"),
        ("E:\\Dev\\sublime_text_capture.png", "sublime_text_capture.png"),

        # 办公软件
        ("C:\\Documents\\word_document_screenshot.png", "word_document_screenshot.png"),
        ("D:\\Office\\excel_spreadsheet.png", "excel_spreadsheet.png"),
        ("E:\\Work\\notion_page_capture.png", "notion_page_capture.png"),

        # 设计软件
        ("C:\\Design\\photoshop_workspace.png", "photoshop_workspace.png"),
        ("D:\\Graphics\\figma_design.png", "figma_design.png"),
        ("E:\\Art\\illustrator_project.png", "illustrator_project.png"),

        # 通讯软件
        ("C:\\Chat\\wechat_conversation.png", "wechat_conversation.png"),
        ("D:\\Messages\\discord_channel.png", "discord_channel.png"),
        ("E:\\Communication\\teams_meeting.png", "teams_meeting.png"),

        # 系统工具
        ("C:\\Windows\\explorer_window.png", "explorer_window.png"),
        ("D:\\System\\notepad_file.png", "notepad_file.png"),
        ("E:\\Tools\\calculator_app.png", "calculator_app.png"),

        # 特殊模式
        ("C:\\Screenshots\\screenshot_2024_01_15.png", "screenshot_2024_01_15.png"),
        ("D:\\Captures\\capture_main_window.png", "capture_main_window.png"),
        ("E:\\Images\\screen_shot_001.png", "screen_shot_001.png"),

        # 路径中包含应用名�?        ("C:\\Program Files\\Google\\Chrome\\screenshot.png", "screenshot.png"),
        ("D:\\Applications\\Visual Studio Code\\debug_capture.png", "debug_capture.png"),
        ("E:\\Software\\Adobe\\Photoshop\\workspace.png", "workspace.png"),

        # 未知应用
        ("C:\\Unknown\\random_file.png", "random_file.png"),
        ("D:\\Temp\\unknown_screenshot.png", "unknown_screenshot.png"),
    ]

    print(f"📋 测试 {len(test_cases)} 个用�?\n")

    success_count = 0
    total_count = len(test_cases)

    for i, (file_path, filename) in enumerate(test_cases, 1):
        detected_app = ocr_processor._detect_app_name_from_path(file_path, filename)

        # 判断检测是否合�?        is_reasonable = detected_app != "外部工具" or "unknown" in filename.lower() or "random" in filename.lower()

        status = "�? if is_reasonable else "�?
        if is_reasonable:
            success_count += 1

        print(f"{i:2d}. {status} 文件: {filename}")
        print(f"    路径: {file_path}")
        print(f"    检测结�? {detected_app}")
        print()

    # 统计结果
    success_rate = (success_count / total_count) * 100
    print("=" * 50)
    print(f"📊 测试结果统计:")
    print(f"   总测试用�? {total_count}")
    print(f"   成功检�? {success_count}")
    print(f"   成功�? {success_rate:.1f}%")

    if success_rate >= 80:
        print("🎉 应用名称检测功能工作良好！")
    elif success_rate >= 60:
        print("⚠️  应用名称检测功能基本可用，但还有改进空间�?)
    else:
        print("�?应用名称检测功能需要进一步优化�?)

def test_specific_patterns():
    """测试特定的应用名称模�?""
    print("\n🔍 测试特定应用名称模式")
    print("=" * 50)

    ocr_processor = SimpleOCRProcessor()

    # 测试常见的截图工具模�?    patterns = {
        "Snipaste_2024-01-15_14-30-25.png": "Snipaste",
        "Screenshot_20240115_143025.png": "系统截图工具",
        "screen_shot_001.png": "截图工具",
        "capture_window.png": "屏幕捕获工具",
        "chrome_tab_screenshot.png": "Google Chrome",
        "vscode_editor.png": "Visual Studio Code",
        "random_image.png": "外部工具"
    }

    print("📋 特定模式测试:\n")

    for filename, expected in patterns.items():
        detected = ocr_processor._detect_app_name_from_path(f"C:\\Test\\{filename}", filename)
        status = "�? if detected == expected else "�?

        print(f"{status} {filename}")
        print(f"    期望: {expected}")
        print(f"    检�? {detected}")
        print()

if __name__ == "__main__":
    try:
        test_app_name_detection()
        test_specific_patterns()

        print("\n🎯 测试完成�?)
        print("\n💡 提示: 如果检测效果不理想，可以在 _detect_app_name_from_path 方法�?)
        print("   添加更多的应用名称模式或调整检测逻辑�?)

    except Exception as e:
        print(f"�?测试过程中出现错�? {e}")
        import traceback
        traceback.print_exc()
