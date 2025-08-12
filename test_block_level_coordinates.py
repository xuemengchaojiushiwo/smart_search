#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试块级模糊定位效果
对比精确坐标和块级坐标的区别
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
from typing import List

def expand_bbox_to_block_level(bbox: List[float], page_width: float, page_height: float) -> List[float]:
    """
    将精确的文本片段bbox扩展为块级bbox，提供更好的用户体验
    使用更保守的扩展策略，避免过度扩展
    """
    if len(bbox) != 4:
        return bbox
    
    x0, y0, x1, y1 = bbox
    
    # 计算当前文本的宽度和高度
    text_width = x1 - x0
    text_height = y1 - y0
    
    # 更保守的扩展策略
    # 水平扩展：左右各扩展文本宽度的50%，但不超过页面边距
    horizontal_expansion = min(text_width * 0.5, 30)  # 最大扩展30像素
    
    expanded_x0 = max(20, x0 - horizontal_expansion)
    expanded_x1 = min(page_width - 20, x1 + horizontal_expansion)
    
    # 垂直扩展：上下各扩展文本高度的50%，但不超过页面边距
    vertical_expansion = min(text_height * 0.5, 20)  # 最大扩展20像素
    
    expanded_y0 = max(20, y0 - vertical_expansion)
    expanded_y1 = min(page_height - 20, y1 + vertical_expansion)
    
    return [expanded_x0, expanded_y0, expanded_x1, expanded_y1]

def test_block_level_coordinates():
    """测试块级模糊定位效果"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"🧪 测试块级模糊定位效果: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)  # 第1页
        
        # 获取页面尺寸
        page_width = page.rect.width
        page_height = page.rect.height
        print(f"📄 页面尺寸: {page_width:.1f} x {page_height:.1f}")
        
        # 测试坐标数据
        test_coordinates = [
            {
                "name": "基金总值标签",
                "bbox": [36.9119987487793, 396.734130859375, 71.71895599365234, 404.7938232421875],
                "text": "基金总值：",
                "description": "基金总值的标签位置"
            },
            {
                "name": "基金总值数值",
                "bbox": [117.6500015258789, 395.7666931152344, 139.78282165527344, 404.8216552734375],
                "text": "4.4377",
                "description": "基金总值的具体数值"
            },
            {
                "name": "基金总值单位",
                "bbox": [139.72999572753906, 396.734130859375, 160.61000061035156, 404.7938232421875],
                "text": "亿美元",
                "description": "基金总值的单位"
            }
        ]
        
        print(f"\n🔍 对比精确坐标和块级坐标:")
        for coord_info in test_coordinates:
            name = coord_info["name"]
            original_bbox = coord_info["bbox"]
            text = coord_info["text"]
            
            print(f"\n📄 {name}:")
            print(f"   文本: {text}")
            print(f"   精确坐标: {original_bbox}")
            
            # 计算扩展后的块级坐标
            expanded_bbox = expand_bbox_to_block_level(original_bbox, page_width, page_height)
            print(f"   块级坐标: {expanded_bbox}")
            
            # 计算扩展比例
            original_width = original_bbox[2] - original_bbox[0]
            original_height = original_bbox[3] - original_bbox[1]
            expanded_width = expanded_bbox[2] - expanded_bbox[0]
            expanded_height = expanded_bbox[3] - expanded_bbox[1]
            
            width_ratio = expanded_width / original_width if original_width > 0 else 0
            height_ratio = expanded_height / original_height if original_height > 0 else 0
            
            print(f"   扩展比例: 宽度 {width_ratio:.1f}x, 高度 {height_ratio:.1f}x")
            
            # 判断扩展是否合理
            if width_ratio > 3 or height_ratio > 3:
                print(f"   ⚠️  扩展比例较大，可能需要调整")
            elif width_ratio > 1.5 or height_ratio > 1.5:
                print(f"   ✅ 扩展比例合理")
            else:
                print(f"   ℹ️  扩展比例较小")
        
        # 创建可视化对比
        output_dir = Path("block_level_comparison")
        output_dir.mkdir(exist_ok=True)
        
        print(f"\n🎨 生成可视化对比...")
        
        # 为每个坐标生成对比图
        for coord_info in test_coordinates:
            name = coord_info["name"]
            original_bbox = coord_info["bbox"]
            expanded_bbox = expand_bbox_to_block_level(original_bbox, page_width, page_height)
            
            # 创建新的PDF文档用于绘制
            new_doc = fitz.open()
            new_page = new_doc.new_page(width=page_width, height=page_height)
            
            # 复制原页面内容
            new_page.show_pdf_page(new_page.rect, doc, 0)
            
            # 绘制精确坐标框（红色细线）
            if len(original_bbox) == 4:
                x0, y0, x1, y1 = original_bbox
                rect = fitz.Rect(x0, y0, x1, y1)
                new_page.draw_rect(rect, color=(1, 0, 0), width=2)  # 红色细线
                
                # 添加标签
                new_page.insert_text((x0, y0 - 25), f"精确: {name}", fontsize=8, color=(1, 0, 0))
                new_page.insert_text((x0, y0 - 10), f"({x0:.1f}, {y0:.1f})", fontsize=6, color=(1, 0, 0))
            
            # 绘制块级坐标框（蓝色粗线）
            if len(expanded_bbox) == 4:
                x0, y0, x1, y1 = expanded_bbox
                rect = fitz.Rect(x0, y0, x1, y1)
                new_page.draw_rect(rect, color=(0, 0, 1), width=3)  # 蓝色粗线
                
                # 添加标签
                new_page.insert_text((x0, y1 + 10), f"块级: {name}", fontsize=8, color=(0, 0, 1))
                new_page.insert_text((x0, y1 + 25), f"({x0:.1f}, {y0:.1f})", fontsize=6, color=(0, 0, 1))
            
            # 保存图片
            output_filename = f"{name}_comparison.png"
            output_path = output_dir / output_filename
            
            pix = new_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
            pix.save(str(output_path))
            
            # 关闭新文档
            new_doc.close()
            
            print(f"   ✅ 已生成: {output_filename}")
        
        doc.close()
        print(f"\n🎉 对比完成！请查看 {output_dir} 目录")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

if __name__ == "__main__":
    test_block_level_coordinates()
