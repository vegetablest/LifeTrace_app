#!/usr/bin/env python3
"""
LifeTrace 前后端集成演示启动脚本
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path

def check_backend_health():
    """检查后端服务是否正常运行"""
    try:
        import requests
        response = requests.get('http://127.0.0.1:8840/health', timeout=5)
        return response.status_code == 200
    except:
        return False

def start_backend():
    """启动后端服务"""
    print("启动 LifeTrace 后端服务...")

    # 检查虚拟环境
    venv_python = Path("venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ 找不到虚拟环境，请先运行: python -m venv venv")
        return None

    # 启动后端服务
    try:
        process = subprocess.Popen([
            str(venv_python),
            "-m", "lifetrace_backend.server",
            "--port", "8840"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )

        print("⏳ 等待后端服务启动...")

        # 等待服务启动
        for i in range(30):  # 最多等待30秒
            if check_backend_health():
                print("✅ 后端服务启动成功!")
                return process
            time.sleep(1)
            print(f"   等待中... ({i+1}/30)")

        print("❌ 后端服务启动超时")
        process.terminate()
        return None

    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return None

def create_frontend_html():
    """创建一个简单的前端演示页面"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LifeTrace 前后端集成演示</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .search-box {
            margin-bottom: 30px;
        }
        .search-input {
            width: 100%;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #333;
            background: #2a2a2a;
            color: white;
            border-radius: 8px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #333;
            border: none;
            color: white;
            cursor: pointer;
            border-radius: 5px;
        }
        .tab.active {
            background: #0066cc;
        }
        .results {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        .results-panel {
            background: #2a2a2a;
            border-radius: 8px;
            padding: 20px;
            height: 500px;
            overflow-y: auto;
        }
        .result-item {
            padding: 10px;
            margin-bottom: 10px;
            background: #333;
            border-radius: 5px;
            cursor: pointer;
        }
        .result-item:hover {
            background: #404040;
        }
        .result-title {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .result-subtitle {
            font-size: 14px;
            color: #ccc;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .error {
            text-align: center;
            padding: 40px;
            color: #ff6b6b;
        }
        .status {
            margin-bottom: 20px;
            padding: 10px;
            background: #2a2a2a;
            border-radius: 5px;
        }
        .status.online {
            border-left: 4px solid #4caf50;
        }
        .status.offline {
            border-left: 4px solid #f44336;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 LifeTrace 前后端集成演示</h1>
            <div id="status" class="status">
                <span id="status-text">检查服务状态...</span>
            </div>
        </div>

        <div class="search-box">
            <input type="text" id="searchInput" class="search-input" placeholder="输入搜索关键词..." />
        </div>

        <div class="tabs">
            <button class="tab active" data-type="all">全部搜索</button>
            <button class="tab" data-type="traditional">传统搜索</button>
            <button class="tab" data-type="semantic">语义搜索</button>
            <button class="tab" data-type="multimodal">多模态搜索</button>
        </div>

        <div class="results">
            <div class="results-panel">
                <h3>搜索结果</h3>
                <div id="results"></div>
            </div>
            <div class="results-panel">
                <h3>详细信息</h3>
                <div id="details">
                    <p>选择一个搜索结果查看详细信息</p>
                </div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://127.0.0.1:8840/api';
        let currentSearchType = 'all';
        let searchTimeout = null;

        // 检查后端状态
        async function checkStatus() {
            try {
                const response = await fetch(`${API_BASE}/health`);
                const data = await response.json();
                document.getElementById('status').className = 'status online';
                document.getElementById('status-text').textContent = `✅ 后端服务正常 (数据库: ${data.database}, OCR: ${data.ocr})`;
                return true;
            } catch (error) {
                document.getElementById('status').className = 'status offline';
                document.getElementById('status-text').textContent = '❌ 后端服务连接失败';
                return false;
            }
        }

        // 执行搜索
        async function performSearch(query, searchType = 'all') {
            if (!query.trim()) {
                document.getElementById('results').innerHTML = '<p>请输入搜索关键词</p>';
                return;
            }

            document.getElementById('results').innerHTML = '<div class="loading">搜索中...</div>';

            try {
                let url, body;

                if (searchType === 'traditional' || searchType === 'all') {
                    // 传统搜索
                    const params = new URLSearchParams({ query, limit: '20' });
                    const response = await fetch(`${API_BASE}/search?${params}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, limit: 20 })
                    });
                    const results = await response.json();
                    displayResults(results.map(r => ({
                        id: r.id,
                        title: r.window_title || r.app_name || `截图 ${r.id}`,
                        subtitle: `${r.app_name || '未知应用'} - ${new Date(r.created_at).toLocaleString()}`,
                        type: 'traditional',
                        data: r
                    })));
                } else if (searchType === 'semantic') {
                    // 语义搜索
                    const response = await fetch(`${API_BASE}/semantic-search`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, top_k: 20 })
                    });
                    const results = await response.json();
                    displayResults(results.map(r => ({
                        id: r.metadata.screenshot_id || Math.random(),
                        title: r.text.substring(0, 50) + (r.text.length > 50 ? '...' : ''),
                        subtitle: `语义相似度: ${(r.score * 100).toFixed(1)}%`,
                        type: 'semantic',
                        data: r
                    })));
                } else if (searchType === 'multimodal') {
                    // 多模态搜索
                    const response = await fetch(`${API_BASE}/multimodal-search`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ query, top_k: 20 })
                    });
                    const results = await response.json();
                    displayResults(results.map(r => ({
                        id: r.metadata.screenshot_id || Math.random(),
                        title: r.text.substring(0, 50) + (r.text.length > 50 ? '...' : ''),
                        subtitle: `综合分数: ${(r.combined_score * 100).toFixed(1)}% (文本:${(r.text_score * 100).toFixed(1)}%, 图像:${(r.image_score * 100).toFixed(1)}%)`,
                        type: 'multimodal',
                        data: r
                    })));
                }
            } catch (error) {
                document.getElementById('results').innerHTML = `<div class="error">搜索失败: ${error.message}</div>`;
            }
        }

        // 显示搜索结果
        function displayResults(results) {
            const resultsDiv = document.getElementById('results');

            if (results.length === 0) {
                resultsDiv.innerHTML = '<p>暂无搜索结果</p>';
                return;
            }

            resultsDiv.innerHTML = results.map(result => `
                <div class="result-item" onclick="showDetails(${JSON.stringify(result).replace(/"/g, '&quot;')})">
                    <div class="result-title">${result.title}</div>
                    <div class="result-subtitle">${result.subtitle}</div>
                </div>
            `).join('');
        }

        // 显示详细信息
        function showDetails(result) {
            const detailsDiv = document.getElementById('details');
            detailsDiv.innerHTML = `
                <h4>${result.title}</h4>
                <p><strong>类型:</strong> ${result.type}</p>
                <p><strong>详情:</strong> ${result.subtitle}</p>
                <pre style="background: #1a1a1a; padding: 10px; border-radius: 5px; white-space: pre-wrap; font-size: 12px;">${JSON.stringify(result.data, null, 2)}</pre>
            `;
        }

        // 初始化
        document.addEventListener('DOMContentLoaded', function() {
            checkStatus();

            // 搜索输入框
            const searchInput = document.getElementById('searchInput');
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    performSearch(this.value, currentSearchType);
                }, 500);
            });

            // 标签切换
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    currentSearchType = this.dataset.type;

                    const query = searchInput.value;
                    if (query.trim()) {
                        performSearch(query, currentSearchType);
                    }
                });
            });

            // 定期检查状态
            setInterval(checkStatus, 10000);
        });
    </script>
</body>
</html>"""

    demo_path = Path("frontend_demo.html")
    with open(demo_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return demo_path

def main():
    """主函数"""
    print("LifeTrace 前后端集成演示")
    print("=" * 50)

    # 启动后端服务
    backend_process = start_backend()
    if not backend_process:
        print("❌ 无法启动后端服务，演示终止")
        return

    try:
        # 创建前端演示页面
        print("📄 创建前端演示页面...")
        demo_path = create_frontend_html()
        print(f"✅ 演示页面创建成功: {demo_path}")

        # 打开浏览器
        print("🌐 打开浏览器演示页面...")
        webbrowser.open(f"file://{demo_path.absolute()}")

        print("\n" + "=" * 50)
        print("🎉 演示启动完成!")
        print(f"📍 后端API地址: http://127.0.0.1:8840")
        print(f"📍 前端演示页面: file://{demo_path.absolute()}")
        print("\n功能说明:")
        print("  • 传统搜索: 基于关键词匹配OCR文本内容")
        print("  • 语义搜索: 基于文本语义相似度")
        print("  • 多模态搜索: 综合文本和图像相似度")
        print("\n按 Ctrl+C 停止服务...")

        # 保持运行
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n🛑 正在停止服务...")
        backend_process.terminate()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
