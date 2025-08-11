#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG查询功能
"""

import requests
import json

def test_rag_query(question):
    """测试RAG查询"""
    
    # RAG查询接口
    url = "http://localhost:8000/api/rag/chat"
    
    # 请求数据
    data = {
        "question": question,
        "user_id": "test_user"
    }
    
    print(f"🔍 测试问题: {question}")
    print(f"🌐 请求URL: {url}")
    print("-" * 60)
    
    try:
        # 发送请求
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RAG查询成功!")
            print(f"📄 回答: {result.get('answer', 'N/A')}")
            
            # 显示引用信息
            references = result.get('references', [])
            print(f"\n📚 引用数量: {len(references)}")
            
            for i, ref in enumerate(references):
                print(f"\n📖 引用 {i+1}:")
                print(f"   相关度: {ref.get('relevance', 0):.4f}")
                print(f"   源文件: {ref.get('source_file')}")
                print(f"   页码: {ref.get('page_num')}")
                print(f"   块索引: {ref.get('chunk_index')}")
                print(f"   坐标: {ref.get('bbox_union')}")
                
        else:
            print(f"❌ RAG查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    """主函数"""
    
    # 测试问题列表
    questions = [
        "安联美元基金总值",
        "安联美元基金的回报率是多少",
        "安联美元基金的风险等级",
        "安联美元基金的派息情况"
    ]
    
    for i, question in enumerate(questions):
        print(f"\n{'='*80}")
        print(f"测试 {i+1}/{len(questions)}")
        test_rag_query(question)
        print(f"{'='*80}")

if __name__ == "__main__":
    main()
