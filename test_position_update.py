#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试位置信息更新是否成功的脚本
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'python_service'))

def test_position_update():
    """测试位置信息更新是否成功"""
    print("🧪 测试位置信息更新是否成功")
    print("=" * 60)
    
    # 检查生成的markdown文件
    debug_md_path = "debug_pdfllm_output.md"
    if not os.path.exists(debug_md_path):
        print(f"❌ 找不到debug markdown文件: {debug_md_path}")
        print("请先运行 debug_pdfllm_position.py 生成该文件")
        return
    
    print(f"📁 找到debug markdown文件: {debug_md_path}")
    
    try:
        from python_service.md_pos_to_aligned import parse_md_with_pos
        from langchain.text_splitter import MarkdownHeaderTextSplitter
        from langchain.schema import Document
        
        # 读取markdown内容
        with open(debug_md_path, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        print(f"📝 Markdown文件长度: {len(md_content)}")
        
        # 解析位置信息
        items = parse_md_with_pos(debug_md_path)
        print(f"📊 parse_md_with_pos 解析出 {len(items)} 个项目")
        
        # 分块
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
        print(f"✅ 分块成功，生成 {len(chunks)} 个chunks")
        
        # 测试位置信息匹配和更新
        print("\n🔍 测试位置信息匹配和更新:")
        for i, chunk in enumerate(chunks[:3]):
            chunk_content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            chunk_text = chunk_content[:100]  # 取前100字符作为标识
            print(f"\n📋 Chunk {i}:")
            print(f"   标识文本: {chunk_text}")
            
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
                print(f"   ✅ 找到匹配: page={page_num}, bbox={bbox}, score={best_score:.2f}")
                
                # 更新chunk的metadata
                chunk.metadata.update({
                    "page_num": page_num,
                    "bbox_union": bbox,
                    "char_start": 0,
                    "char_end": len(chunk_content)
                })
                print(f"   📝 已更新metadata: page_num={chunk.metadata.get('page_num')}, bbox_union={chunk.metadata.get('bbox_union')}")
            else:
                print(f"   ❌ 未找到匹配")
        
        # 验证metadata是否正确更新
        print("\n🔍 验证metadata是否正确更新:")
        for i, chunk in enumerate(chunks[:3]):
            print(f"   📋 Chunk {i}:")
            print(f"     page_num: {chunk.metadata.get('page_num', 'N/A')}")
            print(f"     bbox_union: {chunk.metadata.get('bbox_union', 'N/A')}")
            print(f"     char_start: {chunk.metadata.get('char_start', 'N/A')}")
            print(f"     char_end: {chunk.metadata.get('char_end', 'N/A')}")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🎉 测试完成！")
    print("=" * 60)

if __name__ == "__main__":
    test_position_update()
