#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终格式评估：比较所有PDF解析格式并给出最佳推荐
"""

import os
import re
from typing import Dict, List, Tuple

def analyze_format_quality(text: str, format_name: str) -> Dict:
    """分析格式质量"""
    analysis = {
        "format": format_name,
        "total_length": len(text),
        "lines": len(text.split('\n')),
        "tables": 0,
        "headers": 0,
        "position_tags": 0,
        "key_phrases": {},
        "structure_score": 0,
        "ai_readability": 0,
        "position_accuracy": 0
    }
    
    # 统计表格数量
    table_patterns = [
        r'\|.*\|',  # Markdown表格
        r'```\n\|.*\|',  # 代码块中的表格
    ]
    
    for pattern in table_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        analysis["tables"] += len(matches)
    
    # 统计标题数量
    header_patterns = [
        r'^#{1,3}\s+.*$',  # Markdown标题
        r'^###\s+.*$',  # 三级标题
    ]
    
    for pattern in header_patterns:
        matches = re.findall(pattern, text, re.MULTILINE)
        analysis["headers"] += len(matches)
    
    # 统计位置标签数量
    pos_tags = re.findall(r'<pos.*?>.*?</pos>', text)
    analysis["position_tags"] = len(pos_tags)
    
    # 检查关键短语
    key_phrases = [
        "基金总值",
        "海外基金资料", 
        "投资目标",
        "管理费",
        "风险水平",
        "股份类别",
        "ISIN",
        "彭博代码",
        "成立日期",
        "基金经理",
        "收益分配"
    ]
    
    for phrase in key_phrases:
        count = text.count(phrase)
        analysis["key_phrases"][phrase] = count
    
    # 计算结构评分
    analysis["structure_score"] = (
        analysis["tables"] * 10 +  # 表格权重高
        analysis["headers"] * 5 +   # 标题权重中等
        len([v for v in analysis["key_phrases"].values() if v > 0]) * 3  # 关键信息权重
    )
    
    # AI可读性评分
    analysis["ai_readability"] = (
        analysis["structure_score"] * 0.6 +  # 结构权重
        (analysis["total_length"] / 1000) * 0.2 +  # 内容完整性权重
        (1 / (1 + analysis["position_tags"] / 100)) * 100 * 0.2  # 位置标签越少越好
    )
    
    # 位置准确性评分
    if analysis["position_tags"] > 0:
        analysis["position_accuracy"] = min(100, analysis["position_tags"] / 10)
    else:
        analysis["position_accuracy"] = 0
    
    return analysis

def extract_sample_content(text: str, format_name: str, max_lines: int = 15) -> str:
    """提取样本内容用于展示"""
    lines = text.split('\n')
    sample_lines = lines[:max_lines]
    
    sample = f"\n=== {format_name} 样本内容 ===\n"
    sample += "\n".join(sample_lines)
    
    if len(lines) > max_lines:
        sample += f"\n... (还有 {len(lines) - max_lines} 行)"
    
    return sample

def evaluate_all_formats():
    """评估所有格式"""
    
    # 文件路径
    files = {
        "PyMuPDF原始输出": "pymupdf_extraction_result.txt",
        "结构化Markdown": "python_service/file/安联美元_converted.md", 
        "带位置信息Markdown": "python_service/file/安联美元_with_positions.md",
        "混合格式Markdown": "python_service/file/安联美元_hybrid.md",
        "清洁Markdown": "python_service/file/安联美元_clean.md"
    }
    
    results = {}
    samples = {}
    
    print("🔍 正在评估所有PDF解析格式...\n")
    
    for format_name, file_path in files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析质量
                analysis = analyze_format_quality(content, format_name)
                results[format_name] = analysis
                
                # 提取样本
                samples[format_name] = extract_sample_content(content, format_name)
                
                print(f"✅ {format_name}: 评估完成")
                
            except Exception as e:
                print(f"❌ {format_name}: 评估失败 - {e}")
        else:
            print(f"⚠️  {format_name}: 文件不存在 - {file_path}")
    
    print("\n" + "="*100)
    print("📊 所有格式质量评估结果")
    print("="*100)
    
    # 按AI可读性评分排序
    sorted_by_ai = sorted(results.items(), key=lambda x: x[1]["ai_readability"], reverse=True)
    
    print("\n🏆 AI可读性排名:")
    for i, (format_name, analysis) in enumerate(sorted_by_ai, 1):
        print(f"\n第{i}名: {format_name}")
        print(f"   AI可读性评分: {analysis['ai_readability']:.1f}")
        print(f"   结构评分: {analysis['structure_score']}")
        print(f"   总长度: {analysis['total_length']:,} 字符")
        print(f"   行数: {analysis['lines']:,}")
        print(f"   表格: {analysis['tables']}")
        print(f"   标题: {analysis['headers']}")
        print(f"   位置标签: {analysis['position_tags']}")
        print(f"   位置准确性: {analysis['position_accuracy']:.1f}")
    
    # 按位置准确性排序
    sorted_by_position = sorted(results.items(), key=lambda x: x[1]["position_accuracy"], reverse=True)
    
    print("\n🎯 位置准确性排名:")
    for i, (format_name, analysis) in enumerate(sorted_by_position, 1):
        print(f"\n第{i}名: {format_name}")
        print(f"   位置准确性: {analysis['position_accuracy']:.1f}")
        print(f"   位置标签数量: {analysis['position_tags']}")
    
    print("\n" + "="*100)
    print("💡 最终推荐与使用建议")
    print("="*100)
    
    best_ai_format = sorted_by_ai[0][0]
    best_position_format = sorted_by_position[0][0]
    
    print(f"🎯 最佳AI理解格式: {best_ai_format}")
    print(f"🎯 最佳位置信息格式: {best_position_format}")
    
    print("\n📋 各格式特点分析:")
    
    for format_name, analysis in results.items():
        print(f"\n🔸 {format_name}:")
        
        if "清洁" in format_name:
            print("   ✅ 优势: 结构清晰，无位置标签干扰，AI理解最佳")
            print("   ✅ 适用: RAG问答系统，语义搜索")
            print("   ⚠️  劣势: 缺乏位置信息")
            
        elif "混合" in format_name:
            print("   ✅ 优势: 平衡了结构和位置信息")
            print("   ✅ 适用: 需要定位的RAG系统")
            print("   ⚠️  劣势: 位置标签可能影响AI理解")
            
        elif "带位置信息" in format_name:
            print("   ✅ 优势: 位置信息最完整")
            print("   ✅ 适用: 需要精确定位的应用")
            print("   ⚠️  劣势: 位置标签过多，影响AI理解")
            
        elif "结构化" in format_name:
            print("   ✅ 优势: 结构清晰，表格识别好")
            print("   ✅ 适用: 结构化文档处理")
            print("   ⚠️  劣势: 位置信息不足")
            
        elif "PyMuPDF原始" in format_name:
            print("   ✅ 优势: 原始信息完整")
            print("   ✅ 适用: 需要原始数据的场景")
            print("   ⚠️  劣势: 结构混乱，AI理解困难")
    
    print("\n🚀 推荐使用策略:")
    print("1. 主要RAG问答: 使用清洁Markdown格式")
    print("2. 需要定位的RAG: 使用混合格式Markdown")
    print("3. 精确定位应用: 使用带位置信息Markdown")
    print("4. 可以考虑在ES中存储两种格式，根据需求选择")
    
    print("\n" + "="*100)
    print("📝 各格式样本内容对比")
    print("="*100)
    
    for format_name, sample in samples.items():
        print(sample)
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    evaluate_all_formats()
