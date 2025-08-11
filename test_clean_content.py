#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的干净内容方案
验证内容不包含位置标签，位置信息单独保存
"""

import fitz  # PyMuPDF
import re
import os

def test_clean_content_generation():
    """测试干净内容生成"""
    pdf_path = "python_service/file/安联美元.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print("🔍 测试新的干净内容方案...")
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        print(f"✅ 成功打开PDF，页数: {len(doc)}")
        
        # 生成干净的Markdown内容
        content_lines = []
        content_lines.append(f"# {os.path.basename(pdf_path)}")
        content_lines.append("")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
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
                                    # 只添加文本内容，不添加位置标签
                                    line_text += text + " "
                            
                            if line_text.strip():
                                block_text += line_text.strip() + "\n"
                        
                        if block_text.strip():
                            # 检查是否可能是标题（基于字体大小）
                            max_font_size = max(span["size"] for line in block["lines"] for span in line["spans"])
                            if max_font_size > 12:  # 假设大于12pt的是标题
                                content_lines.append(f"### {block_text.strip()}")
                            else:
                                content_lines.append(block_text.strip())
                            content_lines.append("")
        
        # 合并所有内容
        final_content = "\n".join(content_lines)
        
        # 保存到文件
        output_path = "python_service/file/安联美元_clean_content.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ 干净内容Markdown已保存到: {output_path}")
        print(f"📊 文件长度: {len(final_content):,} 字符")
        
        # 检查是否包含位置标签
        pos_tags = re.findall(r'<sub>pos:|<pos|bbox=', final_content)
        if pos_tags:
            print(f"❌ 内容中仍然包含位置标签: {len(pos_tags)} 个")
        else:
            print("✅ 内容中不包含位置标签")
        
        # 检查关键信息
        key_phrases = ["基金总值", "海外基金资料", "投资目标", "管理费", "风险水平"]
        for phrase in key_phrases:
            count = final_content.count(phrase)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {phrase}: {count}")
        
        # 单独提取位置信息
        position_mapping = extract_position_mapping(doc)
        print(f"🔍 单独提取出 {len(position_mapping)} 个位置信息项")
        
        if position_mapping:
            print("📋 前3个位置信息项:")
            for i, pos_info in enumerate(position_mapping[:3]):
                text = pos_info.get("text", "")[:20] + "..." if len(pos_info.get("text", "")) > 20 else pos_info.get("text", "")
                print(f"   {i+1}. 文本: '{text}', 页{pos_info.get('page', 'N/A')}, bbox={pos_info.get('bbox', [])}")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def extract_position_mapping(doc):
    """单独提取位置信息映射"""
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
    
    return position_mapping

if __name__ == "__main__":
    test_clean_content_generation()
    print("\n🎯 测试完成！现在内容应该干净了，位置信息单独保存。")
