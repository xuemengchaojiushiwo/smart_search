#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键创建/重建 ES 索引（knowledge_chunks），用于存储"知识+附件"分块
- 支持 dense_vector(1536)
- 支持页码、位置（char_start/char_end）、元信息块（knowledge_meta）
"""
import requests
import json

ES_BASE = "http://localhost:9200"
INDEX = "knowledge_base"  # 若你想独立索引，可改为 knowledge_chunks，并在服务中同步修改 ES_CONFIG['index']
AUTH = ("elastic", "password")

mapping = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "knowledge_id": {"type": "long"},
            "knowledge_name": {"type": "keyword"},
            "description": {"type": "text"},
            "tags": {"type": "keyword"},
            "effective_time": {"type": "keyword"},  # 改为keyword类型，避免日期解析错误
            "attachment_name": {"type": "keyword"},
            "source_file": {"type": "keyword"},
            "file_type": {"type": "keyword"},
            "chunk_index": {"type": "integer"},
            "chunk_type": {"type": "keyword"},
            "weight": {"type": "float"},
            "page_num": {"type": "integer"},
            "char_start": {"type": "integer"},
            "char_end": {"type": "integer"},
            "content": {"type": "text"},
            "embedding": {"type": "dense_vector", "dims": 1536}
        }
    }
}

def delete_index():
    r = requests.delete(f"{ES_BASE}/{INDEX}", auth=AUTH)
    print("DELETE", r.status_code, r.text)

def create_index():
    headers = {"Content-Type": "application/json"}
    r = requests.put(f"{ES_BASE}/{INDEX}", auth=AUTH, headers=headers, data=json.dumps(mapping))
    print("PUT", r.status_code, r.text)

def show_mapping():
    r = requests.get(f"{ES_BASE}/{INDEX}/_mapping", auth=AUTH)
    print("GET _mapping", r.status_code)
    print(r.text)

if __name__ == "__main__":
    try:
        delete_index()
    except Exception as e:
        print("ignore delete error:", e)
    create_index()
    show_mapping()
