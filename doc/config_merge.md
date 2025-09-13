# LifeTrace 配置合并机制

## 概述

LifeTrace 应用现在支持配置合并机制，允许用户通过自定义配置文件覆盖默认配置中的部分设置，而不需要完全复制整个配置文件。这种机制使配置管理更加灵活和方便。

## 配置文件加载顺序

系统按照以下顺序查找配置文件：

1. 项目目录下的 `config/default_config.yaml`（默认配置）
2. 项目目录下的 `~/config.yaml`（用户配置）
3. 用户主目录下的 `.lifetrace/config.yaml`（用户配置）

## 配置合并机制

配置加载过程如下：

1. 首先加载默认配置（`default_config.yaml`）
2. 如果存在用户配置文件（`~/config.yaml` 或 `.lifetrace/config.yaml`），则加载用户配置
3. 用户配置中的设置会覆盖默认配置中的同名设置
4. 对于嵌套的配置项（如 `server.port`），系统会递归合并，只覆盖用户配置中指定的部分

## 使用示例

### 默认配置（default_config.yaml）

```yaml
base_dir: ~/
database_path: lifetrace.db
screenshots_dir: screenshots
server:
  host: 127.0.0.1
  port: 8840
  debug: false
record:
  interval: 3
  screens: [3]
```

### 用户配置（~/config.yaml）

```yaml
# 只需要包含要覆盖的配置项
record:
  interval: 1  # 覆盖默认值
  screens: all  # 覆盖默认值
server:
  # host 未指定，将保留默认值 127.0.0.1
  port: 9000  # 覆盖默认值
```

### 最终合并结果

```yaml
base_dir: ~/
database_path: lifetrace.db
screenshots_dir: screenshots
server:
  host: 127.0.0.1  # 保留默认值
  port: 9000  # 使用用户配置值
  debug: false  # 保留默认值
record:
  interval: 1  # 使用用户配置值
  screens: all  # 使用用户配置值
```

## 注意事项

1. 用户配置文件只需包含要覆盖的配置项，不需要复制整个默认配置
2. 对于嵌套的配置项，系统会智能合并，只覆盖指定的部分
3. 用户配置可以添加默认配置中不存在的新配置项
4. 配置合并是递归进行的，可以处理任意深度的嵌套配置

## 技术实现

配置合并功能通过 `LifeTraceConfig` 类中的 `_merge_configs` 方法实现，该方法递归合并两个配置字典，用户配置的值会覆盖默认配置中的同名项。

```python
def _merge_configs(self, default_config: dict, user_config: dict):
    """递归合并配置，用户配置会覆盖默认配置中的同名项"""
    for key, value in user_config.items():
        if isinstance(value, dict) and key in default_config and isinstance(default_config[key], dict):
            # 如果两边都是字典，递归合并
            self._merge_configs(default_config[key], value)
        else:
            # 否则直接覆盖
            default_config[key] = value
```