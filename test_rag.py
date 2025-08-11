#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试RAG功能
验证智能问答和位置信息返回
"""

import requests
import json

def test_rag_chat():
    """测试RAG聊天功能"""
    print("🧪 开始测试RAG功能...")
    
    # 测试问题列表
    test_questions = [
        "安联美元基金的总值是多少？",
        "这个基金的投资目标是什么？",
        "基金经理是谁？",
        "管理费是多少？",
        "基金成立日期是什么时候？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🔍 测试问题 {i}: {question}")
        
        try:
            # 调用RAG API
            response = requests.post(
                "http://localhost:8000/api/rag/chat",
                json={
                    "question": question,
                    "user_id": "test_user"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 回答: {result.get('answer', 'N/A')}")
                
                # 显示引用信息
                references = result.get('references', [])
                if references:
                    print(f"📚 引用来源 ({len(references)} 个):")
                    for j, ref in enumerate(references[:3], 1):  # 只显示前3个
                        print(f"  {j}. 文件: {ref.get('source_file', 'N/A')}")
                        print(f"     页码: {ref.get('page_num', 'N/A')}")
                        print(f"     块序: {ref.get('chunk_index', 'N/A')}")
                        print(f"     相关性: {ref.get('relevance', 'N/A'):.3f}")
                        if ref.get('bbox_union'):
                            print(f"     坐标: {ref.get('bbox_union', [])}")
                else:
                    print("❌ 没有找到相关引用")
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
    
    print("\n🎯 RAG功能测试完成！")

def test_specific_question():
    """测试特定问题：基金总值"""
    print("\n🎯 专门测试基金总值问题...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/rag/chat",
            json={
                "question": "安联美元基金的总值是多少？请告诉我具体的数值。",
                "user_id": "test_user"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 回答: {result.get('answer', 'N/A')}")
            
            # 详细分析引用
            references = result.get('references', [])
            if references:
                print(f"\n📊 引用分析:")
                for i, ref in enumerate(references, 1):
                    print(f"\n引用 {i}:")
                    print(f"  文件: {ref.get('source_file', 'N/A')}")
                    print(f"  页码: {ref.get('page_num', 'N/A')}")
                    print(f"  块序: {ref.get('chunk_index', 'N/A')}")
                    print(f"  相关性: {ref.get('relevance', 'N/A'):.3f}")
                    print(f"  坐标: {ref.get('bbox_union', [])}")
                    print(f"  字符范围: {ref.get('char_start', 'N/A')} - {ref.get('char_end', 'N/A')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   响应: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    print("🚀 启动RAG功能测试")
    print("=" * 50)
    
    # 测试基本RAG功能
    test_rag_chat()
    
    # 测试特定问题
    test_specific_question()
    
    print("\n🎉 所有测试完成！")
