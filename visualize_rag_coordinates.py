#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG坐标可视化工具
根据RAG返回的bbox坐标在PDF上画框并截图
"""

import fitz  # PyMuPDF
import os
from pathlib import Path
import json

def draw_bbox_on_pdf(pdf_path, bbox_coords, page_num, output_path, chunk_text=""):
    """
    在PDF指定页面上画框并截图
    
    Args:
        pdf_path: PDF文件路径
        bbox_coords: bbox坐标 [x0, y0, x1, y1]
        page_num: 页码（从1开始）
        output_path: 输出图片路径
        chunk_text: 对应的文本内容（用于标注）
    """
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 获取指定页面（页码从0开始）
        page = doc.load_page(page_num - 1)
        
        # 创建新的页面用于绘制
        new_page = doc.new_page(width=page.rect.width, height=page.rect.height)
        
        # 复制原页面内容
        new_page.show_pdf_page(new_page.rect, doc, page_num - 1)
        
        # 绘制bbox框
        if len(bbox_coords) == 4:
            x0, y0, x1, y1 = bbox_coords
            
            # 绘制红色矩形框
            rect = fitz.Rect(x0, y0, x1, y1)
            new_page.draw_rect(rect, color=(1, 0, 0), width=3)  # 红色，宽度3
            
            # 在框上方添加标签
            label_text = f"Chunk Text: {chunk_text[:50]}..." if len(chunk_text) > 50 else f"Chunk Text: {chunk_text}"
            new_page.insert_text((x0, y0 - 10), label_text, fontsize=10, color=(1, 0, 0))
            
            # 添加坐标信息
            coord_text = f"BBox: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
            new_page.insert_text((x0, y1 + 15), coord_text, fontsize=8, color=(0, 0, 1))
        
        # 保存为图片
        pix = new_page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2倍放大
        pix.save(output_path)
        
        doc.close()
        print(f"✅ 已生成可视化图片: {output_path}")
        
    except Exception as e:
        print(f"❌ 生成可视化图片失败: {e}")

def visualize_rag_results(pdf_path, rag_results):
    """
    可视化RAG结果中的所有坐标
    
    Args:
        pdf_path: PDF文件路径
        rag_results: RAG返回的结果数据
    """
    # 创建输出目录
    output_dir = Path("rag_visualization")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🎯 开始可视化RAG坐标...")
    print(f"📁 PDF文件: {pdf_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 处理每个引用
    for i, reference in enumerate(rag_results.get('references', [])):
        try:
            # 提取坐标信息
            bbox = reference.get('bbox_union', [])
            page_num = reference.get('page_num', 1)
            chunk_text = reference.get('content', '')[:100]  # 取前100个字符
            
            if bbox and len(bbox) == 4:
                # 生成输出文件名
                output_filename = f"rag_chunk_{i+1}_page_{page_num}.png"
                output_path = output_dir / output_filename
                
                print(f"\n📄 处理引用 {i+1}:")
                print(f"   页码: {page_num}")
                print(f"   坐标: {bbox}")
                print(f"   文本: {chunk_text}")
                
                # 生成可视化图片
                draw_bbox_on_pdf(pdf_path, bbox, page_num, str(output_path), chunk_text)
                
            else:
                print(f"⚠️ 引用 {i+1} 缺少有效的坐标信息")
                
        except Exception as e:
            print(f"❌ 处理引用 {i+1} 失败: {e}")
    
    print(f"\n🎉 可视化完成！请查看 {output_dir} 目录")

def create_sample_rag_results():
    """
    创建示例RAG结果数据（用于测试）
    """
    return {
        "references": [
            {
                "bbox_union": [31.04, 631.79, 286.98, 638.61],
                "page_num": 1,
                "content": "安联美元高收益基金的总值为4.4377亿美元"
            },
            {
                "bbox_union": [27.36, 126.66, 572.44, 137.08],
                "page_num": 1,
                "content": "基金经理：Justin Kass / David Oberto / Michael Yee"
            },
            {
                "bbox_union": [28.88, 641.63, 301.11, 648.45],
                "page_num": 3,
                "content": "盈利增长、联储局因通胀及劳动力市场持续正常化"
            }
        ]
    }

def main():
    """主函数"""
    print("🚀 RAG坐标可视化工具")
    print("=" * 50)
    
    # 检查PDF文件是否存在
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        print("请确保PDF文件路径正确")
        return
    
    # 创建示例数据或从文件读取
    print("选择数据源:")
    print("1. 使用示例数据")
    print("2. 从文件读取RAG结果")
    
    choice = input("请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        rag_results = create_sample_rag_results()
        print("✅ 使用示例数据")
    elif choice == "2":
        # 从文件读取RAG结果
        rag_file = input("请输入RAG结果文件路径: ").strip()
        try:
            with open(rag_file, 'r', encoding='utf-8') as f:
                rag_results = json.load(f)
            print("✅ 从文件读取数据成功")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return
    else:
        print("❌ 无效选择")
        return
    
    # 开始可视化
    visualize_rag_results(pdf_path, rag_results)

if __name__ == "__main__":
    main()
