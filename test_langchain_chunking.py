#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangChain切块API测试脚本
测试RecursiveCharacterTextSplitter的各种参数配置
"""

import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# 导入配置
import sys
sys.path.append('python_service')
from config import DOCUMENT_CONFIG, CHUNKING_CONFIG

class LangChainChunkingTester:
    """LangChain切块API测试器"""
    
    def __init__(self):
        self.test_files = [
            "python_service/file/安联美元.pdf",
            "python_service/file/店铺入住流程.pdf", 
            "python_service/file/manus介绍.docx",
            "python_service/file/小红书选品.xlsx",
            "python_service/file/network_skill.pptx"
        ]
    
    def test_basic_chunking(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Document]:
        """测试基本的切块功能"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ".", "!", "?"]
        )
        chunks = text_splitter.split_text(text)
        return [Document(page_content=chunk) for chunk in chunks]
    
    def test_advanced_chunking(self, text: str, chunk_size: int, chunk_overlap: int) -> List[Document]:
        """测试高级切块功能，包含更多分隔符"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",  # 段落分隔
                "\n",    # 行分隔
                "。",    # 中文句号
                "！",    # 中文感叹号
                "？",    # 中文问号
                ".",     # 英文句号
                "!",     # 英文感叹号
                "?",     # 英文问号
                ";",     # 分号
                ":",     # 冒号
                "，",    # 中文逗号
                ",",     # 英文逗号
                " ",     # 空格
            ]
        )
        chunks = text_splitter.split_text(text)
        return [Document(page_content=chunk) for chunk in chunks]
    
    def analyze_chunk_overlap(self, chunks: List[Document]) -> Dict[str, Any]:
        """分析块之间的重叠情况"""
        analysis = {
            'total_chunks': len(chunks),
            'overlap_details': [],
            'average_overlap_ratio': 0,
            'overlap_found': False
        }
        
        if len(chunks) <= 1:
            return analysis
        
        total_overlap_chars = 0
        overlap_count = 0
        
        for i in range(len(chunks) - 1):
            chunk1 = chunks[i].page_content
            chunk2 = chunks[i + 1].page_content
            
            # 查找重叠
            overlap_chars = self.find_actual_overlap(chunk1, chunk2)
            overlap_ratio = overlap_chars / len(chunk2) if len(chunk2) > 0 else 0
            
            overlap_detail = {
                'chunk_pair': f"{i+1}-{i+2}",
                'overlap_chars': overlap_chars,
                'overlap_ratio': overlap_ratio,
                'chunk1_length': len(chunk1),
                'chunk2_length': len(chunk2),
                'chunk1_end': chunk1[-50:] if len(chunk1) > 50 else chunk1,
                'chunk2_start': chunk2[:50] if len(chunk2) > 50 else chunk2
            }
            
            analysis['overlap_details'].append(overlap_detail)
            
            if overlap_chars > 0:
                total_overlap_chars += overlap_chars
                overlap_count += 1
        
        if len(chunks) > 1:
            analysis['average_overlap_ratio'] = total_overlap_chars / (len(chunks) - 1) / (sum(len(chunk.page_content) for chunk in chunks) / len(chunks))
            analysis['overlap_found'] = overlap_count > 0
        
        return analysis
    
    def find_actual_overlap(self, text1: str, text2: str) -> int:
        """查找两个文本的实际重叠字符数"""
        # 方法1: 检查字符级别的重叠
        for i in range(min(100, len(text1))):
            end_text = text1[-(i+1):]
            if text2.startswith(end_text) and len(end_text) > 5:
                return len(end_text)
        
        # 方法2: 检查词级别的重叠
        words1 = text1.split()
        words2 = text2.split()
        
        if len(words1) < 2 or len(words2) < 2:
            return 0
        
        for i in range(min(10, len(words1))):
            end_words = ' '.join(words1[-(i+1):])
            if text2.startswith(end_words):
                return len(end_words)
        
        return 0
    
    def extract_text_from_file(self, file_path: str) -> str:
        """从文件提取文本（简化版本）"""
        try:
            # 尝试导入PyMuPDF Pro
            try:
                import pymupdf
                if file_path.endswith('.pdf'):
                    doc = pymupdf.open(file_path)
                    text_parts = []
                    for page_num, page in enumerate(doc):
                        text = page.get_text()
                        if text.strip():
                            text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{text}")
                    return "\n\n".join(text_parts)
            except ImportError:
                pass
            
            # 对于其他文件类型，返回模拟文本
            file_extension = Path(file_path).suffix.lower()
            if file_extension == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                # 生成模拟文本用于测试
                return f"这是{file_extension}文件的模拟内容。" * 100
                
        except Exception as e:
            print(f"文件读取失败: {e}")
            return f"文件读取失败 - {os.path.basename(file_path)}"
    
    def test_file_with_different_configs(self, file_path: str) -> Dict[str, Any]:
        """使用不同配置测试文件"""
        print(f"测试文件: {file_path}")
        
        if not os.path.exists(file_path):
            return {'success': False, 'error': '文件不存在'}
        
        start_time = time.time()
        
        try:
            # 提取文本
            text = self.extract_text_from_file(file_path)
            
            if len(text) < 100:
                return {'success': False, 'error': f'文本太短({len(text)}字符)'}
            
            results = {}
            
            # 测试配置1: 基本配置
            config1 = {
                'chunk_size': 1000,
                'chunk_overlap': 200,
                'description': '基本配置 (20%重叠)'
            }
            chunks1 = self.test_basic_chunking(text, config1['chunk_size'], config1['chunk_overlap'])
            analysis1 = self.analyze_chunk_overlap(chunks1)
            results['config1'] = {
                'config': config1,
                'chunks_count': len(chunks1),
                'analysis': analysis1
            }
            
            # 测试配置2: 优化配置
            config2 = {
                'chunk_size': 1000,
                'chunk_overlap': 300,
                'description': '优化配置 (30%重叠)'
            }
            chunks2 = self.test_basic_chunking(text, config2['chunk_size'], config2['chunk_overlap'])
            analysis2 = self.analyze_chunk_overlap(chunks2)
            results['config2'] = {
                'config': config2,
                'chunks_count': len(chunks2),
                'analysis': analysis2
            }
            
            # 测试配置3: 高级配置
            config3 = {
                'chunk_size': 1000,
                'chunk_overlap': 400,
                'description': '高级配置 (40%重叠)'
            }
            chunks3 = self.test_advanced_chunking(text, config3['chunk_size'], config3['chunk_overlap'])
            analysis3 = self.analyze_chunk_overlap(chunks3)
            results['config3'] = {
                'config': config3,
                'chunks_count': len(chunks3),
                'analysis': analysis3
            }
            
            end_time = time.time()
            
            return {
                'success': True,
                'file_path': file_path,
                'file_size_mb': os.path.getsize(file_path) / (1024 * 1024),
                'text_length': len(text),
                'processing_time': end_time - start_time,
                'results': results
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        print("开始LangChain切块API测试...")
        
        results = {}
        total_files = 0
        successful_files = 0
        
        for file_path in self.test_files:
            if os.path.exists(file_path):
                total_files += 1
                result = self.test_file_with_different_configs(file_path)
                results[Path(file_path).name] = result
                
                if result['success']:
                    successful_files += 1
                    print(f"✅ {Path(file_path).name}: 处理成功")
                    
                    # 打印各配置的结果
                    for config_name, config_result in result['results'].items():
                        config = config_result['config']
                        analysis = config_result['analysis']
                        chunks_count = config_result['chunks_count']
                        
                        print(f"  {config['description']}:")
                        print(f"    块数: {chunks_count}")
                        print(f"    平均重叠比例: {analysis['average_overlap_ratio']:.2%}")
                        print(f"    找到重叠: {'是' if analysis['overlap_found'] else '否'}")
                else:
                    print(f"❌ {Path(file_path).name}: {result['error']}")
            else:
                print(f"⚠️ 文件不存在: {file_path}")
        
        # 生成总结报告
        summary = {
            'total_files': total_files,
            'successful_files': successful_files,
            'success_rate': successful_files / total_files if total_files > 0 else 0
        }
        
        results['summary'] = summary
        
        return results

def main():
    """主函数"""
    tester = LangChainChunkingTester()
    results = tester.run_all_tests()
    
    # 保存结果
    output_file = "langchain_chunking_test_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n测试完成！结果已保存到: {output_file}")
    print(f"总结:")
    print(f"- 测试文件数: {results['summary']['total_files']}")
    print(f"- 成功处理: {results['summary']['successful_files']}")
    print(f"- 成功率: {results['summary']['success_rate']:.1%}")

if __name__ == "__main__":
    main()
