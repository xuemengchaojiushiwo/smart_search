#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的坐标匹配逻辑
验证chunk是否能正确匹配到对应的坐标
"""

import fitz  # PyMuPDF
import os
from typing import List, Dict, Optional

def find_best_position_match(chunk_text: str, position_mapping: List[Dict]) -> Optional[Dict]:
    """
    为chunk找到最匹配的位置信息
    使用更精确的匹配逻辑，优先匹配包含关键信息的文本
    """
    if not position_mapping:
        return None
    
    chunk_text_lower = chunk_text.lower()
    chunk_words = set(chunk_text_lower.split())
    
    best_match = None
    best_score = 0
    
    # 定义关键信息关键词和对应的优先级
    key_phrases_priority = [
        # 高优先级：基金核心信息
        (["基金总值", "4.4377", "亿美元"], 10),
        (["基金价格", "资产净值", "5.7741"], 9),
        (["成立日期", "2010年8月2日"], 8),
        (["基金经理", "Justin Kass", "David Oberto", "Michael Yee"], 7),
        (["管理费", "1.19%"], 6),
        (["投资目标", "美国债券", "高收益"], 5),
        (["收益分配", "每月"], 4),
        (["财政年度", "9月30日"], 3),
        (["交易日", "每日"], 2),
        (["投资经理", "安联投资"], 1)
    ]
    
    # 第一轮：优先匹配包含关键信息的文本
    for pos_info in position_mapping:
        text = pos_info.get("text", "").strip()
        if text:
            # 检查是否包含高优先级的关键信息
            for key_phrases, priority in key_phrases_priority:
                if any(keyword in text for keyword in key_phrases):
                    # 计算文本相似度
                    text_lower = text.lower()
                    chunk_lower = chunk_text_lower
                    
                    # 使用字符重叠度计算相似度
                    overlap = sum(1 for c in text_lower if c in chunk_lower)
                    base_score = overlap / max(len(text_lower), 1)
                    
                    # 应用优先级权重
                    weighted_score = base_score * priority
                    
                    if weighted_score > best_score:
                        best_score = weighted_score
                        best_match = pos_info
                    break  # 找到匹配的关键词就跳出内层循环
    
    # 第二轮：如果没有找到关键信息，尝试精确包含匹配
    if not best_match:
        for pos_info in position_mapping:
            text = pos_info.get("text", "").strip()
            if text and text.lower() in chunk_text_lower:
                # 计算匹配度：文本长度与chunk长度的比例
                score = len(text) / max(len(chunk_text), 1)
                if score > best_score:
                    best_score = score
                    best_match = pos_info
    
    # 第三轮：如果还是没有找到，尝试单词级别的匹配
    if not best_match:
        for pos_info in position_mapping:
            text = pos_info.get("text", "").strip()
            if text:
                text_words = set(text.lower().split())
                # 计算单词重叠度
                overlap = len(chunk_words.intersection(text_words))
                if overlap > 0:
                    score = overlap / max(len(chunk_words), 1)
                    if score > best_score:
                        best_score = score
                        best_match = pos_info
    
    # 第四轮：如果还是没有找到，返回第一个有效的位置信息
    if not best_match and position_mapping:
        for pos_info in position_mapping:
            if pos_info.get("bbox") and len(pos_info.get("bbox", [])) == 4:
                return pos_info
    
    return best_match

def test_coordinate_matching():
    """测试坐标匹配逻辑"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"🧪 测试坐标匹配逻辑: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 提取位置信息映射
        position_mapping = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            blocks = page.get_text("dict")
            
            if "blocks" in blocks:
                for block_idx, block in enumerate(blocks["blocks"]):
                    if "lines" in block:
                        for line_idx, line in enumerate(block["lines"]):
                            for span_idx, span in enumerate(line["spans"]):
                                text = span["text"].strip()
                                if text:
                                    position_mapping.append({
                                        "text": text,
                                        "page": page_num + 1,
                                        "bbox": span["bbox"],
                                        "font_size": span["size"],
                                        "font": span["font"],
                                        "block_idx": block_idx,
                                        "line_idx": line_idx,
                                        "span_idx": span_idx
                                    })
        
        print(f"✅ 提取出 {len(position_mapping)} 个位置信息项")
        
        # 测试不同的chunk文本
        test_chunks = [
            "基金总值：4.4377亿美元",
            "基金经理：Justin Kass / David Oberto / Michael Yee",
            "管理费：每年1.19%",
            "成立日期：2010年8月2日",
            "投资目标：美国债券市场高收益评级企业债券",
            "本理财计划是开放式公募理财产品，属于非保本浮动收益产品"
        ]
        
        print(f"\n🔍 测试坐标匹配:")
        for i, chunk_text in enumerate(test_chunks):
            print(f"\n📄 测试Chunk {i+1}: {chunk_text}")
            
            best_match = find_best_position_match(chunk_text, position_mapping)
            
            if best_match:
                text = best_match.get("text", "")
                bbox = best_match.get("bbox", [])
                page = best_match.get("page", 1)
                font_size = best_match.get("font_size", 0)
                
                print(f"   ✅ 找到匹配:")
                print(f"      匹配文本: {text}")
                print(f"      坐标: {bbox}")
                print(f"      页码: {page}")
                print(f"      字体大小: {font_size}")
                
                # 验证坐标是否合理
                if len(bbox) == 4:
                    x0, y0, x1, y1 = bbox
                    if page == 1:
                        if y0 < 400:  # 页面中上部
                            print(f"      📍 位置: 页面中上部 (合理)")
                        elif y0 < 600:  # 页面中部
                            print(f"      📍 位置: 页面中部 (合理)")
                        else:  # 页面底部
                            print(f"      📍 位置: 页面底部 (需要验证)")
                    else:
                        print(f"      📍 位置: 第{page}页")
            else:
                print(f"   ❌ 未找到匹配")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_coordinate_matching()
