# 配置热重载功能使用说明

## 简介

LifeTrace现在支持配置文件自动热重载功能！修改`config/config.yaml`后，各进程会自动检测并应用新配置，无需手动重启。

## 快速开始

### 1. 确保依赖已安装

配置热重载功能依赖`watchdog`库，该库已包含在requirements中：

```bash
conda activate laptop_showcase
pip install watchdog>=3.0.0
```

### 2. 正常启动服务

正常启动Server、Recorder、OCR进程，配置监听会自动开启：

```bash
# 启动Server
python -m lifetrace_backend.server

# 启动Recorder
python -m lifetrace_backend.recorder

# 启动OCR
python -m lifetrace_backend.simple_ocr
```

### 3. 修改配置

直接编辑`config/config.yaml`文件，保存后配置会自动生效：

```yaml
record:
  interval: 3  # 修改截图间隔为3秒
  
ocr:
  check_interval: 10  # 修改OCR检查间隔为10秒
```

### 4. 观察日志

查看进程日志，确认配置变更：

```
检测到配置文件变更: config/config.yaml
配置文件已重新加载
截图间隔已更新: 1s -> 3s
```

## 支持的配置项

### Server进程
- LLM配置（API Key、Base URL、Model等）
- 服务器配置（Host、Port）
- 所有其他配置项

### Recorder进程
- 截图间隔：`record.interval`
- 监控屏幕：`record.screens`
- 去重功能：`storage.deduplicate`
- 去重阈值：`storage.hash_threshold`
- 黑名单配置：`record.blacklist.*`

### OCR进程
- 检查间隔：`ocr.check_interval`
- OCR启用：`ocr.enabled`
- 置信度阈值：`ocr.confidence_threshold`

## 使用示例

### 示例1：动态调整截图间隔

录制过程中想减少系统负担：

1. 编辑`config/config.yaml`：
```yaml
record:
  interval: 5  # 改为5秒截图一次
```

2. 保存文件，Recorder自动应用新间隔

### 示例2：临时启用黑名单

录制时想排除某些应用：

1. 编辑`config/config.yaml`：
```yaml
record:
  blacklist:
    enabled: true
    apps:
      - "WeChat"
      - "QQ"
```

2. 保存文件，立即生效，不再截图这些应用

### 示例3：调整OCR处理频率

OCR处理太频繁时：

1. 编辑`config/config.yaml`：
```yaml
ocr:
  check_interval: 15  # 改为15秒检查一次
```

2. 保存文件，OCR进程自动调整检查频率

## 注意事项

1. **配置语法正确**：确保YAML语法正确，否则会保留旧配置
2. **不重新初始化服务**：配置更新不会重新创建OCR引擎等重量级对象
3. **立即生效**：大部分配置变更立即生效
4. **线程安全**：多进程同时修改配置文件是安全的

## 验证功能

运行自动化测试脚本验证功能：

```bash
conda activate laptop_showcase
python test_config_hot_reload.py
```

预期输出：
```
总计: 5/5 测试通过
🎉 所有测试通过！配置热重载功能工作正常。
```

## 故障排查

### 配置未生效

检查日志中是否有"检测到配置文件变更"消息：
- 如果没有：检查watchdog库是否安装
- 如果有但配置未变：检查配置文件语法是否正确

### watchdog不可用

如果看到"watchdog库不可用"警告：
```bash
pip install watchdog>=3.0.0
```

## 更多信息

详细的测试指南和技术文档：
- [配置热重载测试指南](config_hot_reload_test.md)
- [实现计划](.plan.md)

享受无需重启的配置管理体验！🎉

