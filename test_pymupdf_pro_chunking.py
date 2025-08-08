#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyMuPDF Pro 文件切块测试脚本
测试PyMuPDF Pro对不同文件类型的切块效果
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import List, Dict, Any

# 添加python_service目录到路径
sys.path.append('python_service')

# 导入PyMuPDF Pro相关
from python_service.pymupdf_font_fix import setup_pymupdf_pro_environment, test_pymupdf_pro_initialization

# 初始化 PyMuPDF Pro 环境
if not setup_pymupdf_pro_environment():
    print("❌ PyMuPDF Pro 环境设置失败")
    sys.exit(1)

# 测试 PyMuPDF Pro 初始化
if not test_pymupdf_pro_initialization():
    print("❌ PyMuPDF Pro 初始化失败")
    sys.exit(1)

import pymupdf.pro

# 文档处理相关
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain.schema import Document

# PyMuPDF4LLM 用于结构化分块
try:
    from pymupdf4llm import LlamaMarkdownReader
    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    print("⚠️ PyMuPDF4LLM 不可用，将使用传统分块")
    PYMUPDF4LLM_AVAILABLE = False

# 导入配置
from python_service.config import DOCUMENT_CONFIG, CHUNKING_CONFIG

class PyMuPDFProChunkingTester:
    def __init__(self):
        self.results = {}
        self.test_files = {
            'pdf': ['python_service/file/安联美元.pdf', 'python_service/file/店铺入住流程.pdf'],
            'docx': ['python_service/file/manus介绍.docx'],
            'xlsx': ['python_service/file/小红书选品.xlsx'],
            'pptx': ['python_service/file/network_skill.pptx']
        }
        
    def analyze_coherence(self, chunks: List[Document]) -> Dict[str, Any]:
        """分析分块的连贯性"""
        coherence_analysis = {
            'total_chunks': len(chunks),
            'coherence_score': 0,
            'issues': [],
            'strengths': []
        }
        
        if len(chunks) < 2:
            return coherence_analysis
        
        # 分析连贯性问题
        issues = []
        strengths = []
        
        for i, chunk in enumerate(chunks):
            content = chunk.page_content
            
            # 检查是否有重叠部分（这是优点）
            if i > 0:
                prev_content = chunks[i-1].page_content
                overlap = self.find_overlap(prev_content, content)
                if overlap > 20:  # 重叠超过20字符
                    strengths.append(f"块{i}和{i+1}: 有{overlap}字符重叠，保持连贯性")
            
            # 检查是否在段落中间切断（只在没有重叠时才算问题）
            if i > 0:
                prev_content = chunks[i-1].page_content
                overlap = self.find_overlap(prev_content, content)
                if overlap < 10 and content.count('\n\n') < 1 and len(content) > 300:
                    issues.append(f"块{i+1}: 可能在段落中间切断且重叠不足")
            
            # 检查块长度是否合理
            if len(content) < 100:
                issues.append(f"块{i+1}: 长度过短({len(content)}字符)")
            elif len(content) > 2000:
                issues.append(f"块{i+1}: 长度过长({len(content)}字符)")
        
        # 计算连贯性分数
        total_issues = len(issues)
        total_strengths = len(strengths)
        # 调整评分逻辑：重叠是优点，减少问题权重
        coherence_score = max(0, 100 - total_issues * 5 + total_strengths * 10)
        
        coherence_analysis.update({
            'coherence_score': coherence_score,
            'issues': issues,
            'strengths': strengths
        })
        
        return coherence_analysis
    
    def find_overlap(self, text1: str, text2: str) -> int:
        """查找两个文本的重叠部分"""
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
    
    def test_pymupdf_pro_chunking(self, file_path: str) -> Dict[str, Any]:
        """测试PyMuPDF Pro文件切块"""
        print(f"测试文件: {file_path}")
        
        start_time = time.time()
        
        try:
            # 使用 PyMuPDF Pro 打开文档
            doc = pymupdf.open(file_path)
            print(f"✅ 成功打开文档，页数: {len(doc)}")
            
            # 提取文本
            text_parts = []
            for page_num, page in enumerate(doc):
                text = page.get_text()
                if text.strip():
                    text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{text}")
            
            full_text = "\n\n".join(text_parts)
            print(f"📄 文本提取完成，总字符数: {len(full_text)}")
            
            # 尝试使用 PyMuPDF4LLM 进行结构化分块
            chunks = []
            processing_method = "traditional"
            
            if PYMUPDF4LLM_AVAILABLE:
                try:
                    reader = LlamaMarkdownReader()
                    markdown_text = reader.load_data(file_path)
                    
                    # 使用 MarkdownHeaderTextSplitter 进行结构化分块
                    splitter = MarkdownHeaderTextSplitter(
                        headers_to_split_on=[
                            ("#", "标题1"),
                            ("##", "标题2"),
                            ("###", "标题3"),
                        ]
                    )
                    chunks = splitter.split_text(markdown_text)
                    processing_method = "pymupdf4llm"
                    print(f"✅ PyMuPDF4LLM 结构化分块完成，生成 {len(chunks)} 个chunks")
                    
                except Exception as e:
                    print(f"⚠️ PyMuPDF4LLM 分块失败，使用传统分块: {e}")
                    processing_method = "traditional_fallback"
            
            # 如果PyMuPDF4LLM不可用或失败，使用传统分块
            if not chunks:
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=DOCUMENT_CONFIG['chunk_size'],
                    chunk_overlap=DOCUMENT_CONFIG['chunk_overlap'],
                    length_function=len,
                )
                chunks = text_splitter.split_text(full_text)
                chunks = [Document(page_content=chunk) for chunk in chunks]
                print(f"✅ 传统分块完成，生成 {len(chunks)} 个chunks")
            
            end_time = time.time()
            
            # 统计信息
            total_text_length = sum(len(chunk.page_content) for chunk in chunks)
            avg_chunk_length = total_text_length / len(chunks) if chunks else 0
            
            # 分析连贯性
            coherence_analysis = self.analyze_coherence(chunks)
            
            # 分析chunk内容
            chunk_analysis = []
            for i, chunk in enumerate(chunks):
                chunk_analysis.append({
                    'chunk_index': i,
                    'length': len(chunk.page_content),
                    'content': chunk.page_content,
                    'coherence_issues': coherence_analysis['issues'] if i < len(coherence_analysis['issues']) else []
                })
            
            return {
                'success': True,
                'processing_time': end_time - start_time,
                'total_chunks': len(chunks),
                'total_text_length': total_text_length,
                'avg_chunk_length': avg_chunk_length,
                'chunk_analysis': chunk_analysis,
                'coherence_analysis': coherence_analysis,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'processing_method': processing_method,
                'pages_count': len(doc)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("PyMuPDF Pro 文件切块测试")
        print("=" * 60)
        
        # 测试所有文件
        for file_type, files in self.test_files.items():
            for file_path in files:
                if os.path.exists(file_path):
                    result = self.test_pymupdf_pro_chunking(file_path)
                    self.results[f"{file_type.upper()}_{Path(file_path).name}"] = result
                    self.print_result(file_type.upper(), Path(file_path).name, result)
                else:
                    print(f"❌ 文件不存在: {file_path}")
        
        # 生成测试报告
        self.generate_report()
    
    def print_result(self, file_type: str, filename: str, result: Dict[str, Any]):
        """打印测试结果"""
        print(f"\n{'-' * 50}")
        print(f"文件类型: {file_type}")
        print(f"文件名: {filename}")
        
        if result['success']:
            print(f"✅ 处理成功")
            print(f"📊 处理时间: {result['processing_time']:.2f}秒")
            print(f"📄 文件大小: {result['file_size_mb']:.2f}MB")
            print(f"📑 页数: {result.get('pages_count', 'N/A')}")
            print(f"🔢 总块数: {result['total_chunks']}")
            print(f"📏 总文本长度: {result['total_text_length']}字符")
            print(f"📐 平均块长度: {result['avg_chunk_length']:.1f}字符")
            print(f"🔧 处理方法: {result.get('processing_method', 'N/A')}")
            
            # 连贯性分析
            coherence = result.get('coherence_analysis', {})
            print(f"🎯 连贯性评分: {coherence.get('coherence_score', 0)}/100")
            
            if coherence.get('issues'):
                print(f"\n⚠️ 连贯性问题:")
                for issue in coherence['issues']:
                    print(f"  - {issue}")
            
            if coherence.get('strengths'):
                print(f"\n✅ 连贯性优点:")
                for strength in coherence['strengths']:
                    print(f"  + {strength}")
            
            # 展示所有块的内容
            print(f"\n📋 所有块内容分析:")
            for chunk_info in result['chunk_analysis']:
                print(f"\n{'='*30} 块 {chunk_info['chunk_index']+1} {'='*30}")
                print(f"长度: {chunk_info['length']} 字符")
                print(f"内容:")
                print("-" * 50)
                print(chunk_info['content'])
                print("-" * 50)
        else:
            print(f"❌ 处理失败")
            print(f"🚨 错误信息: {result['error']}")
    
    def generate_report(self):
        """生成测试报告"""
        print(f"\n{'=' * 60}")
        print("PyMuPDF Pro 测试报告总结")
        print(f"{'=' * 60}")
        
        # 统计成功和失败
        success_count = sum(1 for result in self.results.values() if result['success'])
        total_count = len(self.results)
        
        print(f"📈 总测试文件数: {total_count}")
        print(f"✅ 成功处理: {success_count}")
        print(f"❌ 失败处理: {total_count - success_count}")
        
        if success_count > 0:
            # 计算平均处理时间
            avg_time = sum(result['processing_time'] for result in self.results.values() if result['success']) / success_count
            print(f"⏱️ 平均处理时间: {avg_time:.2f}秒")
            
            # 连贯性统计
            coherence_scores = []
            for result in self.results.values():
                if result['success']:
                    coherence = result.get('coherence_analysis', {})
                    coherence_scores.append(coherence.get('coherence_score', 0))
            
            if coherence_scores:
                avg_coherence = sum(coherence_scores) / len(coherence_scores)
                print(f"🎯 平均连贯性评分: {avg_coherence:.1f}/100")
            
            # 按文件类型统计
            type_stats = {}
            method_stats = {}
            
            for key, result in self.results.items():
                if result['success']:
                    file_type = key.split('_')[0]
                    if file_type not in type_stats:
                        type_stats[file_type] = []
                    type_stats[file_type].append(result)
                    
                    method = result.get('processing_method', 'unknown')
                    if method not in method_stats:
                        method_stats[method] = 0
                    method_stats[method] += 1
            
            print(f"\n📊 按文件类型统计:")
            for file_type, results in type_stats.items():
                avg_chunks = sum(r['total_chunks'] for r in results) / len(results)
                avg_length = sum(r['avg_chunk_length'] for r in results) / len(results)
                avg_pages = sum(r.get('pages_count', 0) for r in results) / len(results)
                print(f"  {file_type}: 平均{avg_chunks:.1f}块, 平均块长度{avg_length:.1f}字符, 平均{avg_pages:.1f}页")
            
            print(f"\n🔧 处理方法统计:")
            for method, count in method_stats.items():
                print(f"  {method}: {count}个文件")
        
        # 保存详细报告
        report_file = "pymupdf_pro_chunking_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细报告已保存到: {report_file}")

def main():
    """主函数"""
    print("🚀 开始PyMuPDF Pro文件切块测试")
    tester = PyMuPDFProChunkingTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
