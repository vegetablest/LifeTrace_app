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
├── core/
│   ├── lifetrace_processor.log  # OCR处理器日志 (1.1 KB)
│   └── lifetrace_recorder.log   # 录制器日志 (161.7 KB)
├── sync/
│   └── consistency_checker.log  # 一致性检查日志 (17.4 KB)
└── debug/
    └── (调试日志文件)
```

### 3. 已解决的问题

#### 3.1 重复日志配置
- **问题**: 多个模块有独立的日志配置
- **解决**: 统一使用 `logging_config.py` 中的 `LifeTraceLogger`
- **影响**: 避免日志配置冲突，统一日志格式和轮转策略

#### 3.2 日志文件重复和无用文件
- **问题**: 同一功能的日志可能写入多个文件，存在空文件和废弃文件
- **解决**: 
  - 明确每个模块的日志文件归属
  - 清理无用的日志文件（simple_ocr.log, test_module.log, 历史格式文件等）
  - 删除空的日志文件
- **当前有效文件**:
  - `lifetrace_processor.log`: OCR处理器专用 (1.1 KB)
  - `lifetrace_recorder.log`: 录制器专用 (161.7 KB) 
  - `consistency_checker.log`: 一致性检查专用 (17.4 KB)

#### 3.3 日志配置统一化
- **问题**: `simple_ocr.py` 和 `utils.py` 中存在独立的日志配置函数
- **解决**: 移除重复的 `setup_logging` 函数，统一使用 `logging_config.py`
- **影响**: 所有模块现在使用统一的日志配置和格式

### 4. 当前活跃日志文件

| 文件名 | 目录 | 大小 | 用途 |
|--------|------|------|------|
| lifetrace_processor.log | core | 1.1KB | OCR处理器日志 |
| lifetrace_recorder.log | core | 161.7KB | 录制器日志 |
| consistency_checker.log | sync | 17.4KB | 一致性检查日志 |

**已清理的文件**:
- `simple_ocr.log` (0B) - 已移至统一日志配置
- `test_module.log` (295B) - 测试文件，已删除
- `lifetrace_20250821.log` (3.9KB) - 旧格式，已删除
- `lifetrace_20250822.log` (0B) - 空文件，已删除
- `lifetrace_server.log` (0B) - 空文件，已删除
- `lifetrace_sync.log` (4.9KB) - 已删除
- `lifetrace_consistency.log` (484B) - 已删除

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