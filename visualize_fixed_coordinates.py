#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用修复后的正确坐标可视化PDF中的关键信息位置
展示基金总值、基金经理、管理费等信息的精确定位
"""

import fitz  # PyMuPDF
import os
from pathlib import Path

def visualize_fixed_coordinates():
    """使用修复后的正确坐标可视化关键信息位置"""
    
    # PDF文件路径
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    # 创建输出目录
    output_dir = Path("fixed_coordinates_visualization")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🎯 使用修复后的正确坐标可视化关键信息位置")
    print(f"📁 PDF文件: {pdf_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 修复后的正确坐标数据
    fixed_coordinates = [
        {
            "name": "基金总值",
            "bbox": [36.9119987487793, 396.734130859375, 71.71895599365234, 404.7938232421875],
            "page": 1,
            "text": "基金总值：",
            "description": "基金总值的标签位置"
        },
        {
            "name": "基金总值数值",
            "bbox": [117.6500015258789, 395.7666931152344, 139.78282165527344, 404.8216552734375],
            "page": 1,
            "text": "4.4377",
            "description": "基金总值的具体数值"
        },
        {
            "name": "基金总值单位",
            "bbox": [139.72999572753906, 396.734130859375, 160.61000061035156, 404.7938232421875],
            "page": 1,
            "text": "亿美元",
            "description": "基金总值的单位"
        },
        {
            "name": "基金经理",
            "bbox": [36.9119987487793, 491.994140625, 64.75895690917969, 500.0538330078125],
            "page": 1,
            "text": "基金经理",
            "description": "基金经理标签"
        },
        {
            "name": "管理费",
            "bbox": [36.9119987487793, 507.5641174316406, 57.79895782470703, 515.623779296875],
            "page": 1,
            "text": "管理费",
            "description": "管理费标签"
        },
        {
            "name": "成立日期",
            "bbox": [36.9119987487793, 457.28411865234375, 71.59367370605469, 465.34381103515625],
            "page": 1,
            "text": "成立日期：",
            "description": "成立日期标签"
        }
    ]
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 为每个坐标生成可视化
        for i, coord_info in enumerate(fixed_coordinates):
            try:
                bbox = coord_info["bbox"]
                page_num = coord_info["page"]
                text = coord_info["text"]
                name = coord_info["name"]
                description = coord_info["description"]
                
                print(f"\n📄 处理 {name}:")
                print(f"   页码: {page_num}")
                print(f"   坐标: {bbox}")
                print(f"   文本: {text}")
                print(f"   描述: {description}")
                
                # 获取页面
                page = doc.load_page(page_num - 1)
                
                # 创建新的PDF文档用于绘制
                new_doc = fitz.open()
                new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
                
                # 复制原页面内容到新文档
                new_page.show_pdf_page(new_page.rect, doc, page_num - 1)
                
                # 绘制bbox框
                if len(bbox) == 4:
                    x0, y0, x1, y1 = bbox
                    
                    # 绘制红色矩形框
                    rect = fitz.Rect(x0, y0, x1, y1)
                    new_page.draw_rect(rect, color=(1, 0, 0), width=3)  # 红色，宽度3
                    
                    # 在框上方添加标签
                    label_text = f"{name}: {text}"
                    new_page.insert_text((x0, y0 - 20), label_text, fontsize=10, color=(1, 0, 0))
                    
                    # 添加描述信息
                    desc_text = f"{description}"
                    new_page.insert_text((x0, y0 - 35), desc_text, fontsize=8, color=(0, 0, 1))
                    
                    # 添加坐标信息
                    coord_text = f"BBox: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
                    new_page.insert_text((x0, y1 + 15), coord_text, fontsize=8, color=(0, 0, 1))
                    
                    # 添加页码信息
                    page_text = f"Page: {page_num}"
                    new_page.insert_text((x0, y1 + 30), page_text, fontsize=8, color=(0, 0, 1))
                
                # 保存为图片
                output_filename = f"{name}_page_{page_num}.png"
                output_path = output_dir / output_filename
                
                pix = new_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
                pix.save(str(output_path))
                
                # 关闭新文档
                new_doc.close()
                
                print(f"✅ 已生成: {output_filename}")
                
            except Exception as e:
                print(f"❌ 处理 {name} 失败: {e}")
        
        doc.close()
        print(f"\n🎉 可视化完成！请查看 {output_dir} 目录")
        print(f"📊 总共处理了 {len(fixed_coordinates)} 个坐标")
        
    except Exception as e:
        print(f"❌ 处理PDF失败: {e}")

if __name__ == "__main__":
    visualize_fixed_coordinates()
