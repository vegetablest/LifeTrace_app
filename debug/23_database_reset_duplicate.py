#!/usr/bin/env python3
"""
重置LifeTrace数据库工具
同时重置SQLite和向量数据库
"""

import os
import sys
import shutil
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from lifetrace.config import config
from lifetrace.storage import db_manager
from lifetrace.vector_service import create_vector_service


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def reset_sqlite_database():
    """重置SQLite数据库"""
    print("🗄️ 重置SQLite数据库...")
    
    try:
        # 获取数据库路径
        db_path = config.database_path
        print(f"数据库路径: {db_path}")
        
        # 删除数据库文件
        if os.path.exists(db_path):
            os.remove(db_path)
            print("✅ SQLite数据库文件已删除")
        else:
            print("ℹ️  SQLite数据库文件不存在")
        
        # 重新初始化数据库
        db_manager._init_database()
        print("✅ SQLite数据库已重新初始化")
        
        return True
        
    except Exception as e:
        print(f"❌ 重置SQLite数据库失败: {e}")
        return False


def reset_vector_database():
    """重置向量数据库"""
    print("\n🧠 重置向量数据库...")
    
    try:
        # 创建向量服务
        vector_service = create_vector_service(config, db_manager)
        
        if not vector_service.is_enabled():
            print("ℹ️  向量数据库未启用，跳过重置")
            return True
        
        # 重置向量数据库
        success = vector_service.reset()
        
        if success:
            print("✅ 向量数据库已重置")
        else:
            print("❌ 向量数据库重置失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 重置向量数据库失败: {e}")
        return False


def clean_vector_files():
    """清理向量数据库文件"""
    print("\n🧹 清理向量数据库文件...")
    
    try:
        vector_db_path = Path(config.vector_db_persist_directory)
        
        if vector_db_path.exists():
            shutil.rmtree(vector_db_path)
            print(f"✅ 向量数据库目录已删除: {vector_db_path}")
        else:
            print("ℹ️  向量数据库目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理向量数据库文件失败: {e}")
        return False


def clean_screenshot_files():
    """清理截图目录"""
    print("\n📸 清理截图目录...")
    
    try:
        screenshots_dir = Path(config.screenshots_dir)
        
        if screenshots_dir.exists():
            # 计算文件数量
            files = list(screenshots_dir.glob("*"))
            file_count = len(files)
            
            if file_count > 0:
                for file_path in files:
                    if file_path.is_file():
                        file_path.unlink()
                
                print(f"✅ 已删除 {file_count} 个文件")
            else:
                print("ℹ️  截图目录为空")
        else:
            print("ℹ️  截图目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理截图目录失败: {e}")
        return False


def clean_logs():
    """清理日志文件"""
    print("\n📝 清理日志文件...")
    
    try:
        logs_dir = Path(config.base_dir) / 'logs'
        
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log"))
            
            if log_files:
                for log_file in log_files:
                    log_file.unlink()
                print(f"✅ 已删除 {len(log_files)} 个日志文件")
            else:
                print("ℹ️  没有日志文件需要清理")
        else:
            print("ℹ️  日志目录不存在")
        
        return True
        
    except Exception as e:
        print(f"❌ 清理日志文件失败: {e}")
        return False


def show_status():
    """显示当前状态"""
    print("\n📊 当前状态:")
    
    # SQLite数据库
    db_path = config.database_path
    db_exists = os.path.exists(db_path)
    print(f"  SQLite数据库: {'存在' if db_exists else '不存在'} ({db_path})")
    
    # 向量数据库
    vector_db_path = Path(config.vector_db_persist_directory)
    vector_exists = vector_db_path.exists()
    print(f"  向量数据库: {'存在' if vector_exists else '不存在'} ({vector_db_path})")
    
    # 截图目录
    screenshots_dir = Path(config.screenshots_dir)
    if screenshots_dir.exists():
        file_count = len(list(screenshots_dir.glob("*")))
        print(f"  截图文件: {file_count} 个")
    else:
        print(f"  截图目录: 不存在")


def main():
    """主函数"""
    print("🔄 LifeTrace 数据库重置工具")
    print("=" * 50)
    
    setup_logging()
    
    # 显示当前状态
    show_status()
    
    # 确认操作
    print(f"\n⚠️  警告: 此操作将删除所有数据，包括:")
    print("  - SQLite数据库中的所有截图和OCR记录")
    print("  - 向量数据库中的所有语义搜索数据")
    print("  - 截图目录中的所有文件")
    print("  - 日志文件")
    
    confirm = input("\n确定要继续吗? (输入 'yes' 确认): ").strip().lower()
    
    if confirm != 'yes':
        print("❌ 操作已取消")
        return
    
    print(f"\n🚀 开始重置...")
    
    # 执行重置操作
    operations = [
        ("清理截图文件", clean_screenshot_files),
        ("重置SQLite数据库", reset_sqlite_database),
        ("清理向量数据库文件", clean_vector_files),
        ("重置向量数据库", reset_vector_database),
        ("清理日志文件", clean_logs),
    ]
    
    results = []
    
    for op_name, op_func in operations:
        try:
            result = op_func()
            results.append((op_name, result))
        except Exception as e:
            print(f"❌ {op_name} 执行异常: {e}")
            results.append((op_name, False))
    
    # 显示结果
    print(f"\n{'='*50}")
    print("📋 重置结果:")
    
    success_count = 0
    for op_name, success in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"  {op_name}: {status}")
        if success:
            success_count += 1
    
    print(f"\n总计: {success_count}/{len(results)} 个操作成功")
    
    if success_count == len(results):
        print(f"\n🎉 数据库重置完成！")
        print(f"\n接下来可以:")
        print(f"  1. 重新初始化: lifetrace init")
        print(f"  2. 启动服务: lifetrace start")
        print(f"  3. 开始截图和OCR处理")
    else:
        print(f"\n⚠️  部分操作失败，请检查错误信息")
    
    # 显示重置后状态
    print(f"\n重置后状态:")
    show_status()


if __name__ == '__main__':
    main()