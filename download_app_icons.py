#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
下载常用应用图标
从免费图标库下载应用图标到assets/icons/apps目录
"""

import os
import requests
from pathlib import Path
import time

# 图标保存目录
ICON_DIR = Path("assets/icons/apps")
ICON_DIR.mkdir(parents=True, exist_ok=True)

# 应用图标URL映射（使用免费的图标资源）
# 使用 icons8.com 的免费图标（100x100, png格式）
ICON_URLS = {
    # 浏览器
    "chrome.png": "https://img.icons8.com/color/100/chrome--v1.png",
    "edge.png": "https://img.icons8.com/color/100/ms-edge-new.png",
    "firefox.png": "https://img.icons8.com/color/100/firefox--v1.png",
    
    # 开发工具
    "vscode.png": "https://img.icons8.com/color/100/visual-studio-code-2019.png",
    "pycharm.png": "https://img.icons8.com/color/100/pycharm.png",
    "intellij.png": "https://img.icons8.com/color/100/intellij-idea.png",
    "webstorm.png": "https://img.icons8.com/color/100/webstorm.png",
    "github.png": "https://img.icons8.com/color/100/github--v1.png",
    
    # 通讯工具
    "wechat.png": "https://img.icons8.com/color/100/wechat--v1.png",
    "qq.png": "https://img.icons8.com/color/100/qq.png",
    "telegram.png": "https://img.icons8.com/color/100/telegram-app.png",
    "discord.png": "https://img.icons8.com/color/100/discord-logo.png",
    
    # Office套件
    "word.png": "https://img.icons8.com/color/100/ms-word.png",
    "excel.png": "https://img.icons8.com/color/100/ms-excel.png",
    "powerpoint.png": "https://img.icons8.com/color/100/ms-powerpoint.png",
    "wps.png": "https://img.icons8.com/color/100/documents.png",
    
    # 设计工具
    "photoshop.png": "https://img.icons8.com/color/100/adobe-photoshop--v1.png",
    "xmind.png": "https://img.icons8.com/color/100/mind-map.png",
    "snipaste.png": "https://img.icons8.com/color/100/screenshot.png",
    
    # 媒体工具
    "spotify.png": "https://img.icons8.com/color/100/spotify.png",
    "vlc.png": "https://img.icons8.com/color/100/vlc.png",
    
    # 系统工具
    "explorer.png": "https://img.icons8.com/color/100/folder-invoices.png",
    "notepad.png": "https://img.icons8.com/color/100/notepad.png",
    "calculator.png": "https://img.icons8.com/color/100/calculator--v1.png",
}

def download_icon(filename, url, max_retries=3):
    """
    下载单个图标
    
    Args:
        filename: 保存的文件名
        url: 图标URL
        max_retries: 最大重试次数
    """
    filepath = ICON_DIR / filename
    
    # 如果文件已存在且大小>0，跳过
    if filepath.exists() and filepath.stat().st_size > 0:
        print(f"[OK] {filename} 已存在，跳过")
        return True
    
    for attempt in range(max_retries):
        try:
            print(f"下载 {filename}... (尝试 {attempt + 1}/{max_retries})")
            
            # 设置请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"[OK] {filename} 下载成功 ({len(response.content)} bytes)")
            time.sleep(0.5)  # 避免请求过快
            return True
            
        except Exception as e:
            print(f"[FAIL] {filename} 下载失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                return False
    
    return False

def main():
    """主函数：下载所有图标"""
    print(f"图标保存目录: {ICON_DIR.absolute()}")
    print(f"准备下载 {len(ICON_URLS)} 个图标...\n")
    
    success_count = 0
    fail_count = 0
    
    for filename, url in ICON_URLS.items():
        if download_icon(filename, url):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n完成！成功: {success_count}, 失败: {fail_count}")
    
    # 列出已下载的图标
    print(f"\n已下载的图标文件:")
    for icon_file in sorted(ICON_DIR.glob("*.png")):
        size_kb = icon_file.stat().st_size / 1024
        print(f"  - {icon_file.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    main()

