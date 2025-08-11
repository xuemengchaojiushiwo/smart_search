#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用完整的文档内容，验证RAG系统能否找到基金总值信息
"""

import os
import sys

def analyze_complete_document():
    """分析完整文档内容"""
    
    doc_path = "out_pdf_allianz_v2/document.md"
    
    if not os.path.exists(doc_path):
        print(f"❌ 完整文档不存在: {doc_path}")
        return
    
    print(f"🔍 分析完整文档: {doc_path}")
    print("=" * 60)
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📊 文档总长度: {len(content)}")
    
    # 检查关键信息
    key_phrases = [
        "海外基金资料",
        "基金总值",
        "4.4377亿美元",
        "基金价格",
        "5.7741美元",
        "成立日期",
        "2010年8月2日",
        "基金经理",
        "Justin Kass",
        "David Oberto",
        "Michael Yee",
        "管理费",
        "1.19%",
        "财政年度终结日",
        "9月30日",
        "收益分配方式",
        "每月",
        "投资经理",
        "安联投资"
    ]
    
    print("\n🔍 检查关键信息:")
    found_count = 0
    for phrase in key_phrases:
        if phrase in content:
            print(f"✅ 找到: {phrase}")
            found_count += 1
        else:
            print(f"❌ 未找到: {phrase}")
    
    print(f"\n📈 关键信息覆盖率: {found_count}/{len(key_phrases)} ({found_count/len(key_phrases)*100:.1f}%)")
    
    # 查找基金总值相关信息
    print("\n💰 基金总值相关信息:")
    if "基金总值" in content:
        # 找到基金总值行
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if "基金总值" in line:
                print(f"  行 {i+1}: {line.strip()}")
                # 显示上下文
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print("  上下文:")
                for j in range(start, end):
                    marker = ">>> " if j == i else "    "
                    print(f"  {marker}{j+1}: {lines[j].strip()}")
                break
    
    # 查找表格结构
    print(f"\n📋 表格结构分析:")
    table_lines = [line for line in content.split('\n') if '|' in line and line.strip()]
    print(f"  表格行数: {len(table_lines)}")
    
    if table_lines:
        print("  表格内容预览:")
        for i, line in enumerate(table_lines[:15]):  # 显示前15行
            print(f"    {i+1}: {line}")

def main():
    """主函数"""
    analyze_complete_document()
    
    print("\n" + "="*60)
    print("💡 建议:")
    print("1. 使用 out_pdf_allianz_v2/document.md 作为数据源")
    print("2. 重新配置PDFLLM参数，确保能提取完整内容")
    print("3. 或者直接使用现有完整文档进行RAG测试")

if __name__ == "__main__":
    main()
