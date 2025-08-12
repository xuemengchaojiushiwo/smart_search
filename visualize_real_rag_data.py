#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG坐标可视化工具 - 使用真实测试数据
根据测试RAG时的真实日志数据可视化坐标
"""

import fitz  # PyMuPDF
import os
from pathlib import Path

def visualize_real_rag_data():
    """使用真实RAG测试数据可视化坐标"""
    
    # PDF文件路径
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    # 创建输出目录
    output_dir = Path("rag_visualization")
    output_dir.mkdir(exist_ok=True)
    
    print(f"🎯 开始可视化真实RAG坐标...")
    print(f"📁 PDF文件: {pdf_path}")
    print(f"📁 输出目录: {output_dir}")
    
    # 从测试RAG日志中提取的真实数据
    real_rag_data = [
        {
            "question": "安联美元基金的总值是多少？",
            "answer": "安联美元基金的总值为4.4377亿美元。根据文档第1页的信息。",
            "references": [
                {
                    "name": "引用1 - 基金总值",
                    "bbox": [31.04204559326172, 631.7859497070312, 286.9818420410156, 638.6079711914062],
                    "page": 1,
                    "text": "安联美元基金的总值为4.4377亿美元",
                    "relevance": 1.576
                },
                {
                    "name": "引用2 - 基金信息",
                    "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
                    "page": 1,
                    "text": "基金经理：Justin Kass / David Oberto / Michael Yee",
                    "relevance": 1.575
                },
                {
                    "name": "引用3 - 经济分析",
                    "bbox": [28.882043838500977, 641.6259765625, 301.1078186035156, 648.447998046875],
                    "page": 3,
                    "text": "盈利增长、联储局因通胀及劳动力市场持续正常化",
                    "relevance": 1.574
                }
            ]
        },
        {
            "question": "这个基金的投资目标是什么？",
            "answer": "这个基金的投资目标是投资于美国债券市场的高收益评级企业债券，以实现长期资本增值和收益。",
            "references": [
                {
                    "name": "引用1 - 投资目标",
                    "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
                    "page": 1,
                    "text": "投资目标：美国债券市场高收益评级企业债券",
                    "relevance": 1.506
                },
                {
                    "name": "引用2 - 基金策略",
                    "bbox": [31.04204559326172, 631.7859497070312, 286.9818420410156, 638.6079711914062],
                    "page": 1,
                    "text": "基金策略：长期资本增值和收益",
                    "relevance": 1.491
                }
            ]
        },
        {
            "question": "管理费是多少？",
            "answer": "管理费为每年1.19%。根据文档第1页的信息。",
            "references": [
                {
                    "name": "引用1 - 管理费",
                    "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
                    "page": 1,
                    "text": "管理费：每年1.19%",
                    "relevance": 1.379
                }
            ]
        },
        {
            "question": "基金成立日期是什么时候？",
            "answer": "基金成立日期是2010年8月2日（AM类（美元）收息股份）。",
            "references": [
                {
                    "name": "引用1 - 成立日期",
                    "bbox": [27.360000610351562, 126.6589584350586, 572.43701171875, 137.08096313476562],
                    "page": 1,
                    "text": "成立日期：2010年8月2日",
                    "relevance": 1.419
                }
            ]
        }
    ]
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        
        # 处理每个问题
        for q_idx, q_data in enumerate(real_rag_data):
            question = q_data["question"]
            answer = q_data["answer"]
            references = q_data["references"]
            
            print(f"\n🔍 问题 {q_idx + 1}: {question}")
            print(f"✅ 答案: {answer}")
            print(f"📚 引用数量: {len(references)}")
            
            # 为每个引用生成可视化
            for ref_idx, ref in enumerate(references):
                try:
                    bbox = ref["bbox"]
                    page_num = ref["page"]
                    text = ref["text"]
                    name = ref["name"]
                    relevance = ref["relevance"]
                    
                    print(f"\n📄 处理 {name}:")
                    print(f"   页码: {page_num}")
                    print(f"   坐标: {bbox}")
                    print(f"   文本: {text}")
                    print(f"   相关性: {relevance}")
                    
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
                        
                        # 在框上方添加问题标签
                        question_label = f"Q{q_idx + 1}: {question[:40]}..."
                        new_page.insert_text((x0, y0 - 30), question_label, fontsize=9, color=(1, 0, 0))
                        
                        # 在框上方添加引用标签
                        ref_label = f"{name}: {text[:35]}..."
                        new_page.insert_text((x0, y0 - 15), ref_label, fontsize=10, color=(1, 0, 0))
                        
                        # 添加坐标信息
                        coord_text = f"BBox: ({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})"
                        new_page.insert_text((x0, y1 + 15), coord_text, fontsize=8, color=(0, 0, 1))
                        
                        # 添加页码和相关性信息
                        info_text = f"Page: {page_num} | Relevance: {relevance}"
                        new_page.insert_text((x0, y1 + 30), info_text, fontsize=8, color=(0, 0, 1))
                    
                    # 保存为图片
                    output_filename = f"Q{q_idx + 1}_{name}_page_{page_num}.png"
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
        print(f"📊 总共处理了 {len(real_rag_data)} 个问题")
        
    except Exception as e:
        print(f"❌ 处理PDF失败: {e}")

if __name__ == "__main__":
    visualize_real_rag_data()
