#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path

def test_file_listing():
    """简单测试文件列表"""
    print("=== 测试文件列表 ===")
    
    # 文件目录
    file_dir = Path("python_service/file")
    
    if not file_dir.exists():
        print(f"文件目录不存在: {file_dir}")
        return
    
    # 获取所有文件
    files = list(file_dir.glob("*"))
    print(f"找到 {len(files)} 个文件:")
    
    for file_path in files:
        file_size_kb = file_path.stat().st_size / 1024
        print(f"  - {file_path.name} ({file_size_kb:.1f}KB)")
        
        # 根据文件类型预测切块数量
        file_ext = file_path.suffix.lower()
        if file_ext == '.pdf':
            if file_size_kb < 1024:  # 小于1MB
                chunks = 3
            elif file_size_kb < 5120:  # 小于5MB
                chunks = 8
            else:
                chunks = 15
            print(f"    PDF文件，预计切块数量: {chunks}")
        elif file_ext == '.docx':
            chunks = 4
            print(f"    Word文档，预计切块数量: {chunks}")
        elif file_ext == '.pptx':
            chunks = 6
            print(f"    PowerPoint，预计切块数量: {chunks}")
        elif file_ext == '.xlsx':
            chunks = 4
            print(f"    Excel表格，预计切块数量: {chunks}")
        else:
            chunks = 3
            print(f"    其他文件，预计切块数量: {chunks}")

def simulate_chunking():
    """模拟切块效果"""
    print("\n=== 模拟切块效果 ===")
    
    # 模拟不同文件的切块
    test_files = [
        ("安联美元.pdf", "PDF", 535),
        ("店铺入住流程.pdf", "PDF", 6600),
        ("manus介绍.docx", "DOCX", 22),
        ("小红书选品.xlsx", "XLSX", 19),
        ("network_skill.pptx", "PPTX", 14336)
    ]
    
    for filename, file_type, size_kb in test_files:
        print(f"\n文件: {filename}")
        print(f"类型: {file_type}")
        print(f"大小: {size_kb}KB")
        
        # 根据文件类型和大小生成切块
        if file_type == "PDF":
            if size_kb < 1024:
                chunks = 3
            elif size_kb < 5120:
                chunks = 8
            else:
                chunks = 15
        elif file_type == "DOCX":
            chunks = 4
        elif file_type == "PPTX":
            chunks = 6
        elif file_type == "XLSX":
            chunks = 4
        else:
            chunks = 3
        
        print(f"预计切块数量: {chunks}")
        
        # 显示前3个切块示例
        for i in range(min(3, chunks)):
            if file_type == "PDF":
                content = f"PDF第{i+1}页内容 - 包含重要的文档信息，如标题、正文、图表等。"
            elif file_type == "DOCX":
                content = f"Word文档第{i+1}节 - 包含文档的标题、段落、列表等内容。"
            elif file_type == "PPTX":
                content = f"PPT第{i+1}页 - 包含幻灯片标题、要点、图表等内容。"
            elif file_type == "XLSX":
                content = f"Excel第{i+1}个工作表 - 包含数据表格、统计信息等。"
            else:
                content = f"文件第{i+1}个片段 - 包含文档的主要内容。"
            
            print(f"  切块{i+1}: {content}")
        
        if chunks > 3:
            print(f"  ... 还有 {chunks - 3} 个切块")

def test_rag_scenario():
    """测试RAG场景"""
    print("\n=== 测试RAG场景 ===")
    
    # 模拟从PDF文档中提取的切块
    pdf_chunks = [
        "安联美元保险产品介绍 - 这是一款美元计价的保险产品，具有稳定的收益和风险保障功能。",
        "产品特点包括：1) 美元计价，规避汇率风险；2) 稳定收益，年化收益率可达3-5%；3) 风险保障，提供身故和全残保障。",
        "投保条件：年龄18-65岁，身体健康，年收入不低于10万元人民币。",
        "保险期间：10年、15年、20年可选，缴费期间与保险期间相同。",
        "保障责任：身故保险金、全残保险金、满期保险金等。"
    ]
    
    print("模拟PDF文档切块:")
    for i, chunk in enumerate(pdf_chunks):
        print(f"  切块{i+1}: {chunk}")
    
    # 模拟用户问题
    questions = [
        "安联美元保险产品有什么特点？",
        "投保条件是什么？",
        "保险期间有哪些选择？"
    ]
    
    print("\n可能的用户问题:")
    for i, question in enumerate(questions):
        print(f"  问题{i+1}: {question}")
    
    print("\nRAG回答示例:")
    print("  问题: 安联美元保险产品有什么特点？")
    print("  回答: 根据文档内容，安联美元保险产品具有以下特点：")
    print("  1. 美元计价，可以规避汇率风险")
    print("  2. 提供稳定收益，年化收益率可达3-5%")
    print("  3. 具有风险保障功能，提供身故和全残保障")
    print("  4. 保险期间灵活，可选择10年、15年或20年")

if __name__ == "__main__":
    print("开始简单测试文档切块效果...")
    
    # 1. 测试文件列表
    test_file_listing()
    
    # 2. 模拟切块效果
    simulate_chunking()
    
    # 3. 测试RAG场景
    test_rag_scenario()
    
    print("\n测试完成!") 