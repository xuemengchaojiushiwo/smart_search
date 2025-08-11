#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug位置信息匹配过程的脚本
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_service'))

def debug_position_matching():
    """Debug位置信息匹配过程"""
    print("🔍 开始Debug位置信息匹配过程")
    print("=" * 60)
    
    # 检查生成的markdown文件
    debug_md_path = "debug_pdfllm_output.md"
    if not os.path.exists(debug_md_path):
        print(f"❌ 找不到debug markdown文件: {debug_md_path}")
        print("请先运行 debug_pdfllm_position.py 生成该文件")
        return
    
    print(f"📁 找到debug markdown文件: {debug_md_path}")
    
    # 读取markdown内容
    with open(debug_md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    print(f"📝 Markdown文件长度: {len(md_content)}")
    
    # 查找所有位置标签
    import re
    pos_pattern = r'<sub>pos: page=(\d+), bbox=([\d.,]+)</sub>'
    pos_matches = re.findall(pos_pattern, md_content)
    
    print(f"🔍 找到 {len(pos_matches)} 个位置标签")
    
    # 显示前10个位置标签
    print("\n📋 前10个位置标签:")
    for i, (page, bbox) in enumerate(pos_matches[:10]):
        bbox_parts = [float(x) for x in bbox.split(',')]
        print(f"   {i}: page={page}, bbox={bbox_parts}")
    
    # 检查parse_md_with_pos的结果
    try:
        from python_service.md_pos_to_aligned import parse_md_with_pos
        items = parse_md_with_pos(debug_md_path)
        print(f"\n📊 parse_md_with_pos 解析出 {len(items)} 个项目")
        
        # 显示前5个items的详细信息
        print("\n📋 前5个items的详细信息:")
        for i, item in enumerate(items[:5]):
            print(f"   📋 项目 {i}:")
            if isinstance(item, dict):
                for key, value in item.items():
                    print(f"     {key}: {value}")
            print()
        
        # 模拟分块过程
        print("\n🔍 模拟分块过程:")
        from langchain.text_splitter import MarkdownHeaderTextSplitter
        
        markdown_headers = [
            ("#", "标题1"),
            ("##", "标题2"), 
            ("###", "标题3"),
            ("####", "标题4"),
            ("#####", "标题5"),
            ("######", "标题6"),
        ]
        
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=markdown_headers)
        chunks = splitter.split_text(md_content)
        print(f"   ✅ 分块成功，生成 {len(chunks)} 个chunks")
        
        # 测试位置信息匹配
        print("\n🔍 测试位置信息匹配:")
        for i, chunk in enumerate(chunks[:3]):
            chunk_content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            chunk_text = chunk_content[:100]  # 取前100字符作为标识
            print(f"   📋 Chunk {i}:")
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
                page_num = best_match.get('page_num', -1)
                bbox = best_match.get('bbox_union', [])
                print(f"     ✅ 找到匹配: page={page_num}, bbox={bbox}, score={best_score:.2f}")
                
                # 检查bbox是否为空
                if bbox:
                    print(f"     📍 bbox有效: {bbox}")
                else:
                    print(f"     ❌ bbox为空")
            else:
                print(f"     ❌ 未找到匹配")
            print()
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 Debug完成！")
    print("=" * 60)

if __name__ == "__main__":
    debug_position_matching()
