![LifeTrace Logo](assets/rhn8yu8l.png)

![GitHub stars](https://img.shields.io/github/stars/tangyuanbo1/LifeTrace_app?style=social) ![GitHub forks](https://img.shields.io/github/forks/tangyuanbo1/LifeTrace_app?style=social) ![GitHub issues](https://img.shields.io/github/issues/tangyuanbo1/LifeTrace_app) ![GitHub license](https://img.shields.io/github/license/tangyuanbo1/LifeTrace_app) ![Python version](https://img.shields.io/badge/python-3.13+-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)

**语言**: [English](README.md) | [中文](README_CN.md)

[📖 文档](doc/README.md) • [🚀 快速开始](#部署与配置) • [💡 功能特性](#核心功能) • [🔧 开发指南](#开发指南) • [🤝 贡献指南](#贡献)

# LifeTrace - 智能生活记录系统

## 项目概述

LifeTrace 是一个基于 AI 的智能生活记录系统，通过自动截图捕获、OCR 文本识别和多模态搜索技术，帮助用户记录和检索日常活动。系统支持传统关键词搜索、语义搜索和多模态搜索，提供强大的生活轨迹追踪能力。

## 核心功能

- **自动截图记录**：定时自动屏幕捕获，记录用户活动
- **智能 OCR 识别**：使用 RapidOCR 从截图中提取文本内容
- **多模态搜索**：支持文本、图像和语义搜索
- **向量数据库**：基于 ChromaDB 的高效向量存储和检索
- **Web API 服务**：提供完整的 RESTful API 接口
- **前端集成**：支持与各种前端框架集成

## 📋 待办事项与路线图

### 🚀 高优先级


- ☐ **用户体验改进**
  - ☐ 为高级用户实现键盘快捷键
  - ☐ 创建交互式入门教程




### 💡 未来计划


- ☐ **移动端与跨平台**
  - ☐ 开发移动配套应用
  - ☐ 添加平板优化界面
  - ☐ 创建 Web 版本


### ✅ 最近完成
- ☑ **核心基础设施** - 基础截图记录和 OCR 功能


---

> 💡 **想要贡献？** 查看我们的[贡献指南](#贡献)并选择任何你感兴趣的待办事项！

## 部署与配置

### 环境要求
- Python 3.13+
- 支持的操作系统：Windows、macOS
- 可选：CUDA 支持（用于 GPU 加速）

### 安装依赖

所有依赖文件位于 `requirements/` 目录下：

**For Windows:**
```bash
pip install -r requirements/requirements_windows.txt
```

**For macOS:**
```bash
pip install -r requirements/requirements_macos.txt
```

### 初始化数据库
```bash
python init_database.py
```

### 启动服务

#### 启动所有服务
```bash
python start_all_services.py
```

#### 仅启动 Web 服务
```bash
python -m lifetrace_backend.server --port 8840
```

#### 启动单个服务
```bash
# 启动录制器
python -m lifetrace_backend.recorder

# 启动处理器
python -m lifetrace_backend.processor

# 启动 OCR 服务
python -m lifetrace_backend.simple_ocr
```

## 开发指南

### 项目结构
```
LifeTrace_app/
├── lifetrace_backend/          # 核心后端模块
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py               # Web API 服务
│   ├── models.py               # 数据模型
│   ├── config.py               # 配置管理
│   ├── storage.py              # 存储管理
│   ├── simple_ocr.py           # OCR 处理
│   ├── vector_service.py       # 向量服务
│   ├── multimodal_*.py         # 多模态服务
│   ├── processor.py            # 文件处理
│   ├── recorder.py             # 屏幕录制
│   ├── heartbeat.py            # 服务心跳
│   ├── rag_service.py          # RAG 服务
│   ├── retrieval_service.py    # 检索服务
│   ├── sync_service.py         # 同步服务
│   ├── utils.py                # 工具函数
│   └── templates/              # HTML 模板
├── config/                     # 配置文件
│   ├── config.yaml
│   └── default_config.yaml
├── doc/                        # 文档
├── front/                      # 前端应用
│   ├── components/             # React 组件
│   ├── services/               # API 服务
│   ├── public/                 # 静态资源
│   └── package.json            # 前端依赖
├── debug/                      # 调试和诊断工具
│   ├── test_*.py               # 测试文件
│   ├── check_*.py              # 状态检查工具
│   ├── diagnostic_tool.py      # 系统诊断
│   ├── memory_analyzer.py      # 内存分析
│   └── *.py                    # 其他调试工具
├── requirements/               # 依赖文件
│   ├── requirements.txt        # 主要依赖
│   ├── requirements_multimodal.txt
│   ├── requirements_rapidocr.txt
│   └── requirements_vector.txt
├── assets/                     # 静态资源
├── start_all_services.py       # 主服务启动器
├── init_database.py            # 数据库初始化
├── init_config.py              # 配置初始化
└── setup.py                    # 项目设置
```



## 贡献

LifeTrace 社区的存在离不开像您这样的众多友善志愿者。我们欢迎所有对社区的贡献，并很高兴欢迎您的加入。

> 请按照以下步骤进行贡献。

**最近的贡献：**

![GitHub contributors](https://img.shields.io/github/contributors/tangyuanbo1/LifeTrace_app) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/tangyuanbo1/LifeTrace_app) ![GitHub last commit](https://img.shields.io/github/last-commit/tangyuanbo1/LifeTrace_app)

**如何贡献：**

1. **🍴 Fork 项目** - 创建您自己的仓库副本
2. **🌿 创建功能分支** - `git checkout -b feature/amazing-feature`
3. **💾 提交您的更改** - `git commit -m 'Add some amazing feature'`
4. **📤 推送到分支** - `git push origin feature/amazing-feature`
5. **🔄 创建 Pull Request** - 提交您的更改以供审核

**代码风格与质量要求：**

为确保项目代码风格统一，请在开发前进行以下准备：

1. **安装代码检查与格式化依赖**

   ```bash
   pip install -r ../requirements/requirements_lint.txt
   ```

2. **安装 pre-commit 钩子**

   ```bash
   pre-commit install
   ```

   这样每次提交代码前都会自动进行格式化与检查。

3. **（可选）手动执行格式化与检查**

   ```bash
   make format
   make lint
   ```

**您可以贡献的领域：**

- 🐛 **错误报告** - 帮助我们识别和修复问题
- 💡 **功能请求** - 建议新功能
- 📝 **文档** - 改进指南和教程
- 🧪 **测试** - 编写测试并提高覆盖率
- 🎨 **UI/UX** - 增强用户界面
- 🔧 **代码** - 实现新功能和改进

**开始贡献：**

- 查看我们的[贡献指南](CONTRIBUTING.md)
- 寻找标记为 `good first issue` 或 `help wanted` 的问题
- 在 Issues 和 Pull Requests 中加入我们的社区讨论

我们感谢所有贡献，无论大小！🙏



## 文档
我们使用 deepwiki 管理文档，请参考此[**网站**](https://deepwiki.com/tangyuanbo1/LifeTrace_app/6.2-deployment-and-setup)。

## Star 历史

[![Star History Chart](https://api.star-history.com/svg?repos=tangyuanbo1/LifeTrace_app&type=Timeline)](https://www.star-history.com/#tangyuanbo1/LifeTrace_app&Timeline)


## 许可证

版权所有 © 2024 LifeTrace.org

本仓库的内容受以下许可证约束：

• 计算机软件根据 [Apache License 2.0](LICENSE) 许可。
• `/doc` 目录及其子目录中的学习资源版权所有 © 2024 LifeTrace.org

### Apache License 2.0

根据 Apache License 2.0 版（"许可证"）授权；
除非遵守许可证，否则您不得使用此文件。
您可以在以下位置获取许可证副本：

    http://www.apache.org/licenses/LICENSE-2.0

除非适用法律要求或书面同意，否则根据许可证分发的软件是基于
"按原样"分发的，不附带任何明示或暗示的保证或条件。
有关许可证下的特定语言管理权限和限制，请参阅许可证。
