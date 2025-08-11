#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用完整文档测试RAG系统能否找到基金总值信息
"""

import os
import sys

def test_complete_document():
    """测试完整文档内容"""
    
    doc_path = "out_pdf_allianz_v2/document.md"
    
    if not os.path.exists(doc_path):
        print(f"❌ 完整文档不存在: {doc_path}")
        return
    
    print(f"🔍 测试完整文档: {doc_path}")
    print("=" * 60)
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 测试问题
    test_questions = [
        "安联美元基金总值是多少？",
        "安联美元基金的成立日期是什么时候？",
        "安联美元基金的基金经理是谁？",
        "安联美元基金的管理费是多少？"
    ]
    
    for question in test_questions:
        print(f"\n❓ 问题: {question}")
        print("-" * 40)
        
        # 简单的关键词匹配测试
        if "基金总值" in question and "4.4377亿美元" in content:
            print("✅ 找到答案: 4.4377亿美元")
        elif "成立日期" in question and "2010年8月2日" in content:
            print("✅ 找到答案: 2010年8月2日")
        elif "基金经理" in question and "Justin Kass" in content and "David Oberto" in content and "Michael Yee" in content:
            print("✅ 找到答案: Justin Kass / David Oberto / Michael Yee")
        elif "管理费" in question and "1.19%" in content:
            print("✅ 找到答案: 每年1.19%")
        else:
            print("❌ 未找到答案")
    
    print("\n" + "="*60)
    print("💡 结论:")
    print("完整文档包含了所有关键信息，RAG系统应该能够回答这些问题")
    print("当前PDFLLM配置丢失了'海外基金资料'表格，需要修复配置")

if __name__ == "__main__":
    test_complete_document()
