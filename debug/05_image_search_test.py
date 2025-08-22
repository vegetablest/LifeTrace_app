import requests
import json

# 测试图像搜索分数
response = requests.post('http://127.0.0.1:8843/api/multimodal-search', json={
    'query': '连接',
    'top_k': 3,
    'text_weight': 0.1,
    'image_weight': 0.9
})

results = response.json()
print('🔍 图像权重测试 (text_weight=0.1, image_weight=0.9):')
for i, result in enumerate(results):
    print(f'  结果 {i+1}:')
    print(f'    text_score: {result["text_score"]:.3f}')
    print(f'    image_score: {result["image_score"]:.3f}')
    print(f'    combined_score: {result["combined_score"]:.3f}')
    print()

# 测试纯图像搜�?response2 = requests.post('http://127.0.0.1:8843/api/multimodal-search', json={
    'query': '页面',
    'top_k': 2,
    'text_weight': 0.0,
    'image_weight': 1.0
})

results2 = response2.json()
print('🖼�?纯图像搜索测�?(text_weight=0.0, image_weight=1.0):')
for i, result in enumerate(results2):
    print(f'  结果 {i+1}:')
    print(f'    text_score: {result["text_score"]:.3f}')
    print(f'    image_score: {result["image_score"]:.3f}')
    print(f'    combined_score: {result["combined_score"]:.3f}')
    print()
