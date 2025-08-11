#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
改进的搜索策略
处理多文档场景下的精确匹配问题
"""

import re
from typing import List, Dict, Optional

def extract_fund_names_from_question(question: str) -> List[str]:
    """
    从问题中提取基金名称
    """
    # 常见的基金名称模式
    fund_patterns = [
        r'([^，。！？\s]+基金)',  # 匹配"XX基金"
        r'([^，。！？\s]+美元)',  # 匹配"XX美元"
        r'([^，。！？\s]+债券)',  # 匹配"XX债券"
        r'([^，。！？\s]+股票)',  # 匹配"XX股票"
    ]
    
    fund_names = []
    for pattern in fund_patterns:
        matches = re.findall(pattern, question)
        fund_names.extend(matches)
    
    # 去重并过滤
    fund_names = list(set(fund_names))
    fund_names = [name for name in fund_names if len(name) > 2]  # 过滤太短的
    
    return fund_names

def classify_question_type(question: str) -> str:
    """
    分类问题类型
    """
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['总值', '规模', '资产', '金额']):
        return "fund_size"
    elif any(word in question_lower for word in ['投资目标', '目标', '策略']):
        return "investment_objective"
    elif any(word in question_lower for word in ['基金经理', '经理', '管理人']):
        return "fund_manager"
    elif any(word in question_lower for word in ['管理费', '费用', '费率']):
        return "management_fee"
    elif any(word in question_lower for word in ['成立日期', '成立', '成立时间']):
        return "establishment_date"
    elif any(word in question_lower for word in ['收益率', '回报', '收益']):
        return "performance"
    else:
        return "general"

def enhanced_chunk_filtering(question: str, chunks: List[Dict]) -> List[Dict]:
    """
    增强的chunk过滤策略
    """
    # 1. 提取问题中的关键信息
    fund_names = extract_fund_names_from_question(question)
    question_type = classify_question_type(question)
    
    print(f"🔍 问题分析:")
    print(f"   基金名称: {fund_names}")
    print(f"   问题类型: {question_type}")
    
    # 2. 如果没有明确指定基金名称，返回所有chunks
    if not fund_names:
        print("   未检测到具体基金名称，返回所有chunks")
        return chunks
    
    # 3. 按基金名称过滤chunks
    filtered_chunks = []
    for chunk in chunks:
        chunk_content = chunk.get('content', '').lower()
        chunk_metadata = chunk.get('metadata', {})
        
        # 检查chunk内容或元数据中是否包含基金名称
        is_relevant = False
        
        # 方法1: 检查chunk内容
        for fund_name in fund_names:
            if fund_name.lower() in chunk_content:
                is_relevant = True
                break
        
        # 方法2: 检查元数据中的基金名称
        if not is_relevant:
            chunk_fund_name = chunk_metadata.get('fund_name', '')
            if chunk_fund_name and any(fund_name.lower() in chunk_fund_name.lower() for fund_name in fund_names):
                is_relevant = True
        
        # 方法3: 检查文件名（作为备选方案）
        if not is_relevant:
            source_file = chunk_metadata.get('source_file', '')
            if source_file and any(fund_name.lower() in source_file.lower() for fund_name in fund_names):
                is_relevant = True
        
        if is_relevant:
            filtered_chunks.append(chunk)
    
    print(f"   过滤前chunks数量: {len(chunks)}")
    print(f"   过滤后chunks数量: {len(filtered_chunks)}")
    
    # 4. 如果过滤后chunks太少，放宽条件
    if len(filtered_chunks) < 3:
        print("   ⚠️ 过滤后chunks太少，放宽过滤条件")
        # 使用更宽松的匹配：只要包含部分关键词即可
        for chunk in chunks:
            if chunk not in filtered_chunks:
                chunk_content = chunk.get('content', '').lower()
                # 检查是否包含基金名称的部分关键词
                for fund_name in fund_names:
                    fund_keywords = fund_name.lower().split()
                    if any(keyword in chunk_content for keyword in fund_keywords if len(keyword) > 1):
                        filtered_chunks.append(chunk)
                        break
    
    print(f"   最终chunks数量: {len(filtered_chunks)}")
    return filtered_chunks

def smart_search_strategy(question: str, all_chunks: List[Dict]) -> List[Dict]:
    """
    智能搜索策略
    """
    print(f"\n🧠 智能搜索策略启动")
    print(f"问题: {question}")
    
    # 1. 增强过滤
    filtered_chunks = enhanced_chunk_filtering(question, all_chunks)
    
    # 2. 如果过滤后chunks仍然太少，返回所有chunks
    if len(filtered_chunks) < 2:
        print("   ⚠️ 过滤后chunks仍然太少，返回所有chunks")
        return all_chunks
    
    return filtered_chunks

# 使用示例
if __name__ == "__main__":
    # 模拟chunks数据
    sample_chunks = [
        {
            "content": "安联美元高收益基金的总值为4.4377亿美元",
            "metadata": {
                "source_file": "安联美元.pdf",
                "fund_name": "安联美元高收益基金",
                "page_num": 1
            }
        },
        {
            "content": "华夏成长基金的投资目标是追求长期资本增值",
            "metadata": {
                "source_file": "华夏成长.pdf",
            "fund_name": "华夏成长基金",
                "page_num": 1
            }
        },
        {
            "content": "安联美元基金的基金经理是Justin Kass",
            "metadata": {
                "source_file": "安联美元.pdf",
                "fund_name": "安联美元高收益基金",
                "page_num": 1
            }
        }
    ]
    
    # 测试不同问题
    test_questions = [
        "安联美元基金的总值是多少？",
        "华夏成长基金的投资目标是什么？",
        "基金经理是谁？",  # 没有指定具体基金
        "基金的总值是多少？"  # 没有指定具体基金
    ]
    
    for question in test_questions:
        print(f"\n{'='*50}")
        result_chunks = smart_search_strategy(question, sample_chunks)
        print(f"搜索结果: {len(result_chunks)} 个chunks")
        for i, chunk in enumerate(result_chunks[:2]):  # 只显示前2个
            print(f"  {i+1}. {chunk['content'][:50]}...")
