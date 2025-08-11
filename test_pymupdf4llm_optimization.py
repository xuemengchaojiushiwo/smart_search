#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyMuPDF4LLM 优化测试脚本
验证优化后的PyMuPDF4LLM分块效果
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# 导入配置
import sys
sys.path.append('python_service')
from config import DOCUMENT_CONFIG, CHUNKING_CONFIG

# 尝试导入PyMuPDF4LLM
try:
    from mypymupdf4llm import LlamaMarkdownReader
    PYMUPDF4LLM_AVAILABLE = True
except ImportError:
    PYMUPDF4LLM_AVAILABLE = False
    print("⚠️ PyMuPDF4LLM 不可用")

from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain.schema import Document

class PyMuPDF4LLMOptimizationTester:
    """PyMuPDF4LLM 优化测试器"""
    
    def __init__(self):
        self.test_files = [
            "python_service/file/安联美元.pdf",
            "python_service/file/店铺入住流程.pdf", 
            "python_service/file/manus介绍.docx",
            "python_service/file/小红书选品.xlsx",
            "python_service/file/network_skill.pptx"
        ]
    
    def test_pymupdf4llm_chunking(self, file_path: str) -> Dict[str, Any]:
        """测试PyMuPDF4LLM分块效果"""
        print(f"测试文件: {file_path}")
        
        if not os.path.exists(file_path):
            return {'success': False, 'error': '文件不存在'}
        
        start_time = time.time()
        
        try:
            # 使用PyMuPDF4LLM进行结构化分块
            if PYMUPDF4LLM_AVAILABLE:
                reader = LlamaMarkdownReader()
                markdown_text = reader.load_data(file_path)
                
                # 使用优化后的MarkdownHeaderTextSplitter
                splitter = MarkdownHeaderTextSplitter(
                    headers_to_split_on=CHUNKING_CONFIG['markdown_headers']
                )
                chunks = splitter.split_text(markdown_text)
                
                # 如果chunks太少，使用更细粒度的分割
                if len(chunks) < CHUNKING_CONFIG['pymupdf4llm_config']['min_chunks']:
                    print(f"chunks数量较少({len(chunks)})，使用更细粒度的分割")
                    # 使用传统分块作为补充
                    text_splitter = RecursiveCharacterTextSplitter(
                        chunk_size=DOCUMENT_CONFIG['chunk_size'],
                        chunk_overlap=DOCUMENT_CONFIG['chunk_overlap'],
                        length_function=len,
                        separators=DOCUMENT_CONFIG['splitter_config']['separators'],
                        keep_separator=DOCUMENT_CONFIG['splitter_config']['keep_separator'],
                        is_separator_regex=DOCUMENT_CONFIG['splitter_config']['is_separator_regex']
                    )
                    additional_chunks = text_splitter.split_text(markdown_text)
                    additional_chunks = [Document(page_content=chunk) for chunk in additional_chunks]
                    chunks.extend(additional_chunks)
                    print(f"补充分割后，总chunks数: {len(chunks)}")
                
                processing_method = "pymupdf4llm_optimized"
                
            else:
                # 回退到传统分块
                print("PyMuPDF4LLM不可用，使用传统分块")
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=DOCUMENT_CONFIG['chunk_size'],
                    chunk_overlap=DOCUMENT_CONFIG['chunk_overlap'],
                    length_function=len,
                    separators=DOCUMENT_CONFIG['splitter_config']['separators'],
                    keep_separator=DOCUMENT_CONFIG['splitter_config']['keep_separator'],
                    is_separator_regex=DOCUMENT_CONFIG['splitter_config']['is_separator_regex']
                )
                chunks = text_splitter.split_text(f"模拟文本内容 - {os.path.basename(file_path)}" * 50)
                chunks = [Document(page_content=chunk) for chunk in chunks]
                processing_method = "traditional_fallback"
            
            end_time = time.time()
            
            # 分析分块效果
            analysis = self.analyze_chunking_effectiveness(chunks)
            
            return {
                'success': True,
                'file_path': file_path,
                'file_extension': Path(file_path).suffix.lower(),
                'processing_time': end_time - start_time,
                'total_chunks': len(chunks),
                'processing_method': processing_method,
                'analysis': analysis,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def analyze_chunking_effectiveness(self, chunks: List[Document]) -> Dict[str, Any]:
        """分析分块效果"""
        analysis = {
            'total_chunks': len(chunks),
            'chunk_sizes': [],
            'avg_chunk_size': 0,
            'min_chunk_size': 0,
            'max_chunk_size': 0,
            'structure_preservation': 0,
            'semantic_coherence': 0,
            'overlap_analysis': []
        }
        
        if not chunks:
            return analysis
        
        # 分析chunk大小
        chunk_sizes = [len(chunk.page_content) for chunk in chunks]
        analysis['chunk_sizes'] = chunk_sizes
        analysis['avg_chunk_size'] = sum(chunk_sizes) / len(chunk_sizes)
        analysis['min_chunk_size'] = min(chunk_sizes)
        analysis['max_chunk_size'] = max(chunk_sizes)
        
        # 分析重叠
        if len(chunks) > 1:
            for i in range(len(chunks) - 1):
                chunk1 = chunks[i].page_content
                chunk2 = chunks[i + 1].page_content
                
                # 计算重叠
                overlap = self.calculate_overlap(chunk1, chunk2)
                overlap_ratio = overlap / len(chunk2) if len(chunk2) > 0 else 0
                
                analysis['overlap_analysis'].append({
                    'chunk_pair': f"{i+1}-{i+2}",
                    'overlap_chars': overlap,
                    'overlap_ratio': overlap_ratio,
                    'chunk1_size': len(chunk1),
                    'chunk2_size': len(chunk2)
                })
        
        # 评估结构保持
        structure_score = 0
        semantic_score = 0
        
        for chunk in chunks:
            content = chunk.page_content
            
            # 检查是否包含标题结构
            if any(header in content for header in ['#', '##', '###', '####', '#####', '######']):
                structure_score += 1
            
            # 检查语义连贯性（简单的句子完整性检查）
            if content.strip().endswith(('.', '。', '!', '！', '?', '？')):
                semantic_score += 1
        
        analysis['structure_preservation'] = structure_score / len(chunks) * 100 if chunks else 0
        analysis['semantic_coherence'] = semantic_score / len(chunks) * 100 if chunks else 0
        
        return analysis
    
    def calculate_overlap(self, text1: str, text2: str) -> int:
        """计算两个文本的重叠字符数"""
        # 检查字符级别的重叠
        for i in range(min(200, len(text1))):
            end_text = text1[-(i+1):]
            if text2.startswith(end_text) and len(end_text) > 10:
                return len(end_text)
        
        # 检查词级别的重叠
        words1 = text1.split()
        words2 = text2.split()
        
        if len(words1) < 3 or len(words2) < 3:
            return 0
        
        for i in range(min(15, len(words1))):
            end_words = ' '.join(words1[-(i+1):])
            if text2.startswith(end_words):
                return len(end_words)
        
        return 0
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("开始PyMuPDF4LLM优化测试...")
        
        results = {}
        total_files = 0
        successful_files = 0
        
        for file_path in self.test_files:
            if os.path.exists(file_path):
                total_files += 1
                result = self.test_pymupdf4llm_chunking(file_path)
                results[Path(file_path).name] = result
                
                if result['success']:
                    successful_files += 1
                    analysis = result['analysis']
                    processing_method = result['processing_method']
                    total_chunks = result['total_chunks']
                    structure_score = analysis['structure_preservation']
                    semantic_score = analysis['semantic_coherence']
                    
                    print(f"✅ {Path(file_path).name}:")
                    print(f"  处理方法: {processing_method}")
                    print(f"  块数: {total_chunks}")
                    print(f"  平均块大小: {analysis['avg_chunk_size']:.1f}")
                    print(f"  结构保持分数: {structure_score:.1f}%")
                    print(f"  语义连贯分数: {semantic_score:.1f}%")
                else:
                    print(f"❌ {Path(file_path).name}: {result['error']}")
            else:
                print(f"⚠️ 文件不存在: {file_path}")
        
        # 生成总结报告
        summary = {
            'total_files': total_files,
            'successful_files': successful_files,
            'success_rate': successful_files / total_files if total_files > 0 else 0,
            'average_structure_score': 0,
            'average_semantic_score': 0,
            'total_chunks_generated': 0
        }
        
        if successful_files > 0:
            structure_scores = [r['analysis']['structure_preservation'] for r in results.values() if r['success']]
            semantic_scores = [r['analysis']['semantic_coherence'] for r in results.values() if r['success']]
            total_chunks = [r['total_chunks'] for r in results.values() if r['success']]
            
            summary['average_structure_score'] = sum(structure_scores) / len(structure_scores)
            summary['average_semantic_score'] = sum(semantic_scores) / len(semantic_scores)
            summary['total_chunks_generated'] = sum(total_chunks)
        
        results['summary'] = summary
        
        return results

def main():
    """主函数"""
    tester = PyMuPDF4LLMOptimizationTester()
    results = tester.run_all_tests()
    
    # 保存结果
    output_file = "pymupdf4llm_optimization_test_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成！结果已保存到: {output_file}")
    print(f"总结:")
    print(f"- 测试文件数: {results['summary']['total_files']}")
    print(f"- 成功处理: {results['summary']['successful_files']}")
    print(f"- 成功率: {results['summary']['success_rate']:.1%}")
    print(f"- 平均结构保持分数: {results['summary']['average_structure_score']:.1f}%")
    print(f"- 平均语义连贯分数: {results['summary']['average_semantic_score']:.1f}%")
    print(f"- 总生成块数: {results['summary']['total_chunks_generated']}")

if __name__ == "__main__":
    main()
