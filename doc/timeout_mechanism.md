# 超时机制说明

## 概述

为了防止 LifeTrace 录制器在文件 I/O 和数据库操作时发生卡死，我们为 `recorder.py` 添加了完善的超时机制。当操作超过预设时间时，系统会记录警告日志并继续执行。

## 实现原理

### 超时装饰器

使用 `@with_timeout` 装饰器为关键操作添加超时控制：

```python
@with_timeout(timeout_seconds=15, operation_name="文件保存")
def _save_screenshot(self, screenshot, file_path: str) -> bool:
    # 文件保存逻辑
```

### 超时实现机制

- 使用 `threading.Thread` 在单独线程中执行操作
- 通过 `thread.join(timeout)` 设置超时时间
- 兼容 Windows 系统（不依赖 Unix 信号机制）
- 超时时记录警告日志，不中断主程序流程

## 配置参数

在 `config/default_config.yaml` 中的 `record` 部分添加了以下超时配置：

```yaml
record:
  # 超时配置（秒）
  file_io_timeout: 15      # 文件I/O操作超时
  db_timeout: 20           # 数据库操作超时
  window_info_timeout: 5   # 获取窗口信息超时
```

### 配置说明

- **file_io_timeout**: 文件读写操作的超时时间，包括截图保存、图像哈希计算等
- **db_timeout**: 数据库操作的超时时间，包括插入截图记录等
- **window_info_timeout**: 获取活动窗口信息的超时时间

## 受保护的操作

以下操作已添加超时保护：

### 文件 I/O 操作
1. **截图保存** (`_save_screenshot`)
   - 将截图保存到指定路径
   - 超时时间：`file_io_timeout`

2. **图像哈希计算** (`_calculate_image_hash`)
   - 计算图像的感知哈希值
   - 超时时间：`file_io_timeout`

3. **图像尺寸获取** (`_get_image_size`)
   - 读取图像文件获取尺寸信息
   - 超时时间：`file_io_timeout`

4. **文件哈希计算** (`_calculate_file_hash`)
   - 计算文件的 MD5 哈希值
   - 超时时间：`file_io_timeout`

### 数据库操作
1. **截图信息保存** (`_save_to_database`)
   - 将截图元数据保存到数据库
   - 超时时间：`db_timeout`

### 外部依赖操作
1. **窗口信息获取** (`_get_window_info`)
   - 获取当前活动窗口的应用名和标题
   - 超时时间：`window_info_timeout`

## 日志记录

当操作超时时，系统会记录警告日志：

```
2025-09-02 20:39:10,562 - lifetrace_recorder - WARNING - 操作超时: 文件保存 (超过 15 秒)
```

日志包含以下信息：
- 操作名称
- 超时时间
- 时间戳

## 测试验证

可以运行 `test_timeout_mechanism.py` 脚本来验证超时机制：

```bash
python test_timeout_mechanism.py
```

测试内容包括：
- 超时装饰器功能测试
- 录制器超时配置验证
- 文件操作超时测试
- 窗口信息获取超时测试

## 优势

1. **防止卡死**: 避免因文件系统或数据库问题导致程序无响应
2. **可配置**: 可根据系统性能调整超时时间
3. **非阻塞**: 超时不会中断录制流程，只记录警告
4. **跨平台**: 兼容 Windows 和 Linux 系统
5. **详细日志**: 便于问题诊断和性能优化

## 注意事项

1. 超时时间应根据系统性能合理设置
2. 频繁超时可能表明系统资源不足或配置问题
3. 超时操作会返回默认值或 None，调用方需要处理这些情况
4. 建议定期检查日志中的超时警告，及时优化系统配置