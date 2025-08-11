#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将PDF转换为类似pdfllm_document_with_pos.md的格式
使用PyMuPDF确保信息完整，保持位置信息
"""

import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Tuple

def extract_text_with_positions(pdf_path: str, output_path: str = None) -> str:
    """提取带位置信息的文本，格式类似pdfllm_document_with_pos.md"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    content_lines = []
    
    # 添加文档标题
    filename = os.path.basename(pdf_path)
    content_lines.append(f"# {filename}")
    content_lines.append("")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        content_lines.append(f"## 第 {page_num + 1} 页")
        content_lines.append("")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    block_text = ""
                    block_positions = []
                    
                    for line_idx, line in enumerate(block["lines"]):
                        line_text = ""
                        line_positions = []
                        
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                # 添加位置信息标签，格式类似pdfllm
                                pos_tag = f'<sub>pos: page={page_num+1}, bbox={span["bbox"]}</sub>'
                                line_text += f"{text} {pos_tag} "
                                
                                line_positions.append({
                                    "text": text,
                                    "page": page_num + 1,
                                    "bbox": span["bbox"],
                                    "font_size": span["size"],
                                    "font": span["font"]
                                })
                        
                        if line_text.strip():
                            block_text += line_text.strip() + "\n"
                            block_positions.extend(line_positions)
                    
                    if block_text.strip():
                        # 检查是否可能是标题（基于字体大小）
                        max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                        if max_font_size > 12:  # 假设大于12pt的是标题
                            content_lines.append(f"### {block_text.strip()}")
                        else:
                            content_lines.append(block_text.strip())
                        content_lines.append("")
    
    doc.close()
    
    # 合并所有内容
    final_content = "\n".join(content_lines)
    
    # 保存到文件
    if output_path is None:
        output_path = f"{os.path.splitext(pdf_path)[0]}_pdfllm_style.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"PDFLLM风格Markdown文件已保存到: {output_path}")
    return final_content

def create_compact_pos_format(pdf_path: str, output_path: str = None) -> str:
    """创建紧凑的位置信息格式，减少冗余"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    content_lines = []
    
    # 添加文档标题
    filename = os.path.basename(pdf_path)
    content_lines.append(f"# {filename}")
    content_lines.append("")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        content_lines.append(f"## 第 {page_num + 1} 页")
        content_lines.append("")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    block_text = ""
                    
                    for line_idx, line in enumerate(block["lines"]):
                        line_text = ""
                        
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                # 使用更紧凑的位置格式
                                bbox = span["bbox"]
                                pos_info = f'<pos page={page_num+1} bbox={bbox[0]:.1f},{bbox[1]:.1f},{bbox[2]:.1f},{bbox[3]:.1f}>'
                                line_text += f"{pos_info}{text}</pos> "
                        
                        if line_text.strip():
                            block_text += line_text.strip() + "\n"
                    
                    if block_text.strip():
                        # 检查是否可能是标题
                        max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                        if max_font_size > 12:
                            content_lines.append(f"### {block_text.strip()}")
                        else:
                            content_lines.append(block_text.strip())
                        content_lines.append("")
    
    doc.close()
    
    # 合并所有内容
    final_content = "\n".join(content_lines)
    
    # 保存到文件
    if output_path is None:
        output_path = f"{os.path.splitext(pdf_path)[0]}_compact_pos.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"紧凑位置格式Markdown文件已保存到: {output_path}")
    return final_content

def create_table_aware_format(pdf_path: str, output_path: str = None) -> str:
    """创建表格感知的格式，保持表格结构"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    content_lines = []
    
    # 添加文档标题
    filename = os.path.basename(pdf_path)
    content_lines.append(f"# {filename}")
    content_lines.append("")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        content_lines.append(f"## 第 {page_num + 1} 页")
        content_lines.append("")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    # 检测是否为表格（多列结构）
                    lines = block["lines"]
                    if len(lines) > 0:
                        max_spans = max(len(line.get("spans", [])) for line in lines)
                        if max_spans > 1:
                            # 可能是表格，转换为Markdown表格格式
                            content_lines.append("### 表格")
                            content_lines.append("")
                            
                            # 构建表格数据
                            table_data = []
                            for line in lines:
                                row = []
                                for span in line.get("spans", []):
                                    text = span["text"].strip()
                                    if text:
                                        # 添加位置信息
                                        pos_info = f'<pos page={page_num+1} bbox={span["bbox"]}>'
                                        row.append(f"{pos_info}{text}</pos>")
                                if any(cell for cell in row):
                                    table_data.append(row)
                            
                            # 转换为Markdown表格
                            if table_data:
                                # 表头
                                headers = table_data[0]
                                content_lines.append("| " + " | ".join(headers) + " |")
                                content_lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
                                
                                # 数据行
                                for row in table_data[1:]:
                                    content_lines.append("| " + " | ".join(row) + " |")
                                
                                content_lines.append("")
                            continue
                    
                    # 普通文本块
                    block_text = ""
                    for line_idx, line in enumerate(block["lines"]):
                        line_text = ""
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                # 添加位置信息
                                pos_info = f'<pos page={page_num+1} bbox={span["bbox"]}>'
                                line_text += f"{pos_info}{text}</pos> "
                        
                        if line_text.strip():
                            block_text += line_text.strip() + "\n"
                    
                    if block_text.strip():
                        # 检查是否可能是标题
                        max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                        if max_font_size > 12:
                            content_lines.append(f"### {block_text.strip()}")
                        else:
                            content_lines.append(block_text.strip())
                        content_lines.append("")
    
    doc.close()
    
    # 合并所有内容
    final_content = "\n".join(content_lines)
    
    # 保存到文件
    if output_path is None:
        output_path = f"{os.path.splitext(pdf_path)[0]}_table_aware.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"表格感知Markdown文件已保存到: {output_path}")
    return final_content

if __name__ == "__main__":
    pdf_path = "python_service/file/安联美元.pdf"
    
    print("正在转换PDF为PDFLLM风格的Markdown格式...")
    
    # 转换1: PDFLLM风格（类似pdfllm_document_with_pos.md）
    try:
        pdfllm_style = extract_text_with_positions(pdf_path)
        print("✅ PDFLLM风格转换完成")
    except Exception as e:
        print(f"❌ PDFLLM风格转换失败: {e}")
    
    # 转换2: 紧凑位置格式
    try:
        compact_pos = create_compact_pos_format(pdf_path)
        print("✅ 紧凑位置格式转换完成")
    except Exception as e:
        print(f"❌ 紧凑位置格式转换失败: {e}")
    
    # 转换3: 表格感知格式
    try:
        table_aware = create_table_aware_format(pdf_path)
        print("✅ 表格感知格式转换完成")
    except Exception as e:
        print(f"❌ 表格感知格式转换失败: {e}")
    
    print("\n转换完成！")
    print("\n📋 文件说明:")
    print("- PDFLLM风格: 类似pdfllm_document_with_pos.md的格式")
    print("- 紧凑位置格式: 位置信息更紧凑，减少冗余")
    print("- 表格感知格式: 保持表格结构，适合AI理解")
