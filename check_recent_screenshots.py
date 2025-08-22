#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查最近的截图活动
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lifetrace_backend.storage import db_manager
from lifetrace_backend.models import Screenshot
from datetime import datetime, timedelta

def check_recent_screenshots():
    """检查最近的截图活动"""
    try:
        with db_manager.get_session() as session:
            # 检查最近10分钟的截图
            recent_10min = session.query(Screenshot).filter(
                Screenshot.created_at > datetime.now() - timedelta(minutes=10)
            ).order_by(Screenshot.created_at.desc()).limit(10).all()
            
            # 检查最近1小时的截图
            recent_1hour = session.query(Screenshot).filter(
                Screenshot.created_at > datetime.now() - timedelta(hours=1)
            ).count()
            
            # 检查最新的5张截图
            latest_screenshots = session.query(Screenshot).order_by(
                Screenshot.created_at.desc()
            ).limit(5).all()
            
            print("=== 截图活动检查 ===")
            print(f"最近10分钟内的截图数量: {len(recent_10min)}")
            print(f"最近1小时内的截图数量: {recent_1hour}")
            
            if recent_10min:
                print("\n=== 最近10分钟的截图 ===")
                for screenshot in recent_10min:
                    print(f"时间: {screenshot.created_at}, 文件: {os.path.basename(screenshot.file_path)}")
            else:
                print("\n❌ 最近10分钟内没有新截图")
            
            print("\n=== 最新的5张截图 ===")
            for screenshot in latest_screenshots:
                print(f"时间: {screenshot.created_at}, 文件: {os.path.basename(screenshot.file_path)}")
            
            # 检查截图目录
            screenshot_dir = os.path.expanduser("~/.lifetrace/screenshots")
            if os.path.exists(screenshot_dir):
                files = os.listdir(screenshot_dir)
                png_files = [f for f in files if f.endswith('.png')]
                print(f"\n=== 截图目录状态 ===")
                print(f"截图目录: {screenshot_dir}")
                print(f"目录中的PNG文件数量: {len(png_files)}")
                
                # 检查最新的文件
                if png_files:
                    file_times = []
                    for f in png_files[:5]:  # 只检查前5个文件
                        file_path = os.path.join(screenshot_dir, f)
                        mtime = os.path.getmtime(file_path)
                        file_times.append((f, datetime.fromtimestamp(mtime)))
                    
                    file_times.sort(key=lambda x: x[1], reverse=True)
                    print("\n最新的文件:")
                    for filename, mtime in file_times[:3]:
                        print(f"  {filename} - {mtime}")
            else:
                print(f"\n❌ 截图目录不存在: {screenshot_dir}")
                
    except Exception as e:
        print(f"检查截图活动时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_recent_screenshots()