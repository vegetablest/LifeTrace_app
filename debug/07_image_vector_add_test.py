import numpy as np
from lifetrace_backend.config import config
from lifetrace_backend.storage import db_manager
from lifetrace_backend.multimodal_vector_service import create_multimodal_vector_service
from lifetrace_backend.multimodal_embedding import get_multimodal_embedding
import requests

def test_image_vector_addition():
    """测试图像向量的直接添�?""
    print("🔍 测试图像向量添加...")

    # 获取多模态嵌入器
    multimodal_embedding = get_multimodal_embedding()
    if not multimodal_embedding.is_available():
        print("�?多模态嵌入器不可�?)
        return

    print("�?多模态嵌入器可用")

    # 创建多模态向量服�?    service = create_multimodal_vector_service(config, db_manager)
    if not service.is_enabled():
        print("�?多模态向量服务不可用")
        return

    print("�?多模态向量服务可�?)

    # 获取一些现有的OCR结果和截�?    print("\n📋 获取现有数据...")
    try:
        search_response = requests.post('http://127.0.0.1:8843/api/multimodal-search', json={
            'query': '页面',
            'top_k': 2,
            'text_weight': 1.0,
            'image_weight': 0.0
        })

        if search_response.status_code == 200:
            results = search_response.json()
            if results:
                for i, result in enumerate(results[:1]):
                    screenshot = result.get('screenshot')
                    if screenshot and screenshot.get('file_path'):
                        image_path = screenshot['file_path']
                        ocr_result_id = result.get('id')

                        print(f"\n🖼�?测试图像: {image_path}")
                        print(f"📝 OCR结果ID: {ocr_result_id}")

                        # 生成图像嵌入
                        try:
                            image_embedding = multimodal_embedding.encode_image(image_path)
                            if image_embedding is not None:
                                print(f"�?图像嵌入生成成功，维�? {len(image_embedding)}")
                                print(f"📊 向量范数: {np.linalg.norm(image_embedding):.4f}")

                                # 直接测试向量数据库添�?                                doc_id = f"test_image_{ocr_result_id or 'unknown'}"
                                metadata = {
                                    "modality": "image",
                                    "ocr_result_id": str(ocr_result_id) if ocr_result_id is not None else "unknown",
                                    "screenshot_path": image_path,
                                    "test": "true"
                                }

                                print(f"\n🔧 测试直接添加到图像向量数据库...")
                                success = service.image_vector_db.add_document_with_embedding(
                                    doc_id=doc_id,
                                    text=image_path,
                                    embedding=image_embedding.tolist(),
                                    metadata=metadata
                                )

                                if success:
                                    print(f"�?成功添加到图像向量数据库")

                                    # 验证添加结果
                                    image_count = service.image_vector_db.collection.count()
                                    print(f"📊 图像向量数据库文档数: {image_count}")

                                    # 测试搜索
                                    print(f"\n🔍 测试图像向量搜索...")
                                    search_results = service.image_vector_db.collection.query(
                                        query_embeddings=[image_embedding.tolist()],
                                        n_results=3,
                                        include=['documents', 'metadatas', 'distances']
                                    )

                                    if search_results['ids'][0]:
                                        print(f"�?找到 {len(search_results['ids'][0])} 个搜索结�?)
                                        for j, (result_id, doc, metadata, distance) in enumerate(zip(
                                            search_results['ids'][0],
                                            search_results['documents'][0],
                                            search_results['metadatas'][0],
                                            search_results['distances'][0] if search_results['distances'] else [None] * len(search_results['ids'][0])
                                        )):
                                            print(f"  结果 {j+1}:")
                                            print(f"    ID: {result_id}")
                                            print(f"    文档: {doc[:50]}...")
                                            print(f"    距离: {distance}")
                                            print(f"    OCR结果ID: {metadata.get('ocr_result_id')}")
                                    else:
                                        print("�?搜索未返回结�?)

                                else:
                                    print(f"�?添加到图像向量数据库失败")

                            else:
                                print(f"�?图像嵌入生成失败")

                        except Exception as e:
                            print(f"�?图像处理异常: {e}")
                            import traceback
                            traceback.print_exc()

            else:
                print("�?没有找到现有数据")
        else:
            print(f"�?获取数据失败: {search_response.status_code}")

    except Exception as e:
        print(f"�?测试异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_image_vector_addition()
