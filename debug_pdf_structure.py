#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试PDF的实际页面结构和内容分布
"""

import fitz  # PyMuPDF
import os

def debug_pdf_structure():
    """调试PDF结构"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    print(f"调试PDF结构: {pdf_path}")
    print("=" * 60)
    
    try:
        doc = fitz.open(pdf_path)
        
        print(f"PDF总页数: {len(doc)}")
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_rect = page.rect
            
            print(f"\n页面 {page_num + 1}:")
            print(f"  尺寸: {page_rect.width:.1f} x {page_rect.height:.1f}")
            print(f"  边界: x0={page_rect.x0:.1f}, y0={page_rect.y0:.1f}, x1={page_rect.x1:.1f}, y1={page_rect.y1:.1f}")
            
            # 获取页面文本
            text = page.get_text()
            print(f"  文本长度: {len(text)} 字符")
            print(f"  文本预览: {text[:100]}...")
            
            # 获取页面文本字典
            text_dict = page.get_text("dict")
            if "blocks" in text_dict:
                print(f"  文本块数量: {len(text_dict['blocks'])}")
                
                # 分析每个块的Y坐标分布
                y_coords = []
                for block in text_dict["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                y_coords.append(span["bbox"][1])  # y0坐标
                
                if y_coords:
                    min_y = min(y_coords)
                    max_y = max(y_coords)
                    print(f"  Y坐标范围: {min_y:.1f} - {max_y:.1f}")
                    print(f"  Y坐标跨度: {max_y - min_y:.1f}")
                    
                    # 检查是否跨越页面边界
                    if max_y > page_rect.height:
                        print(f"  ⚠️  警告: 内容超出页面高度!")
                    else:
                        print(f"  ✅ 内容在页面范围内")
        
        doc.close()
        
    except Exception as e:
        print(f"调试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_structure()
