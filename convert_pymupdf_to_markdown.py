#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将PyMuPDF提取的文本转换为结构化的Markdown格式
保持表格结构和位置信息，便于AI理解
"""

import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Tuple

def detect_table_structure(text_blocks: List[Dict]) -> List[Dict]:
    """检测表格结构"""
    tables = []
    current_table = []
    
    for block in text_blocks:
        if "lines" in block:
            # 检查是否可能是表格行
            lines = block["lines"]
            if len(lines) > 0:
                # 检查是否有多个span（可能是表格列）
                max_spans = max(len(line.get("spans", [])) for line in lines)
                if max_spans > 1:
                    # 可能是表格
                    table_data = []
                    for line in lines:
                        row = []
                        for span in line.get("spans", []):
                            row.append({
                                "text": span["text"].strip(),
                                "bbox": span["bbox"],
                                "font_size": span["size"]
                            })
                        if any(cell["text"] for cell in row):
                            table_data.append(row)
                    
                    if table_data:
                        tables.append({
                            "type": "table",
                            "data": table_data,
                            "bbox": block["bbox"]
                        })
    
    return tables

def convert_to_markdown(pdf_path: str, output_path: str = None) -> str:
    """将PDF转换为Markdown格式"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    markdown_content = []
    
    # 添加文档标题
    filename = os.path.basename(pdf_path)
    markdown_content.append(f"# {filename}\n")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        markdown_content.append(f"\n## 第 {page_num + 1} 页\n")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            # 检测表格
            tables = detect_table_structure(blocks["blocks"])
            table_used = set()
            
            # 处理每个文本块
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    # 检查是否已被识别为表格
                    is_table_block = False
                    for table in tables:
                        if block["bbox"] == table["bbox"]:
                            is_table_block = True
                            if block_idx not in table_used:
                                # 转换为Markdown表格
                                markdown_content.append("### 表格\n")
                                markdown_content.append("```\n")
                                
                                table_data = table["data"]
                                # 添加表头
                                if table_data:
                                    headers = [cell["text"] for cell in table_data[0]]
                                    markdown_content.append("| " + " | ".join(headers) + " |\n")
                                    markdown_content.append("| " + " | ".join(["---"] * len(headers)) + " |\n")
                                    
                                    # 添加数据行
                                    for row in table_data[1:]:
                                        row_text = [cell["text"] for cell in row]
                                        markdown_content.append("| " + " | ".join(row_text) + " |\n")
                                
                                markdown_content.append("```\n\n")
                                table_used.add(block_idx)
                            break
                    
                    if not is_table_block:
                        # 普通文本块
                        block_text = ""
                        for line in block["lines"]:
                            line_text = ""
                            for span in line["spans"]:
                                text = span["text"].strip()
                                if text:
                                    line_text += text + " "
                            if line_text.strip():
                                block_text += line_text.strip() + "\n"
                        
                        if block_text.strip():
                            # 检查是否可能是标题（基于字体大小）
                            max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                            if max_font_size > 12:  # 假设大于12pt的是标题
                                markdown_content.append(f"### {block_text.strip()}\n\n")
                            else:
                                markdown_content.append(f"{block_text.strip()}\n\n")
    
    doc.close()
    
    # 合并所有内容
    final_markdown = "".join(markdown_content)
    
    # 保存到文件
    if output_path is None:
        output_path = f"{os.path.splitext(pdf_path)[0]}_converted.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
    
    print(f"Markdown文件已保存到: {output_path}")
    return final_markdown

def convert_with_positions(pdf_path: str, output_path: str = None) -> str:
    """转换为带位置信息的Markdown格式"""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    markdown_content = []
    
    # 添加文档标题
    filename = os.path.basename(pdf_path)
    markdown_content.append(f"# {filename}\n")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        
        # 页面标题
        markdown_content.append(f"\n## 第 {page_num + 1} 页\n")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    block_text = ""
                    positions = []
                    
                    for line_idx, line in enumerate(block["lines"]):
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                bbox = span["bbox"]
                                font_size = span["size"]
                                font_name = span["font"]
                                
                                # 添加位置信息标签
                                pos_tag = f'<pos page="{page_num+1}" bbox="{bbox}" font_size="{font_size:.1f}" font="{font_name}">'
                                block_text += f"{pos_tag}{text}</pos> "
                                positions.append({
                                    "text": text,
                                    "page": page_num + 1,
                                    "bbox": bbox,
                                    "font_size": font_size,
                                    "font": font_name
                                })
                        
                        if line_idx < len(block["lines"]) - 1:
                            block_text += "\n"
                    
                    if block_text.strip():
                        # 检查是否可能是标题
                        max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                        if max_font_size > 12:
                            markdown_content.append(f"### {block_text.strip()}\n\n")
                        else:
                            markdown_content.append(f"{block_text.strip()}\n\n")
    
    doc.close()
    
    # 合并所有内容
    final_markdown = "".join(markdown_content)
    
    # 保存到文件
    if output_path is None:
        output_path = f"{os.path.splitext(pdf_path)[0]}_with_positions.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
    
    print(f"带位置信息的Markdown文件已保存到: {output_path}")
    return final_markdown

if __name__ == "__main__":
    pdf_path = "python_service/file/安联美元.pdf"
    
    print("正在转换PDF为Markdown格式...")
    
    # 转换1: 结构化Markdown（适合AI理解）
    try:
        markdown_result = convert_to_markdown(pdf_path)
        print("✅ 结构化Markdown转换完成")
    except Exception as e:
        print(f"❌ 结构化Markdown转换失败: {e}")
    
    # 转换2: 带位置信息的Markdown（保持位置信息）
    try:
        pos_markdown = convert_with_positions(pdf_path)
        print("✅ 带位置信息的Markdown转换完成")
    except Exception as e:
        print(f"❌ 带位置信息的Markdown转换失败: {e}")
    
    print("\n转换完成！")
