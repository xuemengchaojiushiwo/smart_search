#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试PDF坐标位置
验证基金总值等关键信息的坐标是否正确
"""

import fitz  # PyMuPDF
import os

def debug_pdf_coordinates():
    """调试PDF中的坐标位置"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"🔍 调试PDF坐标位置: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        print(f"✅ 成功打开PDF，共 {len(doc)} 页")
        
        # 检查第1页的坐标
        page = doc.load_page(0)  # 第1页
        print(f"\n📄 第1页坐标分析:")
        
        # 获取页面文本块
        blocks = page.get_text("dict")
        
        if "blocks" in blocks:
            # 查找包含基金总值信息的块
            fund_value_blocks = []
            
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    for line_idx, line in enumerate(block["lines"]):
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                # 检查是否包含基金总值相关信息
                                if any(keyword in text for keyword in ["基金总值", "4.4377", "亿美元"]):
                                    bbox = span["bbox"]
                                    font_size = span["size"]
                                    print(f"📍 找到基金总值相关信息:")
                                    print(f"   文本: {text}")
                                    print(f"   坐标: {bbox}")
                                    print(f"   字体大小: {font_size}")
                                    print(f"   块索引: {block_idx}, 行: {line_idx}, 段: {span_idx}")
                                    print()
                                    fund_value_blocks.append({
                                        "text": text,
                                        "bbox": bbox,
                                        "font_size": font_size,
                                        "block_idx": block_idx,
                                        "line_idx": line_idx,
                                        "span_idx": span_idx
                                    })
            
            # 检查页面底部的坐标（之前RAG返回的坐标）
            print(f"🔍 检查页面底部坐标 (31.04, 631.79, 286.98, 638.61):")
            bottom_bbox = [31.04204559326172, 631.7859497070312, 286.9818420410156, 638.6079711914062]
            
            # 在这个坐标范围内查找文本
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    for line_idx, line in enumerate(block["lines"]):
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                span_bbox = span["bbox"]
                                # 检查是否在底部坐标范围内
                                if (abs(span_bbox[1] - bottom_bbox[1]) < 50 and  # y坐标接近
                                    abs(span_bbox[0] - bottom_bbox[0]) < 50):     # x坐标接近
                                    print(f"📍 在底部坐标附近找到文本:")
                                    print(f"   文本: {text}")
                                    print(f"   坐标: {span_bbox}")
                                    print(f"   字体大小: {span['size']}")
                                    print(f"   块索引: {block_idx}, 行: {line_idx}, 段: {span_idx}")
                                    print()
            
            # 检查页面中部的坐标（另一个RAG返回的坐标）
            print(f"🔍 检查页面中部坐标 (27.36, 126.66, 572.44, 137.08):")
            middle_bbox = [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562]
            
            for block_idx, block in enumerate(blocks["blocks"]):
                if "lines" in block:
                    for line_idx, line in enumerate(block["lines"]):
                        for span_idx, span in enumerate(line["spans"]):
                            text = span["text"].strip()
                            if text:
                                span_bbox = span["bbox"]
                                # 检查是否在中部坐标范围内
                                if (abs(span_bbox[1] - middle_bbox[1]) < 50 and  # y坐标接近
                                    abs(span_bbox[0] - middle_bbox[0]) < 50):     # x坐标接近
                                    print(f"📍 在中部坐标附近找到文本:")
                                    print(f"   文本: {text}")
                                    print(f"   坐标: {span_bbox}")
                                    print(f"   字体大小: {span['size']}")
                                    print(f"   块索引: {block_idx}, 行: {line_idx}, 段: {span_idx}")
                                    print()
        
        doc.close()
        
    except Exception as e:
        print(f"❌ 处理PDF失败: {e}")

if __name__ == "__main__":
    debug_pdf_coordinates()
