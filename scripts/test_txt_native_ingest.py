#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试脚本：验证 TXT 原生解析与入库

功能：
- 调用 Python 服务 /api/document/process 上传一个 TXT 文件（不转 PDF）
- 成功后从 ES 检索该知识与文件对应的 chunks，打印关键元数据（page_num、chunk_index、positions 数量）

运行示例：
  python scripts/test_txt_native_ingest.py --python-url http://localhost:8000 --file python_service/file/sample.txt --knowledge-id 102 --name 测试TXT
"""

import argparse
import json
import os
import sys
import time
import traceback
from typing import Any, Dict

import requests


def add_python_service_to_path():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_dir = os.path.join(repo_root, 'python_service')
    if os.path.isdir(py_dir) and py_dir not in sys.path:
        sys.path.insert(0, py_dir)


def process_document(python_url: str, file_path: str, knowledge_id: int, knowledge_name: str,
                     description: str = None, tags: str = None, effective_time: str = None) -> Dict[str, Any]:
    url = f"{python_url.rstrip('/')}/api/document/process"
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'text/plain')
    }
    data = {
        'knowledge_id': str(knowledge_id),
        'knowledge_name': knowledge_name,
    }
    if description:
        data['description'] = description
    if tags:
        data['tags'] = tags
    if effective_time:
        data['effective_time'] = effective_time

    resp = requests.post(url, files=files, data=data, timeout=120)
    resp.raise_for_status()
    return resp.json()


def search_es(knowledge_id: int, source_file: str) -> None:
    add_python_service_to_path()
    try:
        from config import ES_CONFIG
    except Exception:
        print("无法导入 python_service/config.py，跳过 ES 检索")
        return

    from elasticsearch import Elasticsearch

    es = Elasticsearch(
        [f"http://{ES_CONFIG['host']}:{ES_CONFIG['port']}"] ,
        basic_auth=(ES_CONFIG.get('username') or None, ES_CONFIG.get('password') or None) if ES_CONFIG.get('username') else None,
        verify_certs=ES_CONFIG.get('verify_certs', False)
    )
    index = ES_CONFIG['index']
    try:
        es.indices.refresh(index=index)
    except Exception:
        pass

    def run_and_print(q, note: str):
        res = es.search(index=index, body=q)
        hits = res.get('hits', {}).get('hits', [])
        print(f"ES 命中条数: {len(hits)} (打印最多5条样例) - {note}")
        for i, h in enumerate(hits[:5]):
            src = h['_source']
            content_preview = (src.get('content') or '')[:60].replace('\n', ' ')
            positions = src.get('positions') or []
            print(f"—— 样例 {i+1} ——")
            print(f"knowledge_id={src.get('knowledge_id')}  knowledge_name={src.get('knowledge_name')}")
            print(f"source_file={src.get('source_file')}  page_num={src.get('page_num')}  chunk_index={src.get('chunk_index')}")
            print(f"positions_count={len(positions)}  bbox={(src.get('bbox') or [])}")
            print(f"content_preview={content_preview}")
        return len(hits)

    base_source = [
        "knowledge_id", "knowledge_name", "description", "tags", "effective_time",
        "source_file", "page_num", "chunk_index", "bbox", "positions", "content"
    ]

    # 方案1：按 knowledge_id + source_file.keyword 精确匹配
    query_keyword = {
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {"term": {"knowledge_id": knowledge_id}},
                    {"term": {"source_file.keyword": source_file}}
                ]
            }
        },
        "_source": base_source
    }

    n = run_and_print(query_keyword, "knowledge_id + source_file.keyword")
    if n > 0:
        return

    # 方案2：按 knowledge_id + source_file 短语匹配
    query_phrase = {
        "size": 10,
        "query": {
            "bool": {
                "must": [
                    {"term": {"knowledge_id": knowledge_id}},
                    {"match_phrase": {"source_file": source_file}}
                ]
            }
        },
        "_source": base_source
    }
    n = run_and_print(query_phrase, "knowledge_id + source_file 短语匹配")
    if n > 0:
        return

    # 方案3：仅按 knowledge_id（验证是否成功入库）
    query_kid_only = {
        "size": 10,
        "query": {"term": {"knowledge_id": knowledge_id}},
        "_source": base_source
    }
    run_and_print(query_kid_only, "仅 knowledge_id（排查）")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--python-url', default='http://localhost:8000')
    parser.add_argument('--file', required=True, help='TXT 文件路径 (.txt)')
    parser.add_argument('--knowledge-id', type=int, required=True)
    parser.add_argument('--name', required=True, help='知识名称')
    parser.add_argument('--description', default=None)
    parser.add_argument('--tags', default=None, help='逗号分隔字符串')
    parser.add_argument('--effective-time', default=None)
    args = parser.parse_args()

    try:
        print(f"上传并处理: {args.file}")
        result = process_document(
            python_url=args.python_url,
            file_path=args.file,
            knowledge_id=args.knowledge_id,
            knowledge_name=args.name,
            description=args.description,
            tags=args.tags,
            effective_time=args.effective_time,
        )
        print("处理结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))

        time.sleep(2)
        print("\n从 ES 检索样例块:")
        search_es(args.knowledge_id, os.path.basename(args.file))

        print("\n✅ TXT 原生解析验证完成")
    except Exception as e:
        print("❌ 运行失败:")
        print(str(e))
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()






