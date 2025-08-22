# LifeTrace 日志系统状态报告

## 整理完成时间
2025-01-22

## 日志系统架构

### 1. 统一日志配置
- **主配置文件**: `lifetrace_backend/logging_config.py`
- **配置管理**: 通过 `config/default_config.yaml` 中的 `logging` 部分统一管理
- **日志目录**: `~/.lifetrace/logs` (用户主目录)

### 2. 日志目录结构
```
~/.lifetrace/logs/
├── core/                    # 核心服务日志
│   ├── lifetrace_processor.log
│   ├── lifetrace_recorder.log
│   ├── lifetrace_server.log
│   └── test_module.log
├── sync/                    # 同步服务日志
│   ├── consistency_checker.log
│   ├── lifetrace_consistency.log
│   └── lifetrace_sync.log
├── debug/                   # 调试日志目录
├── lifetrace_20250821.log   # 历史日志
├── lifetrace_20250822.log
└── simple_ocr.log
```

### 3. 已解决的问题

#### 3.1 重复日志配置
- ✅ 移除了各模块中的重复 `setup_logging` 调用
- ✅ 统一使用 `logging_config.py` 进行日志管理
- ✅ 修复了 server.py, processor.py, recorder.py 中的双重配置问题

#### 3.2 重复日志文件
- ✅ 删除了重复的日志文件:
  - `lifetrace.processor.log` (保留 `lifetrace_processor.log`)
  - `lifetrace.server.log` (保留 `lifetrace_server.log`)

#### 3.3 日志文件命名规范
- ✅ 统一使用下划线命名: `lifetrace_[module].log`
- ✅ 按模块类型分目录存储

### 4. 当前活跃日志文件

| 文件名 | 目录 | 大小 | 用途 |
|--------|------|------|------|
| lifetrace_processor.log | core | 1.1KB | OCR处理器日志 |
| lifetrace_recorder.log | core | 23.3KB | 截图录制器日志 |
| lifetrace_server.log | core | 0B | Web服务器日志 |
| consistency_checker.log | sync | 4.5KB | 一致性检查日志 |
| lifetrace_consistency.log | sync | 484B | 一致性服务日志 |
| lifetrace_sync.log | sync | 4.9KB | 同步服务日志 |

### 5. 日志配置特性

- **日志轮转**: 10MB 最大文件大小，保留5个备份
- **编码**: UTF-8
- **格式**: 详细格式包含时间、模块、级别、文件位置和消息
- **级别控制**: 通过配置文件可独立控制各模块日志级别
- **双输出**: 同时输出到文件和控制台

### 6. 配置文件位置

- **主配置**: `config/default_config.yaml` - logging 部分
- **日志管理器**: `lifetrace_backend/logging_config.py`
- **备用配置**: `useless/logging_config.py` (保留作为参考)

### 7. 使用方式

各模块通过以下方式获取日志器:
```python
from .logging_config import setup_logging

logger_manager = setup_logging(config)
logger = logger_manager.get_[module]_logger()
```

### 8. 维护建议

1. 定期清理超过30天的日志文件
2. 监控日志文件大小，避免磁盘空间不足
3. 根据需要调整各模块的日志级别
4. 保持日志配置的统一性，避免重复配置

---

**状态**: ✅ 日志系统已整理完成，运行正常
**最后更新**: 2025-01-22