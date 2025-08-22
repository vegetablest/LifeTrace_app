# 日志目录结构

本目录包含 LifeTrace 应用的所有日志文件。

## 目录结构

- `app/` - 应用程序日志
  - `lifetrace.log` - 主应用日志
  - `lifetrace.log.1`, `lifetrace.log.2` - 轮转的历史日志

- `error/` - 错误日志
  - `error.log` - 错误级别日志
  - `error.log.1`, `error.log.2` - 轮转的历史错误日志

- `debug/` - 调试日志
  - `debug.log` - 调试级别日志
  - `debug.log.1`, `debug.log.2` - 轮转的历史调试日志

- `archive/` - 归档日志
  - 压缩的历史日志文件

## 日志轮转策略

- 单个日志文件最大大小：10MB
- 保留历史文件数量：5个
- 轮转频率：当文件大小超过限制时自动轮转
- 归档策略：超过保留数量的文件会被压缩并移动到 archive 目录

## 日志级别

- `DEBUG` - 详细的调试信息
- `INFO` - 一般信息
- `WARNING` - 警告信息
- `ERROR` - 错误信息
- `CRITICAL` - 严重错误信息

## 配置

日志配置在 `lifetrace/logging_config.py` 中定义，可以通过 `config/default_config.yaml` 进行调整。