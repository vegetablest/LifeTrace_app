import requests
import json
from lifetrace.config import config
from lifetrace.storage import db_manager
from lifetrace.multimodal_vector_service import create_multimodal_vector_service
from lifetrace.multimodal_embedding import get_multimodal_embedding
import numpy as np

def test_direct_image_search():
    """直接测试图像向量搜索"""
    print("🔍 直接测试图像向量搜索...")
    
    # 创建多模态向量服务
    service = create_multimodal_vector_service(config, db_manager)
    if not service.is_enabled():
        print("❌ 多模态向量服务不可用")
        return
    
    print("✅ 多模态向量服务可用")
    
    # 获取多模态嵌入器
    multimodal_embedding = get_multimodal_embedding()
    if not multimodal_embedding.is_available():
        print("❌ 多模态嵌入器不可用")
        return
    
    print("✅ 多模态嵌入器可用")
    
    # 检查图像向量数据库状态
    if service.image_vector_db is None:
        print("❌ 图像向量数据库未初始化")
        return
    
    image_count = service.image_vector_db.collection.count()
    print(f"📊 图像向量数据库文档数: {image_count}")
    
    if image_count == 0:
        print("❌ 图像向量数据库为空")
        return
    
    # 生成查询嵌入
    query = "编程代码"
    print(f"\n🔍 查询: {query}")
    
    query_embedding = multimodal_embedding.encode_text(query)
    if query_embedding is None:
        print("❌ 无法生成查询嵌入")
        return
    
    print(f"✅ 查询嵌入生成成功，维度: {query_embedding.shape}")
    
    # 直接搜索图像向量数据库
    print("\n🔍 直接搜索图像向量数据库...")
    try:
        collection = service.image_vector_db.collection
        
        # 执行向量搜索
        results = collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5,
            include=['documents', 'metadatas', 'distances']
        )
        
        print(f"✅ 搜索完成，找到 {len(results['ids'][0])} 个结果")
        
        # 详细分析每个结果
        for i in range(len(results['ids'][0])):
            result_id = results['ids'][0][i]
            document = results['documents'][0][i]
            metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
            distance = results['distances'][0][i] if results['distances'] else None
            
            print(f"\n  结果 {i+1}:")
            print(f"    ID: {result_id}")
            print(f"    文档: {document}")
            print(f"    距离: {distance}")
            print(f"    距离类型: {type(distance)}")
            
            if distance is not None:
                similarity = 1.0 / (1.0 + distance)
                print(f"    相似度: {similarity}")
            else:
                print(f"    相似度: 无法计算 (距离为None)")
            
            print(f"    元数据: {metadata}")
            
            ocr_id = metadata.get('ocr_result_id')
            print(f"    OCR ID: {ocr_id} (类型: {type(ocr_id)})")
    
    except Exception as e:
        print(f"❌ 图像向量搜索失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 测试通过服务方法搜索
    print("\n🔍 通过服务方法搜索图像向量...")
    try:
        image_results = service._search_image_with_text(
            query_embedding, 
            5,
            None
        )
        
        print(f"✅ 服务方法搜索完成，找到 {len(image_results)} 个结果")
        
        for i, result in enumerate(image_results):
            print(f"\n  结果 {i+1}:")
            print(f"    ID: {result.get('id')}")
            print(f"    文档: {result.get('document')}")
            print(f"    距离: {result.get('distance')}")
            print(f"    距离类型: {type(result.get('distance'))}")
            
            distance = result.get('distance')
            if distance is not None:
                similarity = 1.0 / (1.0 + distance)
                print(f"    相似度: {similarity}")
            else:
                print(f"    相似度: 无法计算 (距离为None)")
            
            metadata = result.get('metadata', {})
            print(f"    元数据: {metadata}")
            
            ocr_id = metadata.get('ocr_result_id')
            print(f"    OCR ID: {ocr_id} (类型: {type(ocr_id)})")
    
    except Exception as e:
        print(f"❌ 服务方法搜索失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_image_search()