#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from pathlib import Path

# 添加python_service目录到路径
sys.path.append('python_service')

from config import *
from geekai_client import init_geekai_client

def test_document_chunking():
    """测试文档切块效果"""
    print("=== 测试文档切块效果 ===")
    
    # 初始化极客智坊客户端
    try:
        geekai_client = init_geekai_client(GEEKAI_API_KEY, GEEKAI_API_BASE)
        print("极客智坊客户端初始化成功")
    except Exception as e:
        print(f"极客智坊客户端初始化失败: {e}")
        return
    
    # 文件目录
    file_dir = Path("python_service/file")
    
    if not file_dir.exists():
        print(f"文件目录不存在: {file_dir}")
        return
    
    # 获取所有文件
    files = list(file_dir.glob("*"))
    print(f"找到 {len(files)} 个文件:")
    
    for file_path in files:
        print(f"  - {file_path.name} ({file_path.stat().st_size / 1024:.1f}KB)")
    
    # 测试每个文件的处理
    for file_path in files:
        print(f"\n--- 测试文件: {file_path.name} ---")
        
        try:
            # 模拟文档处理
            result = simulate_document_processing(file_path, geekai_client)
            
            if result:
                print(f"处理成功:")
                print(f"  知识ID: {result.get('knowledge_id')}")
                print(f"  处理内容: {result.get('processed_content', '')[:100]}...")
                print(f"  切块数量: {len(result.get('chunks', []))}")
                
                # 显示前3个切块
                chunks = result.get('chunks', [])
                for i, chunk in enumerate(chunks[:3]):
                    print(f"  切块{i+1}: {chunk[:100]}...")
                
                if len(chunks) > 3:
                    print(f"  ... 还有 {len(chunks) - 3} 个切块")
                    
        except Exception as e:
            print(f"处理文件 {file_path.name} 失败: {e}")

def simulate_document_processing(file_path, geekai_client):
    """模拟文档处理"""
    
    # 根据文件类型模拟不同的处理结果
    file_ext = file_path.suffix.lower()
    
    if file_ext == '.pdf':
        return simulate_pdf_processing(file_path)
    elif file_ext == '.docx':
        return simulate_docx_processing(file_path)
    elif file_ext == '.pptx':
        return simulate_pptx_processing(file_path)
    elif file_ext == '.xlsx':
        return simulate_xlsx_processing(file_path)
    else:
        return simulate_generic_processing(file_path)

def simulate_pdf_processing(file_path):
    """模拟PDF处理"""
    file_size = file_path.stat().st_size
    
    # 根据文件大小估算切块数量
    if file_size < 1024 * 1024:  # 小于1MB
        chunk_count = 3
    elif file_size < 5 * 1024 * 1024:  # 小于5MB
        chunk_count = 8
    else:
        chunk_count = 15
    
    chunks = []
    for i in range(chunk_count):
        chunks.append(f"PDF文档第{i+1}个切块内容 - 这是{file_path.name}的模拟内容片段，包含重要的文档信息。")
    
    return {
        "knowledge_id": f"pdf_{file_path.stem}",
        "processed_content": f"这是{file_path.name}的完整处理内容",
        "chunks": chunks,
        "file_type": "PDF",
        "file_size": file_size,
        "chunk_count": len(chunks)
    }

def simulate_docx_processing(file_path):
    """模拟DOCX处理"""
    chunks = [
        f"Word文档第1个切块 - {file_path.name}的标题和简介部分",
        f"Word文档第2个切块 - {file_path.name}的主要内容部分",
        f"Word文档第3个切块 - {file_path.name}的详细说明部分",
        f"Word文档第4个切块 - {file_path.name}的总结和结论部分"
    ]
    
    return {
        "knowledge_id": f"docx_{file_path.stem}",
        "processed_content": f"这是{file_path.name}的完整处理内容",
        "chunks": chunks,
        "file_type": "DOCX",
        "file_size": file_path.stat().st_size,
        "chunk_count": len(chunks)
    }

def simulate_pptx_processing(file_path):
    """模拟PPTX处理"""
    chunks = [
        f"PPT第1页 - {file_path.name}的封面和目录",
        f"PPT第2页 - {file_path.name}的主要内容概述",
        f"PPT第3页 - {file_path.name}的详细内容展示",
        f"PPT第4页 - {file_path.name}的案例分析",
        f"PPT第5页 - {file_path.name}的总结和建议",
        f"PPT第6页 - {file_path.name}的问答环节"
    ]
    
    return {
        "knowledge_id": f"pptx_{file_path.stem}",
        "processed_content": f"这是{file_path.name}的完整处理内容",
        "chunks": chunks,
        "file_type": "PPTX",
        "file_size": file_path.stat().st_size,
        "chunk_count": len(chunks)
    }

def simulate_xlsx_processing(file_path):
    """模拟XLSX处理"""
    chunks = [
        f"Excel表格第1个切块 - {file_path.name}的数据概览",
        f"Excel表格第2个切块 - {file_path.name}的详细数据",
        f"Excel表格第3个切块 - {file_path.name}的统计信息",
        f"Excel表格第4个切块 - {file_path.name}的图表分析"
    ]
    
    return {
        "knowledge_id": f"xlsx_{file_path.stem}",
        "processed_content": f"这是{file_path.name}的完整处理内容",
        "chunks": chunks,
        "file_type": "XLSX",
        "file_size": file_path.stat().st_size,
        "chunk_count": len(chunks)
    }

def simulate_generic_processing(file_path):
    """模拟通用文件处理"""
    chunks = [
        f"通用文件第1个切块 - {file_path.name}的内容片段1",
        f"通用文件第2个切块 - {file_path.name}的内容片段2",
        f"通用文件第3个切块 - {file_path.name}的内容片段3"
    ]
    
    return {
        "knowledge_id": f"generic_{file_path.stem}",
        "processed_content": f"这是{file_path.name}的完整处理内容",
        "chunks": chunks,
        "file_type": "GENERIC",
        "file_size": file_path.stat().st_size,
        "chunk_count": len(chunks)
    }

def test_rag_with_chunks():
    """测试使用切块进行RAG对话"""
    print("\n=== 测试RAG对话效果 ===")
    
    try:
        geekai_client = init_geekai_client(GEEKAI_API_KEY, GEEKAI_API_BASE)
        
        # 模拟一些文档切块
        test_chunks = [
            "Spring Boot是一个基于Spring框架的快速开发框架，它简化了Spring应用的配置和部署过程。",
            "Spring Boot提供了自动配置、起步依赖等特性，让开发者可以快速构建生产就绪的应用程序。",
            "Spring Boot内置了Tomcat、Jetty等Web服务器，支持多种数据库连接，提供了丰富的starter模块。"
        ]
        
        # 测试RAG对话
        question = "什么是Spring Boot？它有什么特点？"
        
        print(f"问题: {question}")
        print("相关文档切块:")
        for i, chunk in enumerate(test_chunks):
            print(f"  切块{i+1}: {chunk}")
        
        # 调用RAG对话
        result = geekai_client.rag_chat(question, test_chunks)
        
        if result.get('success'):
            print(f"\nRAG回答: {result['answer']}")
            print(f"引用的文档切块数: {len(result['references'])}")
        else:
            print(f"RAG对话失败: {result.get('answer', '未知错误')}")
            
    except Exception as e:
        print(f"RAG测试失败: {e}")

if __name__ == "__main__":
    print("开始测试文档切块效果...")
    
    # 1. 测试文档切块
    test_document_chunking()
    
    # 2. 测试RAG对话
    test_rag_with_chunks()
    
    print("\n测试完成!") 