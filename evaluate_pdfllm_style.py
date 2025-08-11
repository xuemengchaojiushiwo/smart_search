#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估PDFLLM风格格式的效果
"""

import os
import re
from typing import Dict, List, Tuple

def analyze_pdfllm_style(text: str, format_name: str) -> Dict:
    """分析PDFLLM风格格式的质量"""
    analysis = {
        "format": format_name,
        "total_length": len(text),
        "lines": len(text.split('\n')),
        "position_tags": 0,
        "key_phrases": {},
        "structure_score": 0,
        "position_quality": 0,
        "ai_readability": 0
    }
    
    # 统计位置标签数量
    pos_patterns = [
        r'<sub>pos: page=\d+, bbox=\([^)]+\)</sub>',  # PDFLLM风格
        r'<pos page=\d+ bbox=[^>]+>.*?</pos>',  # 紧凑格式
    ]
    
    for pattern in pos_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        analysis["position_tags"] += len(matches)
    
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
        len([v for v in analysis["key_phrases"].values() if v > 0]) * 10 +  # 关键信息权重
        (analysis["total_length"] / 1000) * 5  # 内容完整性权重
    )
    
    # 位置质量评分
    if analysis["position_tags"] > 0:
        analysis["position_quality"] = min(100, analysis["position_tags"] / 5)
    else:
        analysis["position_quality"] = 0
    
    # AI可读性评分
    analysis["ai_readability"] = (
        analysis["structure_score"] * 0.7 +  # 结构权重
        analysis["position_quality"] * 0.3   # 位置信息权重
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

def evaluate_pdfllm_styles():
    """评估PDFLLM风格格式"""
    
    # 文件路径
    files = {
        "PDFLLM风格": "python_service/file/安联美元_pdfllm_style.md",
        "紧凑位置格式": "python_service/file/安联美元_compact_pos.md",
        "表格感知格式": "python_service/file/安联美元_table_aware.md",
        "清洁Markdown": "python_service/file/安联美元_clean.md",
        "带位置信息Markdown": "python_service/file/安联美元_with_positions.md"
    }
    
    results = {}
    samples = {}
    
    print("🔍 正在评估PDFLLM风格格式...\n")
    
    for format_name, file_path in files.items():
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 分析质量
                analysis = analyze_pdfllm_style(content, format_name)
                results[format_name] = analysis
                
                # 提取样本
                samples[format_name] = extract_sample_content(content, format_name)
                
                print(f"✅ {format_name}: 评估完成")
                
            except Exception as e:
                print(f"❌ {format_name}: 评估失败 - {e}")
        else:
            print(f"⚠️  {format_name}: 文件不存在 - {file_path}")
    
    print("\n" + "="*100)
    print("📊 PDFLLM风格格式评估结果")
    print("="*100)
    
    # 按AI可读性评分排序
    sorted_by_ai = sorted(results.items(), key=lambda x: x[1]["ai_readability"], reverse=True)
    
    print("\n🏆 AI可读性排名:")
    for i, (format_name, analysis) in enumerate(sorted_by_ai, 1):
        print(f"\n第{i}名: {format_name}")
        print(f"   AI可读性评分: {analysis['ai_readability']:.1f}")
        print(f"   结构评分: {analysis['structure_score']:.1f}")
        print(f"   位置质量: {analysis['position_quality']:.1f}")
        print(f"   总长度: {analysis['total_length']:,} 字符")
        print(f"   行数: {analysis['lines']:,}")
        print(f"   位置标签: {analysis['position_tags']}")
        
        print(f"   关键短语覆盖:")
        for phrase, count in analysis["key_phrases"].items():
            status = "✅" if count > 0 else "❌"
            print(f"     {status} {phrase}: {count}")
    
    # 按位置质量排序
    sorted_by_position = sorted(results.items(), key=lambda x: x[1]["position_quality"], reverse=True)
    
    print("\n🎯 位置信息质量排名:")
    for i, (format_name, analysis) in enumerate(sorted_by_position, 1):
        print(f"\n第{i}名: {format_name}")
        print(f"   位置质量: {analysis['position_quality']:.1f}")
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
        
        if "PDFLLM风格" in format_name:
            print("   ✅ 优势: 格式最接近pdfllm_document_with_pos.md")
            print("   ✅ 适用: 需要兼容现有PDFLLM处理流程")
            print("   ✅ 特点: 位置信息清晰，格式规范")
            
        elif "紧凑位置格式" in format_name:
            print("   ✅ 优势: 位置信息紧凑，减少冗余")
            print("   ✅ 适用: 需要位置信息但希望文件较小")
            print("   ✅ 特点: 标签格式简洁")
            
        elif "表格感知格式" in format_name:
            print("   ✅ 优势: 保持表格结构，AI理解最佳")
            print("   ✅ 适用: 包含大量表格的文档")
            print("   ✅ 特点: 表格结构清晰，位置信息完整")
            
        elif "清洁Markdown" in format_name:
            print("   ✅ 优势: 无位置标签干扰，AI理解最佳")
            print("   ✅ 适用: 主要RAG问答系统")
            print("   ⚠️  劣势: 缺乏位置信息")
            
        elif "带位置信息" in format_name:
            print("   ✅ 优势: 位置信息最完整")
            print("   ✅ 适用: 需要精确定位的应用")
            print("   ⚠️  劣势: 位置标签过多，影响AI理解")
    
    print("\n🚀 推荐使用策略:")
    print("1. 主要RAG问答: 使用表格感知格式或清洁Markdown")
    print("2. 需要兼容PDFLLM: 使用PDFLLM风格格式")
    print("3. 需要位置信息: 使用紧凑位置格式")
    print("4. 精确定位应用: 使用带位置信息Markdown")
    
    print("\n" + "="*100)
    print("📝 各格式样本内容对比")
    print("="*100)
    
    for format_name, sample in samples.items():
        print(sample)
        print("\n" + "-"*80 + "\n")

if __name__ == "__main__":
    evaluate_pdfllm_styles()
