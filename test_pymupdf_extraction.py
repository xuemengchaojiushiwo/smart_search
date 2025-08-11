#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用PyMuPDF测试PDF解析能力，提取带页码和坐标的完整文本
"""

import fitz  # PyMuPDF
import os

def test_pymupdf_extraction():
    """测试PyMuPDF的PDF解析能力"""
    
    pdf_path = "python_service/file/安联美元.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"🔍 使用PyMuPDF解析PDF: {pdf_path}")
    print("=" * 60)
    
    try:
        # 打开PDF
        doc = fitz.open(pdf_path)
        print(f"✅ 成功打开PDF，共 {len(doc)} 页")
        
        full_text = ""
        detailed_text = ""
        
        # 逐页处理
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            print(f"\n📄 处理第 {page_num + 1} 页...")
            
            # 提取文本
            text = page.get_text()
            print(f"   文本长度: {len(text)} 字符")
            
            # 提取带坐标的文本块
            blocks = page.get_text("dict")
            page_detailed = f"\n{'='*80}\n📄 第 {page_num + 1} 页 (带坐标信息)\n{'='*80}\n"
            
            if "blocks" in blocks:
                for block_idx, block in enumerate(blocks["blocks"]):
                    if "lines" in block:
                        for line_idx, line in enumerate(block["lines"]):
                            for span_idx, span in enumerate(line["spans"]):
                                # 提取文本和坐标
                                text_content = span["text"]
                                bbox = span["bbox"]  # [x0, y0, x1, y1]
                                font_size = span["size"]
                                font_name = span["font"]
                                
                                if text_content.strip():  # 只显示非空文本
                                    page_detailed += f"📍 块{block_idx+1}-行{line_idx+1}-段{span_idx+1} | 坐标{bbox} | 字体{font_name}({font_size:.1f}) | 文本: {text_content}\n"
            
            detailed_text += page_detailed
            
            # 检查关键信息
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
            
            found_in_page = []
            for phrase in key_phrases:
                if phrase in text:
                    found_in_page.append(phrase)
            
            if found_in_page:
                print(f"   ✅ 找到关键信息: {', '.join(found_in_page)}")
            else:
                print(f"   ❌ 未找到关键信息")
            
            # 提取表格
            try:
                tables = page.find_tables()
                if tables and hasattr(tables, '__len__'):
                    print(f"   📋 找到 {len(tables)} 个表格")
                    for i, table in enumerate(tables):
                        try:
                            table_data = table.extract()
                            print(f"     表格 {i+1}: {table_data}")
                        except Exception as e:
                            print(f"     表格 {i+1}: 提取失败 - {e}")
                else:
                    print(f"   📋 未找到表格或表格提取器不支持")
            except Exception as e:
                print(f"   📋 表格提取异常: {e}")
            
            full_text += f"\n--- 第{page_num+1}页 ---\n{text}\n"
        
        # 保存完整文本
        output_file = "pymupdf_extraction_result.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_text)
        print(f"\n💾 纯文本结果已保存到: {output_file}")
        
        # 保存详细结果（带坐标）
        detailed_output_file = "pymupdf_detailed_result.txt"
        with open(detailed_output_file, 'w', encoding='utf-8') as f:
            f.write(detailed_text)
        print(f"💾 详细结果（带坐标）已保存到: {detailed_output_file}")
        
        # 显示详细结果预览
        print(f"\n{'='*80}")
        print("📋 详细结果预览（前2000字符）:")
        print("=" * 80)
        print(detailed_text[:2000])
        print("..." if len(detailed_text) > 2000 else "")
        
        # 最终检查
        print(f"\n🔍 最终检查 - 关键信息覆盖率:")
        found_count = 0
        for phrase in key_phrases:
            if phrase in full_text:
                print(f"  ✅ {phrase}")
                found_count += 1
            else:
                print(f"  ❌ {phrase}")
        
        coverage = found_count / len(key_phrases) * 100
        print(f"\n📈 关键信息覆盖率: {found_count}/{len(key_phrases)} ({coverage:.1f}%)")
        
        if coverage >= 80:
            print("🎉 PyMuPDF解析成功！建议使用PyMuPDF替换PDFLLM")
        else:
            print("⚠️ PyMuPDF仍有遗漏，需要进一步优化")
        
        doc.close()
        
    except Exception as e:
        print(f"❌ 解析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pymupdf_extraction()
