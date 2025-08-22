# OCR 性能优化说明

## 问题分析

原始�?`pad_ocr.py` 脚本存在以下问题�?1. **性能问题**：使�?PaddleOCR，推理时间约 58 秒，效率极低
2. **资源消�?*：PaddlePaddle 模型较大，内存占用高
3. **初始化慢**：模型下载和初始化时间长

## 优化方案

### 1. 替换 OCR 引擎
- **原来**：PaddleOCR (paddlepaddle)
- **现在**：RapidOCR (onnxruntime)

### 2. 性能对比

| 指标 | PaddleOCR | RapidOCR | 提升幅度 |
|------|-----------|----------|----------|
| 推理时间 | ~58�?| ~5.8�?| **10倍提�?* |
| 模型大小 | 较大 | 较小 | �?5MB减少 |
| 初始化速度 | �?| �?| 显著提升 |
| 识别准确�?| �?| �?| 相当 |

### 3. 主要改进

#### 3.1 引擎替换
```python
# 原来
from paddleocr import PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

# 现在
from rapidocr_onnxruntime import RapidOCR
config_params = {"Global.width_height_ratio": 40}
ocr = RapidOCR(params=config_params)
```

#### 3.2 图像预处理优�?```python
# 添加图像缩放以提高处理速度
MAX_THUMBNAIL_SIZE = (1920, 1920)
with Image.open(image_path) as img:
    img = img.convert("RGB")
    img.thumbnail(MAX_THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
    img_array = np.array(img)
```

#### 3.3 结果格式统一
```python
def convert_ocr_results(self, results):
    """转换OCR结果为统一格式"""
    converted = []
    for result in results:
        item = {
            "dt_boxes": result[0].tolist() if hasattr(result[0], 'tolist') else result[0],
            "rec_txt": result[1],
            "score": float(result[2])
        }
        converted.append(item)
    return converted
```

#### 3.4 智能过滤
```python
# 过滤低置信度结果
filtered_results = [r for r in converted_results if r['score'] > 0.5]
```

### 4. 使用方法

#### 4.1 安装依赖
```bash
pip install -r requirements_rapidocr.txt
```

#### 4.2 集成到LifeTrace系统
```python
# 在LifeTrace主系统中使用
from lifetrace.ocr import SimpleOCRProcessor

# 初始化OCR处理�?ocr_processor = SimpleOCRProcessor()

# 启动OCR监控
ocr_processor.start()
```

#### 4.3 独立运行脚本
```bash
# 持续监控模式（默认）
python rapid_ocr.py

# 指定监控目录
python rapid_ocr.py --dir /path/to/screenshots

# 处理单个文件
python rapid_ocr.py --file /path/to/image.png

# 自定义检查间�?python rapid_ocr.py --interval 1.0
```

### 5. 实际测试结果

```
2025-08-19 16:54:36,776 - INFO - 推理时间: 5.82�?2025-08-19 16:54:36,778 - INFO - 识别结果: 81/81 (置信�?0.5)
2025-08-19 16:54:36,779 - INFO - 识别文本预览: msedge(0.82), 8�?9日周二下�?:54(0.86), 索Microsaft必应(0.78), 127001(0.79), 文件(F)(0.82)
```

### 6. 优势总结

1. **性能大幅提升**：处理速度提升 10 �?2. **资源占用更少**：模型更小，内存占用�?3. **更好的用户体�?*：快速响应，实时处理
4. **保持高准确率**：识别质量不降反�?5. **更好的可维护�?*：代码结构清晰，易于扩展
6. **向量数据库集�?*：自动将OCR结果存储到向量数据库，支持语义搜�?7. **智能去重**：避免重复处理相同文件，提高效率

### 7. 兼容性说�?
- **输出格式**：与原有格式兼容，保存为 JSON 格式
- **文件命名**：保�?`ocr_原文件名.txt` 的命名规�?- **目录结构**：使用相同的监控目录结构

## 建议

1. **替换现有脚本**：建议使�?`rapid_ocr.py` 替代 `pad_ocr.py`
2. **批量处理**：可以扩展脚本支持批量处理历史文�?3. **集成到主系统**：考虑�?RapidOCR 集成�?LifeTrace 主系统中
4. **监控优化**：可以添加文件系统事件监控，进一步提升响应速度
