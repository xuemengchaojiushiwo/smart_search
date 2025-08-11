#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
比较不同格式的PDF解析结果，评估AI理解能力
"""

import os
import re
from typing import Dict, List, Tuple

def analyze_text_structure(text: str, format_name: str) -> Dict:
    """分析文本结构特征"""
    analysis = {
        "format": format_name,
        "total_length": len(text),
        "lines": len(text.split('\n')),
        "tables": 0,
        "headers": 0,
        "position_tags": 0,
        "key_phrases": {},
        "structure_score": 0
    }
    
    # 统计表格数量
    table_patterns = [
        r'\|.*\|',  # Markdown表格
        r'```\n\|.*\|',  # 代码块中的表格
        r'<pos.*?>.*?</pos>',  # 位置标签
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
        "彭博代码"
    ]
    
    for phrase in key_phrases:
        count = text.count(phrase)
        analysis["key_phrases"][phrase] = count
    
    # 计算结构评分
    analysis["structure_score"] = (
        analysis["tables"] * 10 +  # 表格权重高
        analysis["headers"] * 5 +   # 标题权重中等
        analysis["position_tags"] * 2 +  # 位置信息权重较低
        len([v for v in analysis["key_phrases"].values() if v > 0]) * 3  # 关键信息权重
    )
    
    return analysis

def extract_sample_content(text: str, format_name: str, max_lines: int = 20) -> str:
    """提取样本内容用于展示"""
    lines = text.split('\n')
    sample_lines = lines[:max_lines]
    
    sample = f"\n=== {format_name} 样本内容 ===\n"
    sample += "\n".join(sample_lines)
    
    if len(lines) > max_lines:
        sample += f"\n... (还有 {len(lines) - max_lines} 行)"
    
    return sample

def compare_formats():
    """比较不同格式的解析结果"""
    
    # 文件路径
    files = {
        "PyMuPDF原始输出": "pymupdf_extraction_result.txt",
        "结构化Markdown": "python_service/file/安联美元_converted.md", 
        "带位置信息Markdown": "python_service/file/安联美元_with_positions.md"
    }
    
    results = {}
    samples = {}
    
    print("🔍 正在分析不同格式的PDF解析结果...\n")
    
    for format_name, file_path in files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析结构
                analysis = analyze_text_structure(content, format_name)
                results[format_name] = analysis
                
                # 提取样本
                samples[format_name] = extract_sample_content(content, format_name)
                
                print(f"✅ {format_name}: 分析完成")
                
            except Exception as e:
                print(f"❌ {format_name}: 分析失败 - {e}")
        else:
            print(f"⚠️  {format_name}: 文件不存在 - {file_path}")
    
    print("\n" + "="*80)
    print("📊 格式对比分析结果")
    print("="*80)
    
    # 按结构评分排序
    sorted_results = sorted(results.items(), key=lambda x: x[1]["structure_score"], reverse=True)
    
    for i, (format_name, analysis) in enumerate(sorted_results, 1):
        print(f"\n🏆 第{i}名: {format_name}")
        print(f"   结构评分: {analysis['structure_score']}")
        print(f"   总长度: {analysis['total_length']:,} 字符")
        print(f"   行数: {analysis['lines']:,}")
        print(f"   表格: {analysis['tables']}")
        print(f"   标题: {analysis['headers']}")
        print(f"   位置标签: {analysis['position_tags']}")
        
        print(f"   关键短语覆盖:")
        for phrase, count in analysis["key_phrases"].items():
            status = "✅" if count > 0 else "❌"
            print(f"     {status} {phrase}: {count}")
    
    print("\n" + "="*80)
    print("📝 各格式样本内容")
    print("="*80)
    
    for format_name, sample in samples.items():
        print(sample)
        print("\n" + "-"*60 + "\n")
    
    # 推荐分析
    print("="*80)
    print("💡 AI理解能力评估与推荐")
    print("="*80)
    
    best_format = sorted_results[0][0]
    print(f"🎯 推荐格式: {best_format}")
    
    if "结构化Markdown" in best_format:
        print("   优势:")
        print("   - 保持了表格结构，AI更容易理解数据关系")
        print("   - 标题层次清晰，便于理解文档结构")
        print("   - 去除了冗余的位置信息，文本更清洁")
        print("   - 适合语义搜索和问答")
        
    elif "带位置信息Markdown" in best_format:
        print("   优势:")
        print("   - 保留了完整的位置信息，便于高亮显示")
        print("   - 字体和大小信息完整")
        print("   - 适合需要精确定位的应用场景")
        print("   - 但位置标签可能影响AI理解")
        
    elif "PyMuPDF原始输出" in best_format:
        print("   优势:")
        print("   - 原始文本信息完整")
        print("   - 但缺乏结构化信息")
        print("   - 表格结构不清晰")
        print("   - AI理解难度较高")
    
    print("\n🔧 建议:")
    print("1. 对于RAG问答系统，推荐使用结构化Markdown")
    print("2. 对于需要精确定位的应用，可以结合两种格式")
    print("3. 可以考虑在结构化Markdown中添加关键位置信息")

if __name__ == "__main__":
    compare_formats()
