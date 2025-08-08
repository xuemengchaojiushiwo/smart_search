#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重叠调试脚本
分析为什么重叠检测显示为0
"""

import os
import json
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# 导入配置
import sys
sys.path.append('python_service')
from config import DOCUMENT_CONFIG

def debug_overlap():
    """调试重叠问题"""
    
    # 测试文本
    test_text = """
    这是一个测试文档，用于验证重叠功能是否正常工作。
    第一段内容包含了一些基本信息，比如文档的标题和目的。
    第二段内容继续扩展了主题，提供了更多的细节和说明。
    第三段内容进一步深入，包含了具体的示例和案例分析。
    第四段内容总结了前面的内容，并提供了结论和建议。
    第五段内容展望了未来的发展方向和可能的改进措施。
    第六段内容补充了一些额外的信息，确保文档的完整性。
    第七段内容再次强调了重要的观点，并提供了最终的总结。
    第八段内容包含了参考文献和相关的资源链接。
    第九段内容提供了联系方式和其他有用的信息。
    第十段内容作为结尾，感谢读者的关注和支持。
    """ * 10  # 重复10次以生成足够长的文本
    
    print(f"测试文本长度: {len(test_text)} 字符")
    
    # 使用当前配置
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300,  # 30%重叠
        length_function=len,
    )
    
    chunks = text_splitter.split_text(test_text)
    chunks = [Document(page_content=chunk) for chunk in chunks]
    
    print(f"生成了 {len(chunks)} 个块")
    
    # 分析每个块
    for i, chunk in enumerate(chunks):
        print(f"\n块 {i+1}:")
        print(f"长度: {len(chunk.page_content)} 字符")
        print(f"内容预览: {chunk.page_content[:100]}...")
        print(f"内容结尾: ...{chunk.page_content[-100:]}")
    
    # 检查相邻块的重叠
    print(f"\n=== 重叠分析 ===")
    for i in range(len(chunks) - 1):
        chunk1 = chunks[i].page_content
        chunk2 = chunks[i + 1].page_content
        
        # 检查结尾和开头的重叠
        overlap_found = False
        for j in range(min(50, len(chunk1))):
            end_text = chunk1[-(j+1):]
            if chunk2.startswith(end_text) and len(end_text) > 10:
                print(f"块 {i+1}-{i+2}: 找到重叠 '{end_text}' ({len(end_text)} 字符)")
                overlap_found = True
                break
        
        if not overlap_found:
            print(f"块 {i+1}-{i+2}: 未找到明显重叠")
            print(f"  块{i+1}结尾: ...{chunk1[-50:]}")
            print(f"  块{i+2}开头: {chunk2[:50]}...")

def test_simple_overlap():
    """测试简单的重叠功能"""
    
    # 简单的测试文本
    simple_text = "这是第一句话。这是第二句话。这是第三句话。这是第四句话。这是第五句话。" * 20
    
    print(f"\n=== 简单重叠测试 ===")
    print(f"文本长度: {len(simple_text)} 字符")
    
    # 使用较小的块大小进行测试
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,  # 25%重叠
        length_function=len,
    )
    
    chunks = text_splitter.split_text(simple_text)
    chunks = [Document(page_content=chunk) for chunk in chunks]
    
    print(f"生成了 {len(chunks)} 个块")
    
    for i in range(len(chunks) - 1):
        chunk1 = chunks[i].page_content
        chunk2 = chunks[i + 1].page_content
        
        # 查找重叠
        overlap = find_overlap(chunk1, chunk2)
        print(f"块 {i+1}-{i+2}: 重叠 {overlap} 字符")

def find_overlap(text1: str, text2: str) -> int:
    """查找两个文本的重叠字符数"""
    words1 = text1.split()
    words2 = text2.split()
    
    if len(words1) < 3 or len(words2) < 3:
        return 0
    
    # 检查结尾和开头的重叠
    for i in range(min(10, len(words1))):
        end_words = ' '.join(words1[-(i+1):])
        if text2.startswith(end_words):
            return len(end_words)
    
    return 0

if __name__ == "__main__":
    debug_overlap()
    test_simple_overlap()
