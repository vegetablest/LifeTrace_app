# Debug 和 Test 文件说明

本文件夹包含了 LifeTrace 项目中所有的调试和测试相关文件，按功能分类并编号整理。

## 文件分类和编号规则

### 01-03: 数据库相关
- `01_database_check.py` - 数据库状态检查工具
- `02_database_sync_test.py` - 数据库同步测试
- `03_database_reset.py` - 数据库重置工具

### 04-07: 图像搜索相关
- `04_image_search_debug.py` - 图像搜索功能调试
- `05_image_search_test.py` - 图像搜索功能测试
- `06_image_embeddings_check.py` - 图像嵌入向量检查
- `07_image_vector_add_test.py` - 图像向量添加测试

### 08-09: OCR 相关
- `08_ocr_id_mismatch_debug.py` - OCR ID 不匹配问题调试
- `09_ocr_type_issue_debug.py` - OCR 类型问题调试

### 10-12: 多模态相关
- `10_multimodal_debug.py` - 多模态功能调试
- `11_multimodal_fix_test.py` - 多模态修复测试
- `12_multimodal_db_sync.py` - 多模态数据库同步

### 13-14: 向量数据库相关
- `13_vector_db_debug.py` - 向量数据库调试
- `14_semantic_search_fix_test.py` - 语义搜索修复测试

### 15-16: 集成测试
- `15_integration_test.py` - 系统集成测试
- `16_simple_test.py` - 简单功能测试

### 17-18: 工具和演示
- `17_manual_reset.py` - 手动重置工具
- `18_demo_image_similarity.py` - 图像相似度演示程序

### 19-24: 重复文件（后发现）
- `19_database_sync_test_duplicate.py` - 数据库同步测试（重复）
- `20_integration_test_duplicate.py` - 系统集成测试（重复）
- `21_semantic_search_fix_test_duplicate.py` - 语义搜索修复测试（重复）
- `22_simple_test_duplicate.py` - 简单功能测试（重复）
- `23_database_reset_duplicate.py` - 数据库重置工具（重复）
- `24_manual_reset_duplicate.py` - 手动重置工具（重复）

### 25-31: 剩余文件（最后发现）
- `25_vector_db_debug_remaining.py` - 向量数据库调试（剩余）
- `26_database_sync_test_remaining.py` - 数据库同步测试（剩余）
- `27_integration_test_remaining.py` - 系统集成测试（剩余）
- `28_semantic_search_fix_test_remaining.py` - 语义搜索修复测试（剩余）
- `29_simple_test_remaining.py` - 简单功能测试（剩余）
- `30_database_reset_remaining.py` - 数据库重置工具（剩余）
- `31_manual_reset_remaining.py` - 手动重置工具（剩余）

### 32-38: 最终文件（彻底清理）
- `32_vector_db_debug_final.py` - 向量数据库调试（最终）
- `33_manual_reset_final.py` - 手动重置工具（最终）
- `34_database_reset_final.py` - 数据库重置工具（最终）
- `35_simple_test_final.py` - 简单功能测试（最终）
- `36_database_sync_test_final.py` - 数据库同步测试（最终）
- `37_integration_test_final.py` - 系统集成测试（最终）
- `38_semantic_search_fix_test_final.py` - 语义搜索修复测试（最终）

### 日志文件
- `debug_vector_db.log` - 向量数据库调试日志
- `debug_vector_db_duplicate.log` - 向量数据库调试日志（重复）
- `debug_vector_db_remaining.log` - 向量数据库调试日志（剩余）
- `debug_vector_db_final.log` - 向量数据库调试日志（最终）

## 使用说明

1. 所有文件都保持原有功能不变，只是重新组织了目录结构
2. 编号按照功能模块分组，便于查找和维护
3. 运行这些文件时，请确保在项目根目录下执行
4. 部分文件可能需要特定的环境配置或数据库状态

## 注意事项

- 运行调试和测试文件前，请确保相关服务已启动
- 某些文件可能会修改数据库状态，请谨慎使用
- 建议在测试环境中运行这些文件