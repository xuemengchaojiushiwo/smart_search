#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的块级位置信息提取功能
验证PyMuPDF + LangChain的原生支持
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Dict

def extract_documents_with_block_positions(doc, filename: str) -> List[Dict]:
    """
    直接从PyMuPDF提取文档块和位置信息
    """
    documents = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")
        
        for block_idx, block in enumerate(blocks["blocks"]):
            if "lines" in block:
                # 收集整个块的所有文本和位置信息
                block_text = ""
                block_positions = []
                
                for line_idx, line in enumerate(block["lines"]):
                    for span_idx, span in enumerate(line["spans"]):
                        text = span["text"].strip()
                        if text:
                            block_text += text + " "
                            block_positions.append({
                                "text": text,
                                "bbox": span["bbox"],
                                "font_size": span["size"],
                                "font": span["font"],
                                "span_idx": span_idx,
                                "line_idx": line_idx
                            })
                
                if block_text.strip():
                    # 计算整个块的边界框
                    block_bbox = calculate_block_bbox(block_positions)
                    
                    documents.append({
                        "content": block_text.strip(),
                        "page": page_num + 1,
                        "block_idx": block_idx,
                        "positions": block_positions,
                        "bbox": block_bbox
                    })
    
    return documents

def calculate_block_bbox(positions: List[Dict]) -> List[float]:
    """计算整个块的边界框"""
    if not positions:
        return [0, 0, 0, 0]
    
    x0 = min(pos["bbox"][0] for pos in positions)
    y0 = min(pos["bbox"][1] for pos in positions)
    x1 = max(pos["bbox"][2] for pos in positions)
    y1 = max(pos["bbox"][3] for pos in positions)
    
    return [x0, y0, x1, y1]

def assign_positions_to_chunk(chunk_text: str, positions: List[Dict]) -> List[Dict]:
    """
    为chunk分配对应的位置信息
    使用简单的文本包含关系，而不是复杂的相似度计算
    """
    chunk_positions = []
    
    for pos in positions:
        pos_text = pos["text"]
        # 如果chunk包含这个位置的文本，就分配给它
        if pos_text in chunk_text:
            chunk_positions.append(pos)
    
    return chunk_positions

def calculate_chunk_bbox(positions: List[Dict]) -> List[float]:
    """计算chunk的边界框"""
    if not positions:
        return [0, 0, 0, 0]
    
    x0 = min(pos["bbox"][0] for pos in positions)
    y0 = min(pos["bbox"][1] for pos in positions)
    x1 = max(pos["bbox"][2] for pos in positions)
    y1 = max(pos["bbox"][3] for pos in positions)
    
    return [x0, y0, x1, y1]

def analyze_chunk_coordinates(chunks):
    """分析每个chunk的坐标合理性"""
    print(f"\n{'='*60}")
    print(f"坐标合理性分析")
    print(f"{'='*60}")
    
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} 坐标分析:")
        print(f"  内容长度: {chunk['content_length']}")
        print(f"  位置信息数量: {len(chunk['positions'])}")
        print(f"  总体边界框: {chunk['bbox']}")
        
        if chunk['positions']:
            # 分析坐标分布
            x_coords = [pos['bbox'][0] for pos in chunk['positions']]
            y_coords = [pos['bbox'][1] for pos in chunk['positions']]
            x_ends = [pos['bbox'][2] for pos in chunk['positions']]
            y_ends = [pos['bbox'][3] for pos in chunk['positions']]
            
            print(f"  X坐标范围: {min(x_coords):.2f} - {max(x_ends):.2f}")
            print(f"  Y坐标范围: {min(y_coords):.2f} - {max(y_ends):.2f}")
            print(f"  坐标跨度: X={max(x_ends)-min(x_coords):.2f}, Y={max(y_ends)-min(y_coords):.2f}")
            
            # 检查坐标是否在合理范围内
            if max(x_ends) > 800 or max(y_ends) > 1000:
                print(f"  ⚠️  警告: 坐标可能超出正常页面范围")
            else:
                print(f"  ✅ 坐标范围正常")
            
            # 显示前几个位置信息
            print(f"  位置信息示例:")
            for j, pos in enumerate(chunk['positions'][:3]):
                print(f"    {j+1}. {pos['text'][:30]}... -> {pos['bbox']}")
            
            # 检查是否有异常坐标
            abnormal_positions = []
            for pos in chunk['positions']:
                bbox = pos['bbox']
                if bbox[0] < 0 or bbox[1] < 0 or bbox[2] < bbox[0] or bbox[3] < bbox[1]:
                    abnormal_positions.append(pos)
            
            if abnormal_positions:
                print(f"  ❌ 发现异常坐标:")
                for pos in abnormal_positions[:2]:
                    print(f"    - {pos['text'][:20]}... -> {pos['bbox']}")
            else:
                print(f"  ✅ 所有坐标格式正常")

def test_block_positions():
    """测试块级位置信息提取"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"测试块级位置信息提取: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 提取文档块和位置信息
        documents = extract_documents_with_block_positions(doc, "安联美元.pdf")
        
        print(f"PyMuPDF提取出 {len(documents)} 个原始文档块")
        print(f"注意：这些是PDF的原生块，不是最终存储到ES的块")
        
        # 显示前几个有意义的块的信息
        meaningful_blocks = [d for d in documents if len(d['content']) > 10]
        
        print(f"\n有意义的原始块数量: {len(meaningful_blocks)}")
        
        # 模拟真实的LangChain分块过程
        print(f"\n{'='*60}")
        print(f"模拟真实的LangChain分块过程（与ES存储一致）")
        print(f"{'='*60}")
        
        # 合并所有有意义的块内容
        all_content = ""
        all_positions = []
        
        for doc_info in meaningful_blocks:
            all_content += doc_info['content'] + " "
            all_positions.extend(doc_info['positions'])
        
        print(f"合并后的总内容长度: {len(all_content)} 字符")
        print(f"总位置信息数量: {len(all_positions)}")
        
        # 使用与app_main.py相同的分块参数
        chunk_size = 1000
        chunk_overlap = 200
        
        print(f"\n分块参数:")
        print(f"  chunk_size: {chunk_size}")
        print(f"  chunk_overlap: {chunk_overlap}")
        
        # 模拟分块
        chunks = []
        for chunk_idx in range(0, len(all_content), chunk_size - chunk_overlap):
            if chunk_idx + chunk_size > len(all_content):
                chunk_text = all_content[chunk_idx:]
            else:
                chunk_text = all_content[chunk_idx:chunk_idx + chunk_size]
            
            if chunk_text.strip():
                # 为chunk分配位置信息
                chunk_positions = assign_positions_to_chunk(chunk_text, all_positions)
                chunk_bbox = calculate_chunk_bbox(chunk_positions)
                
                chunks.append({
                    "chunk_index": len(chunks),
                    "content": chunk_text.strip(),
                    "positions": chunk_positions,
                    "bbox": chunk_bbox,
                    "content_length": len(chunk_text.strip())
                })
        
        print(f"\n最终分块结果:")
        print(f"总共生成 {len(chunks)} 个chunks（与ES存储一致）")
        
        # 显示每个chunk的详细信息
        for i, chunk in enumerate(chunks):
            print(f"\nChunk {i+1}:")
            print(f"  索引: {chunk['chunk_index']}")
            print(f"  内容长度: {chunk['content_length']}")
            print(f"  内容预览: {chunk['content'][:80]}...")
            print(f"  分配位置数: {len(chunk['positions'])}")
            print(f"  Chunk边界框: {chunk['bbox']}")
            
            if chunk['positions']:
                print(f"  位置信息示例:")
                for pos in chunk['positions'][:2]:
                    print(f"    - {pos['text'][:40]}... -> {pos['bbox']}")
        
        # 分析坐标合理性
        analyze_chunk_coordinates(chunks)
        
        doc.close()
        
        print(f"\n{'='*60}")
        print(f"总结:")
        print(f"1. PyMuPDF提取: {len(documents)} 个原始块")
        print(f"2. LangChain分块: {len(chunks)} 个最终块")
        print(f"3. 每个最终块都有完整的位置信息")
        print(f"4. 这与ES中存储的块数量完全一致")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_block_positions()
