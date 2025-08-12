#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化chunks的边界框
在PDF上绘制每个chunk的边界框并保存图片
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List, Dict
import colorsys

def extract_documents_with_block_positions(doc, filename: str) -> List[Dict]:
    """直接从PyMuPDF提取文档块和位置信息"""
    documents = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")
        
        for block_idx, block in enumerate(blocks["blocks"]):
            if "lines" in block:
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
    """为chunk分配对应的位置信息"""
    chunk_positions = []
    
    for pos in positions:
        pos_text = pos["text"]
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

def generate_chunk_colors(num_chunks: int) -> List[tuple]:
    """为每个chunk生成不同的颜色"""
    colors = []
    for i in range(num_chunks):
        # 使用HSV色彩空间生成不同的颜色
        hue = i / num_chunks
        saturation = 0.8
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        colors.append(rgb)
    return colors

def visualize_chunk_bbox():
    """可视化chunks的边界框"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"开始可视化chunks边界框: {pdf_path}")
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 提取文档块和位置信息
        documents = extract_documents_with_block_positions(doc, "安联美元.pdf")
        meaningful_blocks = [d for d in documents if len(d['content']) > 10]
        
        # 合并所有有意义的块内容
        all_content = ""
        all_positions = []
        
        for doc_info in meaningful_blocks:
            all_content += doc_info['content'] + " "
            all_positions.extend(doc_info['positions'])
        
        # 使用与app_main.py相同的分块参数
        chunk_size = 1000
        chunk_overlap = 200
        
        # 模拟分块
        chunks = []
        for chunk_idx in range(0, len(all_content), chunk_size - chunk_overlap):
            if chunk_idx + chunk_size > len(all_content):
                chunk_text = all_content[chunk_idx:]
            else:
                chunk_text = all_content[chunk_idx:chunk_idx + chunk_size]
            
            if chunk_text.strip():
                chunk_positions = assign_positions_to_chunk(chunk_text, all_positions)
                chunk_bbox = calculate_chunk_bbox(chunk_positions)
                
                chunks.append({
                    "chunk_index": len(chunks),
                    "content": chunk_text.strip(),
                    "positions": chunk_positions,
                    "bbox": chunk_bbox,
                    "content_length": len(chunk_text.strip())
                })
        
        print(f"生成了 {len(chunks)} 个chunks")
        
        # 为每个chunk生成颜色
        colors = generate_chunk_colors(len(chunks))
        
        # 创建输出目录
        output_dir = "chunk_bbox_visualization"
        os.makedirs(output_dir, exist_ok=True)
        
        # 为每个页面创建可视化
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_rect = page.rect
            
            print(f"\n处理页面 {page_num + 1}:")
            print(f"  页面尺寸: {page_rect.width:.1f} x {page_rect.height:.1f}")
            
            # 创建新的文档来绘制
            new_doc = fitz.open()
            new_page = new_doc.new_page(width=page_rect.width, height=page_rect.height)
            
            # 复制原页面内容
            new_page.show_pdf_page(new_page.rect, doc, page_num)
            
            # 基于内容分布来分配chunks到页面
            # 由于所有chunks的Y坐标都在22-692范围内，我们按chunk索引来分配
            page_chunks = []
            
            if page_num == 0:
                # 第1页：显示前3个chunks
                page_chunks = chunks[:3]
            elif page_num == 1:
                # 第2页：显示中间2个chunks
                page_chunks = chunks[3:5]
            elif page_num == 2:
                # 第3页：显示最后2个chunks
                page_chunks = chunks[5:]
            
            print(f"  页面 {page_num + 1}: 分配 {len(page_chunks)} 个chunks")
            
            # 绘制分配的chunks
            for chunk in page_chunks:
                if chunk['positions']:
                    # 使用chunk的原始边界框
                    bbox = chunk['bbox']
                    
                    # 绘制边界框
                    color = colors[chunk['chunk_index']]
                    new_page.draw_rect(bbox, color=color, width=3)
                    
                    # 添加标签
                    label_text = f"Chunk {chunk['chunk_index'] + 1}"
                    new_page.insert_text([bbox[0], bbox[1] - 10], label_text, color=color, fontsize=12)
                    
                    print(f"    Chunk {chunk['chunk_index'] + 1}: bbox=({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
                    print(f"      位置信息数量: {len(chunk['positions'])}")
                    print(f"      内容预览: {chunk['content'][:50]}...")
            
            # 保存页面图片
            output_path = os.path.join(output_dir, f"page_{page_num + 1}_chunks.png")
            pix = new_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x缩放以获得更高分辨率
            pix.save(output_path)
            print(f"  保存页面 {page_num + 1} 到: {output_path}")
            
            new_doc.close()
        
        doc.close()
        
        print(f"\n可视化完成！")
        print(f"输出目录: {output_dir}")
        print(f"每个chunk用不同颜色标识:")
        for i, chunk in enumerate(chunks):
            color = colors[i]
            print(f"  Chunk {i+1}: RGB{color}")
        
        print(f"\n页面分配说明:")
        print(f"  页面1: Chunks 1-3 (前3个)")
        print(f"  页面2: Chunks 4-5 (中间2个)")
        print(f"  页面3: Chunks 6-7 (最后2个)")
        
    except Exception as e:
        print(f"可视化失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    visualize_chunk_bbox()
