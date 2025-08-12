#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG坐标可视化工具 - 简化版
直接使用测试RAG时的坐标数据
"""

import fitz  # PyMuPDF
import os
from pathlib import Path

def visualize_rag_coordinates():
    """可视化RAG返回的坐标"""
    
    # PDF文件路径
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    # 创建输出目录
    output_dir = Path("rag_visualization")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🎯 开始可视化RAG坐标...")
    print(f"📁 PDF文件: {pdf_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 使用测试RAG时返回的真实坐标数据
    rag_coordinates = [
        {
            "name": "基金总值信息",
            "bbox": [31.04204559326172, 631.7859497070312, 286.9818420410156, 638.6079711914062],
            "page": 1,
            "text": "安联美元基金的总值为4.4377亿美元"
        },
        {
            "name": "基金经理信息", 
            "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
            "page": 1,
            "text": "基金经理：Justin Kass / David Oberto / Michael Yee"
        },
        {
            "name": "管理费信息",
            "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
            "page": 1,
            "text": "管理费为每年1.19%"
        },
        {
            "name": "基金成立日期",
            "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
            "page": 1,
            "text": "成立日期：2010年8月2日"
        },
        {
            "name": "经济分析内容",
            "bbox": [28.882043838500977, 641.6259765625, 301.1078186035156, 648.447998046875],
            "page": 3,
            "text": "盈利增长、联储局因通胀及劳动力市场持续正常化"
        }
    ]
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 处理每个坐标
        for i, coord_info in enumerate(rag_coordinates):
            try:
                bbox = coord_info["bbox"]
                page_num = coord_info["page"]
                text = coord_info["text"]
                name = coord_info["name"]
                
                print(f"\n📄 处理 {name}:")
                print(f"   页码: {page_num}")
                print(f"   坐标: {bbox}")
                print(f"   文本: {text}")
                
                # 获取页面
                page = doc.load_page(page_num - 1)
                
                # 创建新的页面用于绘制
                new_page = doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # 复制原页面内容
                new_page.show_pdf_page(new_page.rect, doc, page_num - 1)
                
                # 绘制bbox框
                if len(bbox) == 4:
                    x0, y0, x1, y1 = bbox
                    
                    # 绘制红色矩形框
                    rect = fitz.Rect(x0, y0, x1, y1)
                    new_page.draw_rect(rect, color=(1, 0, 0), width=3)  # 红色，宽度3
                    
                    # 在框上方添加标签
                    label_text = f"{name}: {text[:30]}..."
                    new_page.insert_text((x0, y0 - 15), label_text, fontsize=10, color=(1, 0, 0))
                    
                    # 添加坐标信息
                    coord_text = f"BBox: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
                    new_page.insert_text((x0, y1 + 15), coord_text, fontsize=8, color=(0, 0, 1))
                    
                    # 添加页码信息
                    page_text = f"Page: {page_num}"
                    new_page.insert_text((x0, y1 + 30), page_text, fontsize=8, color=(0, 0, 1))
                
                # 保存为图片
                output_filename = f"rag_{name}_page_{page_num}.png"
                output_path = output_dir / output_filename
                
                pix = new_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
                pix.save(str(output_path))
                
                print(f"✅ 已生成: {output_filename}")
                
            except Exception as e:
                print(f"❌ 处理 {name} 失败: {e}")
        
        doc.close()
        print(f"\n🎉 可视化完成！请查看 {output_dir} 目录")
        
    except Exception as e:
        print(f"❌ 处理PDF失败: {e}")

if __name__ == "__main__":
    visualize_rag_coordinates()
