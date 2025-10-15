import numpy as np
from lifetrace_backend.config import config
from lifetrace_backend.storage import DatabaseManager
from lifetrace_backend.multimodal_vector_service import create_multimodal_vector_service
from lifetrace_backend.multimodal_embedding import get_multimodal_embedding
import requests

def check_image_embeddings():
    """检查图像嵌入向�?""
    print("🔍 检查图像嵌入向�?..")

    # 通过API获取多模态统�?    try:
        stats_response = requests.get('http://127.0.0.1:8843/api/multimodal-stats')
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"📊 API统计: 文本DB={stats.get('text_db_count', 0)}, 图像DB={stats.get('image_db_count', 0)}")
        else:
            print(f"�?无法获取API统计: {stats_response.status_code}")
    except Exception as e:
        print(f"�?API统计异常: {e}")

    # 直接检查多模态嵌入模�?    print("\n🧠 检查多模态嵌入模�?..")
    try:
        multimodal_embedding = get_multimodal_embedding()
        print(f"�?多模态嵌入模型加载成�?)

        # 测试文本嵌入
        test_text = "连接"
        text_embedding = multimodal_embedding.encode_text(test_text)
        print(f"📝 文本嵌入测试:")
        print(f"  - 输入文本: '{test_text}'")
        print(f"  - 嵌入维度: {len(text_embedding)}")
        print(f"  - 嵌入类型: {type(text_embedding)}")
        print(f"  - �?0个�? {text_embedding[:10].tolist()}")
        print(f"  - 向量范数: {np.linalg.norm(text_embedding):.4f}")

        # 测试图像嵌入（如果有图像文件�?        print("\n🖼�?检查数据库中的图像文件...")

        # 通过API获取一些搜索结果来找到图像文件路径
        search_response = requests.post('http://127.0.0.1:8843/api/multimodal-search', json={
            'query': '页面',
            'top_k': 2,
            'text_weight': 1.0,
            'image_weight': 0.0
        })

        if search_response.status_code == 200:
            results = search_response.json()
            if results:
                for i, result in enumerate(results[:2]):
                    screenshot = result.get('screenshot')
                    if screenshot and screenshot.get('file_path'):
                        image_path = screenshot['file_path']
                        print(f"\n📷 测试图像 {i+1}: {image_path}")

                        try:
                            # 测试图像嵌入
                            image_embedding = multimodal_embedding.encode_image(image_path)
                            print(f"  �?图像嵌入生成成功")
                            print(f"  - 嵌入维度: {len(image_embedding)}")
                            print(f"  - 嵌入类型: {type(image_embedding)}")
                            print(f"  - �?0个�? {image_embedding[:10].tolist()}")
                            print(f"  - 向量范数: {np.linalg.norm(image_embedding):.4f}")

                            # 计算文本和图像嵌入的相似�?                            similarity = np.dot(text_embedding, image_embedding) / (np.linalg.norm(text_embedding) * np.linalg.norm(image_embedding))
                            print(f"  - 与文�?{test_text}'的相似度: {similarity:.4f}")

                        except Exception as img_error:
                            print(f"  �?图像嵌入生成失败: {img_error}")
                            import traceback
                            traceback.print_exc()
            else:
                print("�?没有找到搜索结果")
        else:
            print(f"�?搜索请求失败: {search_response.status_code}")

    except Exception as e:
        print(f"�?多模态嵌入模型检查失�? {e}")
        import traceback
        traceback.print_exc()

    # 直接检查向量数据库内容
    print("\n🗄�?直接检查向量数据库...")
    try:
        # 创建一个临时的向量服务来检查数据库
        from lifetrace_backend.vector_db import create_vector_db

        # 创建图像向量数据库配�?        class ImageVectorConfig:
            def __init__(self):
                self.vector_db_enabled = True
                self.vector_db_persist_directory = config.get('vector_db_persist_directory', '.') + '_image'
                self.vector_db_embedding_model = None  # 多模态模式下为空
                self.vector_db_collection_name = 'lifetrace_image'
                self.vector_db_rerank_model = config.get('vector_db_rerank_model', 'cross-encoder/ms-marco-MiniLM-L-6-v2')

            def get(self, key, default=None):
                return getattr(self, key, default)

        image_config = ImageVectorConfig()
        image_vector_db = create_vector_db(image_config)

        image_collection = image_vector_db.collection
        image_count = image_collection.count()
        print(f"📊 图像向量数据库文档数: {image_count}")

        if image_count > 0:
            # 获取一些示例文�?            sample_results = image_collection.get(
                limit=min(3, image_count),
                include=['documents', 'metadatas', 'embeddings']
            )

            print(f"\n📄 图像向量数据库示例文�?")
            for i, (doc_id, doc, metadata, embedding) in enumerate(zip(
                sample_results['ids'],
                sample_results['documents'],
                sample_results['metadatas'],
                sample_results['embeddings'] if sample_results['embeddings'] else [None] * len(sample_results['ids'])
            )):
                print(f"  文档 {i+1}:")
                print(f"    ID: {doc_id}")
                print(f"    文档内容: {doc[:50] if doc else 'None'}...")
                print(f"    OCR结果ID: {metadata.get('ocr_result_id', 'None')}")
                print(f"    截图路径: {metadata.get('screenshot_path', 'None')}")

                if embedding:
                    embedding_array = np.array(embedding)
                    print(f"    嵌入向量维度: {len(embedding)}")
                    print(f"    嵌入向量�?个�? {embedding[:5]}")
                    print(f"    向量范数: {np.linalg.norm(embedding_array):.4f}")
                    print(f"    向量是否全零: {np.allclose(embedding_array, 0)}")
                else:
                    print(f"    �?嵌入向量为空")
                print()
        else:
            print("�?图像向量数据库为�?)

    except Exception as e:
        print(f"�?向量数据库检查失�? {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_image_embeddings()
