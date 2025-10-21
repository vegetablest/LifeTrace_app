# 事件AI摘要功能 - 快速开始

## 🎯 功能简介

为LifeTrace的每个事件自动生成智能摘要，包括：
- **简洁标题**（≤10字）：快速了解事件主题
- **详细摘要**（≤30字）：突出关键信息，重点标粗

## ✨ 特性

- ✅ **完全自动**：应用切换时自动生成，无需手动操作
- ✅ **异步处理**：后台生成，不影响截图录制性能
- ✅ **智能分析**：基于OCR文本内容的AI理解
- ✅ **优雅降级**：OCR不足时使用简单描述

## 🚀 立即使用

### 1. 正常使用（自动生成）

什么都不用做！当你：
1. 使用应用（如Chrome浏览网页）
2. 切换到另一个应用（如VS Code编写代码）
3. 系统自动为前一个事件生成摘要

**查看效果：**
- 打开LifeTrace
- 点击"忆往昔"图标
- 浏览事件列表，看到AI生成的标题和摘要

### 2. 处理历史数据

**查看统计：**
```bash
python -m lifetrace_backend.event_summary_commands stats
```

**批量生成摘要：**
```bash
# 为所有未生成摘要的事件生成
python -m lifetrace_backend.event_summary_commands generate-summaries

# 限制处理数量（如最近100个）
python -m lifetrace_backend.event_summary_commands generate-summaries --limit 100

# 强制重新生成所有摘要
python -m lifetrace_backend.event_summary_commands generate-summaries --force
```

### 3. 测试功能

```bash
# 运行测试脚本
python test_event_summary.py

# 仅查看统计
python test_event_summary.py --stats-only
```

## 📖 展示效果

**传统展示：**
```
标题：LifeTrace - Google Chrome
描述：应用: chrome.exe
     正在进行的活动记录和截图捕捉
```

**AI摘要展示：**
```
标题：浏览技术文档
描述：阅读**LifeTrace**的事件机制和API接口文档
```

## 🔧 技术实现

### 核心文件
- `lifetrace_backend/event_summary_service.py` - 摘要生成服务
- `lifetrace_backend/storage.py` - 集成点（事件关闭时触发）
- `lifetrace_backend/templates/chat.html` - 前端展示
- `lifetrace_backend/event_summary_commands.py` - 批量处理工具

### API端点
- `GET /api/events` - 事件列表（包含ai_title和ai_summary）
- `GET /api/events/{id}` - 事件详情（包含ai_title和ai_summary）
- `POST /api/events/{id}/generate-summary` - 手动触发生成

### 数据库变更
Event表新增字段：
- `ai_title` - AI生成的标题
- `ai_summary` - AI生成的摘要（支持markdown）

## 📚 详细文档

- **完整说明**：[doc/event_mechanism.md](doc/event_mechanism.md) - 查看"AI智能摘要功能"章节
- **使用指南**：[doc/event_ai_summary_usage.md](doc/event_ai_summary_usage.md)
- **实现总结**：[doc/event_ai_summary_implementation.md](doc/event_ai_summary_implementation.md)

## ❓ 常见问题

**Q: 为什么有些事件没有摘要？**
- 事件刚结束，正在后台生成（2-5秒）
- 历史事件需要手动批量生成
- OCR尚未处理完成

**Q: 如何判断是AI生成的？**
- AI生成的标题更简洁语义化（如"编写代码"）
- 摘要有粗体标记重点
- 后备方案通常是"应用名+使用"

**Q: 会影响性能吗？**
- 不会！异步后台处理
- CPU占用极低（网络IO为主）
- 内存占用可忽略（10-20MB临时）

## 🎉 开始使用

1. **首次使用**：运行统计查看需要处理的数量
   ```bash
   python -m lifetrace_backend.event_summary_commands stats
   ```

2. **批量生成**：为历史数据补充摘要
   ```bash
   python -m lifetrace_backend.event_summary_commands generate-summaries --limit 100
   ```

3. **日常使用**：正常使用LifeTrace，自动生成新事件摘要

4. **查看效果**：在"忆往昔"面板浏览智能摘要

---

**版本：** v1.1  
**日期：** 2025-10-11  
**状态：** ✅ 生产就绪

享受更智能的历史记录浏览体验！🚀
