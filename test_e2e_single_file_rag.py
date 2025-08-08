#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
端到端单文件RAG流程测试
- 启动前确保ES与Python服务可用（可使用 start_python_service.bat）
- 步骤：上传→入库→RAG问答→输出评测
"""

import os
import time
import json
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"
TEST_FILE = "python_service/file/店铺入住流程.pdf"  # 用一个文件节省开支

HEADERS = {
    "accept": "application/json"
}

def wait_service_ready(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/api/health", timeout=3)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(1)
    return False


def upload_and_index_file(file_path: str, knowledge_id: int = 1):
    files = {
        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream')
    }
    data = {
        'knowledge_id': str(knowledge_id),
        'knowledge_name': '测试知识',
        'description': '端到端单文件测试',
        'tags': '测试,流程',
        'effective_time': '2024-01-01'
    }
    resp = requests.post(f"{BASE_URL}/api/document/process", files=files, data=data, timeout=120)
    return resp


def rag_ask(question: str, user_id: str = "tester"):
    payload = {"question": question, "user_id": user_id}
    resp = requests.post(f"{BASE_URL}/api/rag/chat", headers={'Content-Type': 'application/json'}, json=payload, timeout=60)
    return resp


def evaluate_answer(answer: str) -> dict:
    # 简易评测：长度、是否包含关键字、是否有结构
    score = 0
    length = len(answer)
    if length > 50:
        score += 30
    if any(k in answer for k in ["流程", "步骤", "文档", "内容", "基于", "参考"]):
        score += 40
    if any(punct in answer for punct in ['。', '.', '\n- ', '\n1.']):
        score += 30
    return {"answer_length": length, "score": score}


def main():
    report = {"steps": []}

    # 1. 等待服务就绪
    ok = wait_service_ready(60)
    report["service_ready"] = ok
    if not ok:
        print("❌ 服务未就绪，请先运行 start_python_service.bat")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    # 2. 上传并入库
    if not os.path.exists(TEST_FILE):
        print(f"❌ 测试文件不存在: {TEST_FILE}")
        return
    resp = upload_and_index_file(TEST_FILE, knowledge_id=1001)
    step = {"stage": "upload", "status_code": resp.status_code}
    try:
        step["response"] = resp.json()
    except Exception:
        step["response_text"] = resp.text[:500]
    report["steps"].append(step)
    if resp.status_code != 200:
        print("❌ 上传/入库失败")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return

    # 3. RAG问答（只问一个问题）
    question = "请根据文档给出店铺入驻的关键步骤概览？"
    resp2 = rag_ask(question)
    step2 = {"stage": "rag", "status_code": resp2.status_code}
    try:
        rag_json = resp2.json()
        step2["response"] = rag_json
        answer = rag_json.get("answer", "")
    except Exception:
        step2["response_text"] = resp2.text[:1000]
        answer = step2["response_text"]
    report["steps"].append(step2)

    # 4. 评测
    eval_res = evaluate_answer(answer)
    report["evaluation"] = eval_res

    # 输出报告
    out = "e2e_single_file_rag_report.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"✅ 测试完成，报告: {out}")

if __name__ == "__main__":
    main()
