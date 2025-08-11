#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug PDF位置信息提取过程的脚本
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_service'))

# 直接从app_main.py导入需要的变量和函数
from python_service.app_main import PYMUPDF4LLM_AVAILABLE
import fitz  # PyMuPDF

def debug_pdfllm_position():
    """Debug PDF位置信息提取过程"""
    print("🔍 开始Debug PDF位置信息提取过程")
    print("=" * 60)
    
    # 测试文件路径
    pdf_path = "python_service/file/安联美元.pdf"
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"📁 测试文件: {pdf_path}")
    
    # 1. 检查PyMuPDF4LLM是否可用
    print("\n1️⃣ 检查PyMuPDF4LLM可用性")
    print(f"   PYMUPDF4LLM_AVAILABLE: {PYMUPDF4LLM_AVAILABLE}")
    
    if PYMUPDF4LLM_AVAILABLE:
        try:
            from mypymupdf4llm import LlamaMarkdownReader
            print("   ✅ LlamaMarkdownReader 导入成功")
        except ImportError as e:
            print(f"   ❌ LlamaMarkdownReader 导入失败: {e}")
            return
    else:
        print("   ❌ PyMuPDF4LLM 不可用")
        return
    
    # 2. 检查PDFLLM相关函数是否可用
    print("\n2️⃣ 检查PDFLLM相关函数")
    try:
        # 使用正确的导入路径
        from mypymupdf4llm.helpers.pymupdf_rag import to_markdown as to_md_with_pos
        from python_service.md_pos_to_aligned import parse_md_with_pos, save_aligned
        
        print(f"   to_md_with_pos: {'✅' if to_md_with_pos else '❌'}")
        print(f"   parse_md_with_pos: {'✅' if parse_md_with_pos else '❌'}")
        print(f"   save_aligned: {'✅' if save_aligned else '❌'}")
        
        if not all([to_md_with_pos, parse_md_with_pos, save_aligned]):
            print("   ❌ PDFLLM函数不完整，无法继续")
            return
            
    except ImportError as e:
        print(f"   ❌ mypymupdf4llm 导入失败: {e}")
        return
    
    # 3. 测试LlamaMarkdownReader
    print("\n3️⃣ 测试LlamaMarkdownReader")
    try:
        reader = LlamaMarkdownReader()
        md_nodes = reader.load_data(pdf_path)
        print(f"   ✅ 加载成功，返回类型: {type(md_nodes)}")
        print(f"   ✅ 节点数量: {len(md_nodes) if isinstance(md_nodes, list) else 1}")
        
        # 显示第一个节点的内容
        if isinstance(md_nodes, list) and md_nodes:
            first_node = md_nodes[0]
            print(f"   📝 第一个节点类型: {type(first_node)}")
            print(f"   📝 第一个节点内容预览: {str(first_node)[:200]}...")
            
    except Exception as e:
        print(f"   ❌ LlamaMarkdownReader 测试失败: {e}")
        return
    
    # 4. 测试to_md_with_pos
    print("\n4️⃣ 测试to_md_with_pos")
    try:
        md_text = to_md_with_pos(pdf_path, emit_positions=True)
        print(f"   ✅ to_md_with_pos 成功")
        print(f"   📝 生成的markdown长度: {len(md_text)}")
        print(f"   📝 前500字符预览:")
        print("   " + "-" * 40)
        print("   " + md_text[:500])
        print("   " + "-" * 40)
        
        # 保存到文件
        debug_md_path = "debug_pdfllm_output.md"
        with open(debug_md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"   💾 完整markdown已保存到: {debug_md_path}")
        
    except Exception as e:
        print(f"   ❌ to_md_with_pos 失败: {e}")
        return
    
    # 5. 测试parse_md_with_pos
    print("\n5️⃣ 测试parse_md_with_pos")
    try:
        items = parse_md_with_pos(debug_md_path)
        print(f"   ✅ parse_md_with_pos 成功")
        print(f"   📊 解析出 {len(items)} 个项目")
        
        # 显示前几个项目的信息
        for i, item in enumerate(items[:3]):
            print(f"   📋 项目 {i}:")
            print(f"     类型: {type(item)}")
            print(f"     属性: {dir(item)}")
            
            # 尝试获取常见属性
            for attr in ['text', 'page', 'bbox', 'pos']:
                if hasattr(item, attr):
                    value = getattr(item, attr)
                    print(f"     {attr}: {value}")
            
            print()
            
    except Exception as e:
        print(f"   ❌ parse_md_with_pos 失败: {e}")
        return
    
    # 6. 测试分块过程
    print("\n6️⃣ 测试分块过程")
    try:
        from langchain.text_splitter import MarkdownHeaderTextSplitter
        
        # 定义分块配置
        markdown_headers = [
            ("#", "标题1"),
            ("##", "标题2"), 
            ("###", "标题3"),
            ("####", "标题4"),
            ("#####", "标题5"),
            ("######", "标题6"),
        ]
        
        # 使用LlamaMarkdownReader的结果
        if isinstance(md_nodes, list):
            markdown_text = "\n\n".join(str(n) for n in md_nodes)
        else:
            markdown_text = str(md_nodes)
        
        print(f"   📝 准备分块的markdown长度: {len(markdown_text)}")
        
        # 分块
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=markdown_headers)
        chunks = splitter.split_text(markdown_text)
        print(f"   ✅ 分块成功，生成 {len(chunks)} 个chunks")
        
        # 显示每个chunk的信息
        for i, chunk in enumerate(chunks[:3]):
            print(f"   📋 Chunk {i}:")
            print(f"     内容长度: {len(chunk.page_content) if hasattr(chunk, 'page_content') else 'N/A'}")
            print(f"     内容预览: {chunk.page_content[:200] if hasattr(chunk, 'page_content') else str(chunk)[:200]}...")
            print()
            
    except Exception as e:
        print(f"   ❌ 分块过程失败: {e}")
        return
    
    # 7. 测试位置信息匹配
    print("\n7️⃣ 测试位置信息匹配")
    try:
        # 显示前几个items的详细信息
        print("   📊 前5个items的详细信息:")
        for i, item in enumerate(items[:5]):
            print(f"   📋 项目 {i}:")
            print(f"     类型: {type(item)}")
            if isinstance(item, dict):
                for key, value in item.items():
                    print(f"     {key}: {value}")
            else:
                print(f"     属性: {dir(item)}")
                # 尝试获取常见属性
                for attr in ['text', 'page', 'bbox', 'pos']:
                    if hasattr(item, attr):
                        value = getattr(item, attr)
                        print(f"     {attr}: {value}")
            print()
        
        # 模拟位置信息匹配过程
        if 'chunks' in locals():
            for i, chunk in enumerate(chunks[:3]):
                chunk_content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
                chunk_text = chunk_content[:100]  # 取前100字符作为标识
                print(f"   🔍 匹配 Chunk {i}:")
                print(f"     标识文本: {chunk_text}")
                
                best_match = None
                best_score = 0
                
                # 在items中查找最匹配的文本块
                for item in items:
                    if isinstance(item, dict) and 'text' in item:
                        item_text = item['text']
                        # 计算文本相似度
                        overlap = 0
                        for char in chunk_text:
                            if char in item_text:
                                overlap += 1
                        score = overlap / len(chunk_text) if chunk_text else 0
                        
                        if score > best_score and score > 0.3:
                            best_score = score
                            best_match = item
                
                if best_match:
                    page_num = best_match.get('page', -1)
                    bbox = best_match.get('bbox', [])
                    print(f"     ✅ 找到匹配: page={page_num}, bbox={bbox}, score={best_score:.2f}")
                else:
                    print(f"     ❌ 未找到匹配")
                print()
            
    except Exception as e:
        print(f"   ❌ 位置信息匹配失败: {e}")
        return
    
    print("\n🎉 Debug完成！")
    print("=" * 60)

if __name__ == "__main__":
    debug_pdfllm_position()
