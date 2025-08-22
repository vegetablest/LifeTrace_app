# LifeTrace 多模态搜索方�?
## 🎯 方案概述

LifeTrace 多模态搜索功能同时考虑**文本相似�?*�?*图像相似�?*，提供更精准的搜索体验�?
### 核心技�?- **CLIP模型**: 将图像和文本映射到同一向量空间
- **多模态向量数据库**: 分别存储文本和图像嵌入向�?- **权重融合**: 可配置的文本/图像权重组合

## 📁 项目结构

```
lifetrace/
├── multimodal_embedding.py      # CLIP多模态嵌入生�?├── multimodal_vector_service.py # 多模态向量数据库服务
├── server.py                    # 添加多模态API端点
└── templates/index.html         # 前端多模态搜索界�?```

## 🔧 技术架�?
### 1. 嵌入生成�?```
文本内容 �?CLIP文本编码�?�?512维文本向�?截图图像 �?CLIP图像编码�?�?512维图像向�?```

### 2. 存储�?```
文本向量数据�? lifetrace_text/
图像向量数据�? lifetrace_image/
```

### 3. 搜索�?```
查询文本 �?文本向量 �?与存储向量计算相似度
                 �?            综合分数 = α×文本相似�?+ β×图像相似�?```

## 🚀 安装和配�?
### 1. 安装依赖
```bash
# 安装多模态依�?pip install -r requirements_multimodal.txt
```

### 2. 配置文件
�?`config/default_config.yaml` 中：
```yaml
multimodal:
  enabled: true
  model_name: 'openai/clip-vit-base-patch32'
  text_weight: 0.6    # 文本权重
  image_weight: 0.4   # 图像权重
  batch_size: 16
  auto_sync: true
```

### 3. 启动服务
```bash
# 启动LifeTrace服务（包含多模态搜索）
python -m lifetrace_backend.server --port 8843

# 或使用启动脚�?python start_all_services.py
```

## 🎨 前端界面

### 搜索类型
- **传统搜索**: 基于关键词匹�?- **语义搜索**: 基于文本语义理解
- **多模态搜�?*: 同时考虑文本和图像相似度

### 多模态搜索选项
- **返回数量**: 1-50个结�?- **文本权重**: 0.0-1.0 (默认0.6)
- **图像权重**: 0.0-1.0 (默认0.4)

### 结果显示
- **🎭标识**: 多模态搜索结�?- **综合分数**: 加权后的最终相似度
- **详细分数**: 文本相似�?| 图像相似�?
## 📡 API接口

### 多模态搜�?```http
POST /api/multimodal-search
Content-Type: application/json

{
  "query": "编程代码",
  "top_k": 10,
  "text_weight": 0.6,
  "image_weight": 0.4,
  "filters": null
}
```

### 多模态统�?```http
GET /api/multimodal-stats
```

### 多模态同�?```http
POST /api/multimodal-sync?force_reset=false
```

## 🔍 搜索策略

### 权重配置建议
- **文本为主**: text_weight=0.8, image_weight=0.2
- **平衡模式**: text_weight=0.6, image_weight=0.4
- **图像为主**: text_weight=0.3, image_weight=0.7

### 适用场景
1. **代码截图**: 高文本权重，识别代码内容和视觉布局
2. **界面设计**: 高图像权重，关注视觉相似�?3. **文档阅读**: 平衡权重，文字内容和排版都重�?4. **图表数据**: 高图像权重，关注图表形状和结�?
## 🛠�?开发和调试

### 测试脚本
```bash
# 测试多模态功�?python -c "
from lifetrace.multimodal_embedding import get_multimodal_embedding
embedding = get_multimodal_embedding()
print('多模态功能可�?', embedding.is_available())
"
```

### 调试步骤
1. **检查依�?*: 确保PyTorch和CLIP已安�?2. **检查配�?*: 验证multimodal.enabled=true
3. **检查模�?*: CLIP模型下载可能需要时�?4. **检查数�?*: 确保有截图和OCR数据可供搜索

## 📊 性能优化

### 批处理优�?- 文本批量编码: 16-32个文本一�?- 图像批量编码: 8-16个图像一�?
### 内存优化
- 使用CPU推理节省显存
- 定期清理向量数据库缓�?
### 搜索优化
- 预计算常用查询向�?- 使用近似最近邻算法(ANN)

## 🔧 故障排查

### 常见问题

1. **多模态功能不可用**
   ```bash
   # 检查依�?   pip list | grep -E "(torch|transformers|clip)"
   ```

2. **模型下载失败**
   ```bash
   # 设置代理或使用镜�?   export HF_ENDPOINT=https://hf-mirror.com
   ```

3. **搜索结果为空**
   ```bash
   # 检查数据同�?   curl -X POST http://localhost:8843/api/multimodal-sync
   ```

4. **内存不足**
   ```yaml
   # 降低批处理大�?   multimodal:
     batch_size: 8
   ```

### 日志分析
```bash
# 查看多模态日�?tail -f ~/.lifetrace/logs/*.log | grep -i multimodal
```

## 🚀 未来扩展

### 模型升级
- 支持多语言CLIP模型
- 集成Chinese-CLIP
- 支持更大的CLIP模型(ViT-L/14)

### 功能增强
- 图像-图像搜索
- 跨模态搜�?用图像搜文本)
- 时间序列相似�?
### 性能优化
- GPU加速推�?- 向量量化压缩
- 分布式向量数据库

## 📈 效果评估

### 搜索质量指标
- **准确�?*: 相关结果占比
- **召回�?*: 找到的相关结果比�?- **多样�?*: 结果的多样性程�?
### 性能指标
- **搜索延迟**: <2秒响应时�?- **同步速度**: >100条记�?分钟
- **内存使用**: <2GB峰值内�?
通过多模态搜索，LifeTrace 能够提供更智能、更精准的个人数字生活搜索体�? 🎉
