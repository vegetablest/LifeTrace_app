#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_api():
    base_url = "http://127.0.0.1:8842/api"
    
    print("=== LifeTrace API Test ===")
    
    # 1. Health check
    print("\n1. Health check...")
    try:
        response = requests.get(f"http://127.0.0.1:8842/health")
        if response.status_code == 200:
            data = response.json()
            print(f"OK: {data}")
        else:
            print(f"Failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # 2. Statistics
    print("\n2. Get statistics...")
    try:
        response = requests.get(f"{base_url}/statistics")
        if response.status_code == 200:
            stats = response.json()
            print(f"Stats: {stats}")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 3. Traditional search
    print("\n3. Traditional search...")
    try:
        search_data = {"query": "test", "limit": 5}
        response = requests.post(f"{base_url}/search", json=search_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Traditional search OK: {len(results)} results")
            if results:
                print(f"Sample: {results[0].get('window_title', 'N/A')}")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 4. Semantic search
    print("\n4. Semantic search...")
    try:
        semantic_data = {"query": "code", "top_k": 5}
        response = requests.post(f"{base_url}/semantic-search", json=semantic_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Semantic search OK: {len(results)} results")
            if results:
                print(f"Score: {results[0].get('score', 0):.3f}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 5. Multimodal search
    print("\n5. Multimodal search...")
    try:
        multimodal_data = {"query": "programming", "top_k": 5}
        response = requests.post(f"{base_url}/multimodal-search", json=multimodal_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Multimodal search OK: {len(results)} results")
            if results:
                result = results[0]
                print(f"Combined score: {result.get('combined_score', 0):.3f}")
                print(f"Text score: {result.get('text_score', 0):.3f}")
                print(f"Image score: {result.get('image_score', 0):.3f}")
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 6. Vector stats
    print("\n6. Vector database status...")
    try:
        response = requests.get(f"{base_url}/vector-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Vector DB: enabled={stats.get('enabled')}, docs={stats.get('document_count')}")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    # 7. Multimodal stats
    print("\n7. Multimodal status...")
    try:
        response = requests.get(f"{base_url}/multimodal-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"Multimodal: enabled={stats.get('enabled')}, available={stats.get('multimodal_available')}")
            print(f"Weights: text={stats.get('text_weight')}, image={stats.get('image_weight')}")
        else:
            print(f"Failed: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_api()
