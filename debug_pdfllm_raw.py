#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试PDFLLM原始输出，查看是否丢失了表格内容
"""

import os
import sys
import tempfile
import shutil

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from mypymupdf4llm import LlamaMarkdownReader
    from mypymupdf4llm.helpers.pymupdf_rag import to_markdown
    print("✅ 成功导入 mypymupdf4llm")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

def debug_pdfllm_raw():
    """调试PDFLLM原始输出"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"🔍 分析PDF: {pdf_path}")
    print("=" * 60)
    
    try:
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"📁 临时目录: {temp_dir}")
            
            # 使用PDFLLM处理PDF
            print("\n🔄 使用PDFLLM处理PDF...")
            
            # 尝试不同的参数
            try:
                # 方法1：使用emit_positions=True
                print("📝 方法1: emit_positions=True")
                md_text = to_markdown(pdf_path, emit_positions=True)
                print(f"✅ 成功生成Markdown，长度: {len(md_text)}")
                
                # 保存到临时文件
                md_file = os.path.join(temp_dir, "output_with_pos.md")
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                print(f"💾 保存到: {md_file}")
                
                # 检查内容
                print("\n🔍 检查Markdown内容...")
                check_markdown_content(md_text)
                
            except TypeError as e:
                print(f"⚠️ emit_positions参数不支持: {e}")
                
                # 方法2：不使用emit_positions
                print("\n📝 方法2: 不使用emit_positions")
                md_text = to_markdown(pdf_path)
                print(f"✅ 成功生成Markdown，长度: {len(md_text)}")
                
                # 保存到临时文件
                md_file = os.path.join(temp_dir, "output_no_pos.md")
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_text)
                print(f"💾 保存到: {md_file}")
                
                # 检查内容
                print("\n🔍 检查Markdown内容...")
                check_markdown_content(md_text)
            
            # 复制临时文件到当前目录以便查看
            final_md_file = "debug_pdfllm_output.md"
            shutil.copy2(md_file, final_md_file)
            print(f"\n📋 最终输出已保存到: {final_md_file}")
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()

def check_markdown_content(md_text):
    """检查Markdown内容"""
    
    print(f"📊 Markdown总长度: {len(md_text)}")
    
    # 检查是否包含关键信息
    key_phrases = [
        "海外基金资料",
        "基金总值",
        "4.4377亿美元",
        "基金价格",
        "5.7741美元",
        "成立日期",
        "2010年8月2日",
        "基金经理",
        "Justin Kass",
        "David Oberto",
        "Michael Yee"
    ]
    
    print("\n🔍 检查关键信息:")
    found_count = 0
    for phrase in key_phrases:
        if phrase in md_text:
            print(f"✅ 找到: {phrase}")
            found_count += 1
        else:
            print(f"❌ 未找到: {phrase}")
    
    print(f"\n📈 关键信息覆盖率: {found_count}/{len(key_phrases)} ({found_count/len(key_phrases)*100:.1f}%)")
    
    # 显示前1000个字符
    print(f"\n📄 内容预览 (前1000字符):")
    print("-" * 60)
    print(md_text[:1000])
    print("-" * 60)
    
    # 检查是否包含表格结构
    if "|" in md_text:
        print("\n📋 检测到表格结构 (包含 | 字符)")
        # 查找表格行
        lines = md_text.split('\n')
        table_lines = [line for line in lines if '|' in line and line.strip()]
        print(f"📊 表格行数: {len(table_lines)}")
        
        if table_lines:
            print("📋 表格内容预览:")
            for i, line in enumerate(table_lines[:10]):  # 显示前10行
                print(f"  {i+1}: {line}")
    else:
        print("\n❌ 未检测到表格结构")

if __name__ == "__main__":
    debug_pdfllm_raw()
