#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的PyMuPDF方案
验证PDFLLM风格输出和位置信息提取
"""

import fitz  # PyMuPDF
import re
import os

def test_pdfllm_style_generation():
    """测试PDFLLM风格Markdown生成"""
    pdf_path = "python_service/file/安联美元.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print("🔍 测试新的PyMuPDF方案...")
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        print(f"✅ 成功打开PDF，页数: {len(doc)}")
        
        # 生成PDFLLM风格的Markdown
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
                                    # 添加位置信息标签，格式类似pdfllm
                                    pos_tag = f'<sub>pos: page={page_num+1}, bbox={span["bbox"]}</sub>'
                                    line_text += f"{text} {pos_tag} "
                            
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
        output_path = "python_service/file/安联美元_new_pymupdf_solution.md"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        print(f"✅ PDFLLM风格Markdown已保存到: {output_path}")
        print(f"📊 文件长度: {len(final_content):,} 字符")
        
        # 统计位置标签
        pos_tags = re.findall(r'<sub>pos: page=\d+, bbox=\([^)]+\)</sub>', final_content)
        print(f"📍 位置标签数量: {len(pos_tags)}")
        
        # 检查关键信息
        key_phrases = ["基金总值", "海外基金资料", "投资目标", "管理费", "风险水平"]
        for phrase in key_phrases:
            count = final_content.count(phrase)
            status = "✅" if count > 0 else "❌"
            print(f"   {status} {phrase}: {count}")
        
        # 解析位置信息
        items = parse_pdfllm_style_markdown(final_content)
        print(f"🔍 解析出 {len(items)} 个位置信息项")
        
        if items:
            print("📋 前3个位置信息项:")
            for i, item in enumerate(items[:3]):
                print(f"   {i+1}. 页{item.get('page', 'N/A')}, bbox={item.get('bbox', [])}")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def parse_pdfllm_style_markdown(md_text: str):
    """解析PDFLLM风格的Markdown，提取位置信息"""
    items = []
    
    # 匹配 <sub>pos: page=X, bbox=(...)</sub> 格式
    pattern = r'<sub>pos: page=(\d+), bbox=\(([^)]+)\)</sub>'
    
    matches = re.findall(pattern, md_text)
    for match in matches:
        page_num = int(match[0])
        bbox_str = match[1]
        
        try:
            # 解析bbox字符串 "x0, y0, x1, y1"
            bbox_parts = bbox_str.split(',')
            if len(bbox_parts) == 4:
                bbox = [float(part.strip()) for part in bbox_parts]
                
                items.append({
                    "page": page_num,
                    "bbox": bbox,
                    "char_start": -1,
                    "char_end": -1,
                    "text": ""
                })
        except Exception as e:
            print(f"⚠️ 解析bbox失败: {bbox_str}, 错误: {e}")
            continue
    
    return items

if __name__ == "__main__":
    test_pdfllm_style_generation()
    print("\n🎯 测试完成！现在可以对比新旧方案的效果了。")
