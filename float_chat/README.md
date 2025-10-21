# LifeTrace Float Chat

一个基于 Electron 的桌面聊天应用，为 LifeTrace 项目提供独立的聊天界面。

## 功能特性

- 🎨 **现代化 UI**: 支持深色/浅色主题切换
- 💬 **智能对话**: 与 LifeTrace 后端 API 完整集成
- 📝 **Markdown 支持**: 富文本消息渲染
- 💾 **本地存储**: 聊天历史和设置持久化
- ⚙️ **可配置**: 支持自定义 API 地址、温度等参数
- 🖥️ **桌面集成**: 原生菜单、快捷键、窗口状态保存
- 🔄 **流式响应**: 实时显示 AI 回复

## 安装要求

- Node.js 16.0 或更高版本
- npm 或 yarn

## 开发环境设置

1. 安装依赖：
```bash
npm install
```

2. 启动开发模式：
```bash
npm run dev
```

3. 构建应用：
```bash
# Windows
npm run build-win

# macOS
npm run build-mac

# Linux
npm run build-linux

# 所有平台
npm run build
```

## 项目结构

```
float_chat/
├── assets/           # 应用图标和资源
├── lib/             # 外部 JavaScript 库
├── main.js          # Electron 主进程
├── preload.js       # 安全桥接脚本
├── index.html       # 聊天界面
├── styles.css       # 样式文件
├── script.js        # 聊天逻辑
└── package.json     # 项目配置
```

## 配置说明

应用支持以下配置项：

- **API 地址**: 后端服务器地址
- **温度**: AI 回复的创造性程度 (0.0-2.0)
- **最大 Token**: 单次对话的最大 token 数
- **主题**: 深色/浅色模式

## 快捷键

- `Ctrl+N` / `Cmd+N`: 新建聊天
- `Ctrl+,` / `Cmd+,`: 打开设置
- `Ctrl+Shift+D` / `Cmd+Shift+D`: 切换主题
- `Enter`: 发送消息
- `Shift+Enter`: 换行

## 技术栈

- **Electron**: 跨平台桌面应用框架
- **Marked.js**: Markdown 解析和渲染
- **Lucide**: 现代图标库
- **Electron Store**: 本地数据存储

## 许可证

MIT License
