#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 切分策略：确保大块与小块完全匹配
基于 PDF 原生块结构进行智能切分，避免跨块切割
"""

import fitz
from typing import List, Dict, Tuple, Any
import re
import logging

logger = logging.getLogger(__name__)

def extract_pdf_blocks_with_positions(doc: fitz.Document, filename: str) -> List[Dict]:
    """
    从PDF提取原生块结构，每个块包含完整的文本和位置信息
    返回: List[Dict] 每个元素包含:
    - content: 块文本
    - page: 页码
    - block_idx: 块索引
    - bbox: 块边界框
    - positions: 该块内所有span的位置信息
    - mini_chunks: 该块内的行级小块
    """
    blocks = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_blocks = page.get_text("dict")
        
        if "blocks" not in page_blocks:
            continue
            
        for block_idx, block in enumerate(page_blocks["blocks"]):
            if "lines" not in block:
                continue
                
            # 收集整个块的所有文本和位置信息
            block_text = ""
            block_positions = []
            line_texts = []
            
            for line_idx, line in enumerate(block["lines"]):
                line_text = ""
                line_positions = []
                
                for span_idx, span in enumerate(line["spans"]):
                    text = span["text"].strip()
                    if text:
                        line_text += text + " "
                        line_positions.append({
                            "text": text,
                            "bbox": span["bbox"],
                            "font_size": span["size"],
                            "font": span["font"],
                            "span_idx": span_idx,
                            "line_idx": line_idx,
                            "page": page_num + 1,
                            "block_idx": block_idx,
                        })
                
                if line_text.strip():
                    line_texts.append(line_text.strip())
                    block_text += line_text.strip() + "\n"
                    block_positions.extend(line_positions)
            
            if block_text.strip():
                # 计算整个块的边界框
                if block_positions:
                    x0 = min(p["bbox"][0] for p in block_positions)
                    y0 = min(p["bbox"][1] for p in block_positions)
                    x1 = max(p["bbox"][2] for p in block_positions)
                    y1 = max(p["bbox"][3] for p in block_positions)
                    block_bbox = [x0, y0, x1, y1]
                else:
                    block_bbox = [0, 0, 0, 0]
                
                # 生成该块的行级小块
                mini_chunks = _generate_mini_chunks_from_block(block_positions, line_texts)
                
                blocks.append({
                    "content": block_text.strip(),
                    "page": page_num + 1,
                    "block_idx": block_idx,
                    "bbox": block_bbox,
                    "positions": block_positions,
                    "mini_chunks": mini_chunks,
                    "line_count": len(line_texts),
                    "char_count": len(block_text.strip())
                })
    
    return blocks

def _generate_mini_chunks_from_block(positions: List[Dict], line_texts: List[str]) -> List[Dict]:
    """
    从单个PDF块生成语义级小块
    将相关的行合并成语义单元，避免过度切分
    """
    mini_chunks = []
    
    # 按行分组位置信息
    line_groups = {}
    for pos in positions:
        line_key = (pos.get("page", 1), pos.get("block_idx", -1), pos.get("line_idx", -1))
        line_groups.setdefault(line_key, []).append(pos)
    
    # 智能合并相关行，避免过度切分
    current_lines = []
    current_positions = []
    current_line_indices = []
    
    for line_idx, line_text in enumerate(line_texts):
        line_key = None
        for key in line_groups.keys():
            if key[2] == line_idx:  # 匹配行索引
                line_key = key
                break
        
        if not line_key or line_key not in line_groups:
            continue
            
        line_positions = line_groups[line_key]
        if not line_text.strip() or not line_positions:
            continue
            
        # 检查是否应该开始新的语义单元
        should_start_new = (
            not current_lines or  # 第一个非空行
            _should_start_new_semantic_unit(current_lines[-1], line_text) or  # 语义分割
            len('\n'.join(current_lines)) > 200  # 长度限制减小到200，确保mini-chunk不会太大
        )
        
        if should_start_new and current_lines:
            # 保存当前语义单元
            mini_chunks.append(_create_mini_chunk_from_lines(
                current_lines, current_positions, current_line_indices
            ))
            current_lines = []
            current_positions = []
            current_line_indices = []
        
        # 添加当前行
        current_lines.append(line_text)
        current_positions.extend(line_positions)
        current_line_indices.append(line_idx)
    
    # 添加最后一个语义单元
    if current_lines:
        mini_chunks.append(_create_mini_chunk_from_lines(
            current_lines, current_positions, current_line_indices
        ))
    
    return mini_chunks

def _should_start_new_semantic_unit(prev_line: str, current_line: str) -> bool:
    """判断是否应该开始新的语义单元"""
    # 如果前一行以冒号结尾，当前行很可能是值，应该合并
    if prev_line.strip().endswith(':') or prev_line.strip().endswith('：'):
        return False
    
    # 如果当前行是标题或分隔符，应该分开
    if (current_line.strip().startswith('**') or 
        current_line.strip().startswith('##') or
        len(current_line.strip()) < 6):  # 减少到6，让更多短行合并在一起
        return True
    
    # 如果前一行很长，当前行很短，可能是标题
    if len(prev_line) > 50 and len(current_line) < 20:
        return True
    
    return False

def _create_mini_chunk_from_lines(lines: List[str], positions: List[Dict], line_indices: List[int]) -> Dict:
    """从多行创建一个小块"""
    combined_text = '\n'.join(lines)
    
    if not positions:
        return {
            "text": combined_text,
            "page": 1,
            "bbox": [0, 0, 0, 0],
            "block_idx": -1,
            "line_idx": line_indices[0] if line_indices else 0,
            "char_start": 0,
            "char_end": len(combined_text)
        }
    
    # 计算合并后的边界框
    x0 = min(p["bbox"][0] for p in positions)
    y0 = min(p["bbox"][1] for p in positions)
    x1 = max(p["bbox"][2] for p in positions)
    y1 = max(p["bbox"][3] for p in positions)
    
    return {
        "text": combined_text,
        "page": positions[0].get("page", 1),
        "bbox": [x0, y0, x1, y1],
        "block_idx": positions[0].get("block_idx", -1),
        "line_idx": line_indices[0] if line_indices else 0,
        "char_start": 0,
        "char_end": len(combined_text)
    }

def smart_merge_blocks(blocks: List[Dict], max_chunk_size: int = 1000, overlap: int = 200) -> List[Dict]:
    """
    智能合并PDF块，确保大块和小块完全匹配
    策略：
    1. 优先保持PDF原生块完整
    2. 如果单个块过大，按行切分
    3. 如果块过小，合并相邻块
    """
    merged_chunks = []
    current_chunk = None
    
    for block in blocks:
        block_size = len(block["content"])
        
        if current_chunk is None:
            # 开始新块
            current_chunk = {
                "content": block["content"],
                "page": block["page"],
                "block_idx": block["block_idx"],
                "bbox": block["bbox"],
                "positions": block["positions"].copy(),
                "mini_chunks": block["mini_chunks"].copy(),
                "source_blocks": [block["block_idx"]],
                "char_count": block_size
            }
        else:
            # 检查是否可以合并
            combined_size = current_chunk["char_count"] + block_size
            
            if combined_size <= max_chunk_size:
                # 可以合并
                current_chunk["content"] += "\n" + block["content"]
                current_chunk["positions"].extend(block["positions"])
                current_chunk["mini_chunks"].extend(block["mini_chunks"])
                current_chunk["source_blocks"].append(block["block_idx"])
                current_chunk["char_count"] = combined_size
                
                # 更新边界框
                if block["bbox"] and current_chunk["bbox"]:
                    x0 = min(current_chunk["bbox"][0], block["bbox"][0])
                    y0 = min(current_chunk["bbox"][1], block["bbox"][1])
                    x1 = max(current_chunk["bbox"][2], block["bbox"][2])
                    y1 = max(current_chunk["bbox"][3], block["bbox"][3])
                    current_chunk["bbox"] = [x0, y0, x1, y1]
            else:
                # 不能合并，保存当前块并开始新块
                merged_chunks.append(current_chunk)
                current_chunk = {
                    "content": block["content"],
                    "page": block["page"],
                    "block_idx": block["block_idx"],
                    "bbox": block["bbox"],
                    "positions": block["positions"].copy(),
                    "mini_chunks": block["mini_chunks"].copy(),
                    "source_blocks": [block["block_idx"]],
                    "char_count": block_size
                }
    
    # 添加最后一个块
    if current_chunk:
        merged_chunks.append(current_chunk)
    
    return merged_chunks

def split_oversized_blocks(chunks: List[Dict], max_chunk_size: int = 1000) -> List[Dict]:
    """
    处理超大块：按行切分，保持小块完整性
    """
    result_chunks = []
    
    for chunk in chunks:
        if chunk["char_count"] <= max_chunk_size:
            result_chunks.append(chunk)
            continue
        
        # 按行切分超大块
        lines = chunk["content"].split('\n')
        mini_chunks = chunk["mini_chunks"]
        
        current_lines = []
        current_mini_chunks = []
        current_size = 0
        
        for i, line in enumerate(lines):
            line_size = len(line)
            
            if current_size + line_size > max_chunk_size and current_lines:
                # 保存当前块
                result_chunks.append({
                    "content": '\n'.join(current_lines),
                    "page": chunk["page"],
                    "block_idx": chunk["block_idx"],
                    "bbox": _calculate_bbox_from_mini_chunks(current_mini_chunks),
                    "positions": _extract_positions_for_lines(current_mini_chunks, chunk["positions"]),
                    "mini_chunks": current_mini_chunks.copy(),
                    "source_blocks": chunk["source_blocks"],
                    "char_count": current_size
                })
                
                # 重置
                current_lines = [line]
                current_mini_chunks = [mini_chunks[i]] if i < len(mini_chunks) else []
                current_size = line_size
            else:
                current_lines.append(line)
                if i < len(mini_chunks):
                    current_mini_chunks.append(mini_chunks[i])
                current_size += line_size
        
        # 添加最后一个块
        if current_lines:
            result_chunks.append({
                "content": '\n'.join(current_lines),
                "page": chunk["page"],
                "block_idx": chunk["block_idx"],
                "bbox": _calculate_bbox_from_mini_chunks(current_mini_chunks),
                "positions": _extract_positions_for_lines(current_mini_chunks, chunk["positions"]),
                "mini_chunks": current_mini_chunks,
                "source_blocks": chunk["source_blocks"],
                "char_count": current_size
            })
    
    return result_chunks

def _calculate_bbox_from_mini_chunks(mini_chunks: List[Dict]) -> List[float]:
    """从mini_chunks计算边界框"""
    if not mini_chunks:
        return [0, 0, 0, 0]
    
    x0 = min(mc["bbox"][0] for mc in mini_chunks)
    y0 = min(mc["bbox"][1] for mc in mini_chunks)
    x1 = max(mc["bbox"][2] for mc in mini_chunks)
    y1 = max(mc["bbox"][3] for mc in mini_chunks)
    
    return [x0, y0, x1, y1]

def _extract_positions_for_lines(mini_chunks: List[Dict], all_positions: List[Dict]) -> List[Dict]:
    """根据mini_chunks提取对应的positions"""
    if not mini_chunks:
        return []
    
    # 获取mini_chunks覆盖的行范围
    line_indices = {mc["line_idx"] for mc in mini_chunks}
    
    # 过滤positions
    filtered_positions = []
    for pos in all_positions:
        if pos.get("line_idx") in line_indices:
            filtered_positions.append(pos)
    
    return filtered_positions

def process_pdf_with_matched_chunks(doc: fitz.Document, filename: str, 
                                  max_chunk_size: int = 500, 
                                  overlap: int = 100) -> List[Dict]:
    """
    处理PDF并生成完全匹配的大块和小块
    返回格式与原有Document.metadata兼容
    """
    # 1. 提取PDF原生块
    blocks = extract_pdf_blocks_with_positions(doc, filename)
    
    # 2. 智能合并块
    merged_chunks = smart_merge_blocks(blocks, max_chunk_size, overlap)
    
    # 3. 处理超大块
    final_chunks = split_oversized_blocks(merged_chunks, max_chunk_size)
    
    # 4. 转换为Document格式
    from langchain.schema import Document
    
    documents = []
    for i, chunk in enumerate(final_chunks):
        # 更新mini_chunks中的字符位置
        _update_char_positions_in_mini_chunks(chunk["mini_chunks"], chunk["content"])
        
        doc = Document(
            page_content=chunk["content"],
            metadata={
                "source_file": filename,
                "page_num": chunk["page"],
                "chunk_index": i,
                "positions": chunk["positions"],
                "bbox": chunk["bbox"],
                "mini_chunks": chunk["mini_chunks"],
                "source_blocks": chunk["source_blocks"],
                "document_type": "文档"
            }
        )
        documents.append(doc)
    
    return documents

def _update_char_positions_in_mini_chunks(mini_chunks: List[Dict], full_content: str):
    """更新mini_chunks中的字符位置信息"""
    current_pos = 0
    for mc in mini_chunks:
        text = mc["text"]
        # 在完整内容中查找该文本的位置
        pos = full_content.find(text, current_pos)
        if pos != -1:
            mc["char_start"] = pos
            mc["char_end"] = pos + len(text)
            current_pos = pos + len(text)
        else:
            mc["char_start"] = current_pos
            mc["char_end"] = current_pos + len(text)
            current_pos += len(text)
