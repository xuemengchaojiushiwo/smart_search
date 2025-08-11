#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将PyMuPDF提取的文本转换为混合格式Markdown
结合结构化信息和关键位置信息，优化AI理解能力
"""

import fitz  # PyMuPDF
import re
import os
from typing import List, Dict, Tuple

def is_important_text(span: Dict) -> bool:
    """判断是否为重要文本（标题、关键信息等）"""
    # 重要文本的特征
    important_patterns = [
        r'基金总值',
        r'海外基金资料',
        r'投资目标',
        r'管理费',
        r'风险水平',
        r'股份类别',
        r'ISIN',
        r'彭博代码',
        r'成立日期',
        r'基金经理',
        r'收益分配'
    ]
    
    text = span["text"].strip()
    if not text:
        return False
    
    # 检查是否匹配重要模式
    for pattern in important_patterns:
        if re.search(pattern, text):
            return True
    
    # 检查字体大小（大字体可能是标题）
    if span["size"] > 10:
        return True
    
    # 检查字体名称（粗体可能是重要信息）
    font_name = span["font"].lower()
    if any(keyword in font_name for keyword in ['bold', 'heavy', 'black']):
        return True
    
    return False

def detect_table_structure(text_blocks: List[Dict]) -> List[Dict]:
    """检测表格结构"""
    tables = []
    
    for block in text_blocks:
        if "lines" in block:
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
                                "font_size": span["size"],
                                "font": span["font"]
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

def convert_to_hybrid_markdown(pdf_path: str, output_path: str = None) -> str:
    """转换为混合格式Markdown"""
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
                                
                                markdown_content.append("\n")
                                table_used.add(block_idx)
                            break
                    
                    if not is_table_block:
                        # 普通文本块
                        block_text = ""
                        important_positions = []
                        
                        for line_idx, line in enumerate(block["lines"]):
                            line_text = ""
                            for span_idx, span in enumerate(line["spans"]):
                                text = span["text"].strip()
                                if text:
                                    # 检查是否为重要文本
                                    if is_important_text(span):
                                        # 为重要文本添加位置信息
                                        pos_tag = f'<pos page="{page_num+1}" bbox="{span["bbox"]}" font_size="{span["size"]:.1f}">{text}</pos>'
                                        line_text += pos_tag + " "
                                        important_positions.append({
                                            "text": text,
                                            "page": page_num + 1,
                                            "bbox": span["bbox"],
                                            "font_size": span["size"]
                                        })
                                    else:
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
        output_path = f"{os.path.splitext(pdf_path)[0]}_hybrid.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
    
    print(f"混合格式Markdown文件已保存到: {output_path}")
    return final_markdown

def create_clean_markdown(pdf_path: str, output_path: str = None) -> str:
    """创建清洁的Markdown版本，去除位置标签但保持结构"""
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
                                
                                markdown_content.append("\n")
                                table_used.add(block_idx)
                            break
                    
                    if not is_table_block:
                        # 普通文本块
                        block_text = ""
                        
                        for line_idx, line in enumerate(block["lines"]):
                            line_text = ""
                            for span_idx, span in enumerate(line["spans"]):
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
        output_path = f"{os.path.splitext(pdf_path)[0]}_clean.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_markdown)
    
    print(f"清洁Markdown文件已保存到: {output_path}")
    return final_markdown

if __name__ == "__main__":
    pdf_path = "python_service/file/安联美元.pdf"
    
    print("正在转换PDF为混合格式Markdown...")
    
    # 转换1: 混合格式Markdown（重要信息带位置标签）
    try:
        hybrid_markdown = convert_to_hybrid_markdown(pdf_path)
        print("✅ 混合格式Markdown转换完成")
    except Exception as e:
        print(f"❌ 混合格式Markdown转换失败: {e}")
    
    # 转换2: 清洁Markdown（无位置标签，适合AI理解）
    try:
        clean_markdown = create_clean_markdown(pdf_path)
        print("✅ 清洁Markdown转换完成")
    except Exception as e:
        print(f"❌ 清洁Markdown转换失败: {e}")
    
    print("\n转换完成！")
    print("\n📋 文件说明:")
    print("- 混合格式Markdown: 重要信息保留位置标签，适合需要定位的场景")
    print("- 清洁Markdown: 去除所有位置标签，结构清晰，适合AI理解和RAG问答")
