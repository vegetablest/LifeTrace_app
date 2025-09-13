```
# LifeTrace 配置文件复制机制

## 概述

LifeTrace 应用现在使用配置文件复制机制，在初始化时会直接复制 `default_config.yaml` 到 `config.yaml`，而不再使用之前的配置合并机制。这种方式简化了配置管理，确保用户始终使用完整的配置文件。同时，配置文件路径也已更新，不再使用用户主目录下的 `.lifetrace` 目录。

## 配置文件加载顺序

系统按照以下顺序查找配置文件：

1. 项目目录下的 `~/config.yaml`（用户配置）

如果没有找到配置文件，系统会使用内置的默认配置。注意：不再使用用户主目录下的 `.lifetrace/config.yaml` 路径。

## 配置文件创建机制

当执行 `lifetrace init` 命令或者配置文件不存在时，系统会：

1. 直接复制 `config/default_config.yaml` 到用户配置文件位置（`~/config.yaml`）
2. 不再使用用户主目录下的 `.lifetrace` 目录
3. 不再进行配置合并，确保用户配置文件包含所有最新的配置项

## 配置文件加载机制

配置加载过程如下：

1. 系统直接加载用户配置文件（`~/config.yaml`）
2. 不再从默认配置文件加载或合并配置
3. 如果用户配置文件不存在，则使用内置的默认配置
4. 不再查找或使用用户主目录下的 `.lifetrace/config.yaml` 文件

## 使用说明

### 初始化配置

```bash
# 初始化系统（会创建配置文件）
python -m lifetrace_backend.commands init

# 强制重新初始化（会覆盖现有配置文件）
python -m lifetrace_backend.commands init --force
```

### 修改配置

直接编辑 `~/config.yaml` 文件，修改所需的配置项。注意：不再使用用户主目录下的 `.lifetrace` 目录。

### 重置配置

如果需要重置配置到默认状态，可以删除 `~/config.yaml` 文件，然后重新执行初始化命令：

```bash
python -m lifetrace_backend.commands init
```

## 技术实现

### 配置保存方法

```python
def save_config(self):
    """保存配置到文件
    直接复制default_config.yaml到config.yaml，不进行配置合并
    不再使用用户主目录下的.lifetrace目录
    """
    os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
    
    # 获取默认配置文件路径
    default_config_path = os.path.join(Path(__file__).parent.parent, 'config', 'default_config.yaml')
    
    # 直接复制default_config.yaml到config.yaml
    if os.path.exists(default_config_path):
        import shutil
        shutil.copy2(default_config_path, self.config_path)
        # 重新加载配置
        self._config = self._load_config()
    else:
        # 如果默认配置文件不存在，则使用硬编码的默认配置
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self._get_default_config(), f, allow_unicode=True, default_flow_style=False)
```

### 配置路径获取方法

```python
def _get_config_path(self) -> str:
    """获取配置文件路径
    不再使用用户主目录下的.lifetrace目录
    """
    # 使用项目目录下的~/config.yaml
    return os.path.join(Path(__file__).parent.parent, '~', 'config.yaml')
```

### 配置加载方法

```python
def _load_config(self) -> dict:
    """加载配置文件
    直接加载配置文件，不进行配置合并
    不再查找或使用用户主目录下的.lifetrace目录
    """
    # 如果配置文件存在，直接加载
    if os.path.exists(self.config_path):
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
            return config
    
    # 如果配置文件不存在，返回默认配置
    return self._get_default_config()
```