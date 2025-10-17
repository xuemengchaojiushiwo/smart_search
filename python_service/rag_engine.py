#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG引擎模块
"""

import logging
import json
from typing import List, Dict, Optional, Any

try:
    from .models import ChatResponse, KnowledgeReference
    from .utils import clean_json_from_answer, parse_used_mc_ids, fallback_keyword_matching
    from .es_client import get_embedding, search_es_chunks
    from .ai_client_manager import get_ai_manager
except ImportError:
    # 当直接运行时使用绝对导入
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from models import ChatResponse, KnowledgeReference
    from utils import clean_json_from_answer, parse_used_mc_ids, fallback_keyword_matching
    from es_client import get_embedding, search_es_chunks
    from ai_client_manager import get_ai_manager

logger = logging.getLogger(__name__)


def condense_question_with_llm(question: str, max_length: int = 1500) -> str:
    """
    使用大模型浓缩过长的问题
    
    Args:
        question: 原始问题
        max_length: 目标最大长度
        
    Returns:
        浓缩后的问题，如果失败则返回None
    """
    try:
        # 获取AI管理器
        manager = get_ai_manager()
        
        # 构建浓缩提示
        condense_prompt = f"""
请将以下问题浓缩为不超过{max_length}个字符的简洁版本，保留关键信息和查询意图。
不要改变问题的本质和核心需求，只需要使其更简洁。

原问题: {question}

浓缩后的问题(不超过{max_length}字符):
"""
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的文本浓缩助手，擅长保留文本核心含义的同时减少字符数量。"
            },
            {
                "role": "user", 
                "content": condense_prompt
            }
        ]
        
        # 调用管理器的chat_completion方法
        logger.info(f"[DEBUG] 通过AI管理器发送问题浓缩请求, 当前API: {manager.get_current_api()}")
        result = manager.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=1500
        )
        
        # 检查结果
        if "error" in result:
            logger.error(f"[DEBUG] 问题浓缩失败: {result['error']}")
            return None
        
        # 提取浓缩后的问题
        if "choices" in result and len(result["choices"]) > 0:
            condensed = result["choices"][0]["message"]["content"]
            # 清理可能的引号和多余空格
            condensed = condensed.strip().strip('"\'').strip()
            logger.info(f"[DEBUG] 问题浓缩成功: 原长度={len(question)}, 新长度={len(condensed)}")
            return condensed
        else:
            logger.error(f"[DEBUG] 问题浓缩API响应格式异常: {result}")
            return None
            
    except Exception as e:
        logger.error(f"[DEBUG] 问题浓缩失败: {e}")
        return None


def generate_ai_answer(prompt: str) -> str:
    """
    通过AI管理器调用大模型生成答案
    """
    try:
        # 获取AI管理器
        manager = get_ai_manager()
        
        # 构建消息
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的文档知识助手，请基于提供的文档信息准确回答问题。"
            },
            {
                "role": "user", 
                "content": prompt
            }
        ]
        
        # 调试：打印请求负载
        logger.info(f"[DEBUG] 调用大模型的请求负载: {json.dumps(messages, ensure_ascii=False)[:200]}...")
        
        # 调用管理器的chat_completion方法
        logger.info(f"[DEBUG] 通过AI管理器发送请求到大模型API, 当前API: {manager.get_current_api()}")
        result = manager.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=1000
        )
        
        # 检查结果
        if "error" in result:
            logger.error(f"[DEBUG] 大模型API调用失败: {result['error']}")
            return f"抱歉，生成答案时出现错误：{result['error']}，请重试。"
        
        # 提取答案
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
            logger.info(f"[DEBUG] 大模型返回答案长度: {len(answer)}")
            return answer
        else:
            logger.error(f"[DEBUG] API响应格式异常: {result}")
            return "抱歉，生成答案时出现格式错误，请重试。"
            
    except Exception as e:
        logger.error(f"[DEBUG] 生成AI答案失败: {e}")
        return f"抱歉，生成答案时出现错误：{str(e)}，请重试。"


def build_enhanced_rag_prompt_with_mini_chunks(question: str, context_chunks: List[Dict]) -> str:
    """
    构建增强的RAG提示词，包含小块清单供模型选择
    """
    context_parts = []
    mini_chunks_list = []
    
    for i, chunk in enumerate(context_chunks):
        metadata = chunk['metadata']
        
        # 构建每个chunk的详细上下文信息
        chunk_context = f"""
📄 引用 {i+1}:
📋 文档: {metadata.get('document_name', 'N/A')}
📄 页码: {metadata.get('page_num', 'N/A')}
📝 内容: {chunk.get('content', '')}
"""
        context_parts.append(chunk_context)
        
        # 收集该chunk的所有mini_chunks
        for mc in metadata.get('mini_chunks', []):
            text = mc.get('text', '').strip()
            if text and len(text) <= 160:  # 限制文本长度
                mini_chunks_list.append(f"- [{mc.get('mc_id')}] {text}")
    
    # 限制mini_chunks数量，但优先保留包含问题关键词的mini_chunks
    if len(mini_chunks_list) > 120:
        # 提取问题中的关键词
        import re
        keywords = []
        if re.search(r'[\u4e00-\u9fff]', question):
            # 中文关键词提取
            chinese_keywords = ['基金', '总值', '价值', '净值', '资产', '规模', '金额', '美元', '投资', '债券', '除息', '价格', '派息', '股息', '收益率']
            for kw in chinese_keywords:
                if kw in question:
                    keywords.append(kw)
        else:
            # 英文关键词提取
            words = re.findall(r'\b\w+\b', question.lower())
            keywords = [w for w in words if len(w) > 2]
        
        # 优先保留包含关键词的mini_chunks
        priority_chunks = []
        other_chunks = []
        
        for item in mini_chunks_list:
            is_priority = False
            for keyword in keywords:
                if keyword.lower() in item.lower():
                    is_priority = True
                    break
            
            if is_priority:
                priority_chunks.append(item)
            else:
                other_chunks.append(item)
        
        # 合并：优先chunks + 其他chunks，总共120个
        mini_chunks_list = priority_chunks + other_chunks[:120-len(priority_chunks)]
    
    # 构建完整提示
    prompt = f"""
你是一个专业的文档知识助手。请基于以下信息回答问题。

每个引用都包含了完整的文档信息，包括：
- 文档名称和类型
- 页码和块序
- 相关性评分和位置坐标
- 具体内容

请仔细分析这些信息，并根据问题找到最准确的答案。

问题: {question}

参考信息:
{''.join(context_parts)}

可用的精确文本片段（MiniChunks）:
{chr(10).join(mini_chunks_list)}

请根据问题，从上述信息中找到最准确的答案。要求：
1. 直接回答问题，不要说"请查看引用信息"
2. 如果问题涉及特定文档，请确保答案来自正确的文档
3. 如果问题没有指定具体文档，请基于所有相关信息给出综合回答
4. 答案要具体、准确，包含关键数据
5. 用中文回答，并说明信息来源（如"根据文档第X页"）
6. 如果提供的文档中完全没有与问题相关的信息，请明确说明"文档中未提及相关内容"或"未找到相关信息"
7. 在回答末尾，请返回一个JSON格式的响应，包含你实际使用的小块ID（按相关性从高到低排序）：
   {{"used_mc_ids": ["30:page_num:chunk_index:mini_chunk_index", ...]}}
   
   注意：请将最相关的小块ID放在数组的前面，这样系统会优先使用最相关的小块进行高亮显示。
   如果文档中没有相关信息，used_mc_ids应该为空数组[]。

请开始回答：
"""
    
    return prompt


def build_enhanced_rag_prompt(question: str, context_chunks: List[Dict]) -> str:
    """
    构建增强的RAG提示词，让大模型能看到完整的上下文信息
    """
    context_parts = []
    
    for i, chunk in enumerate(context_chunks):
        metadata = chunk['metadata']
        
        # 构建每个chunk的详细上下文信息
        chunk_context = f"""
=== 引用 {i+1} ===
📄 文档名称: {metadata.get('document_name', 'N/A')}
📋 文档类型: {metadata.get('document_type', 'N/A')}
📖 页码: {metadata.get('page_num', 'N/A')}
🔢 块序: {metadata.get('chunk_index', 'N/A')}
🎯 相关性: {metadata.get('relevance_score', 'N/A')}
📍 坐标: {metadata.get('bbox', [])}
📝 内容: {chunk.get('content', '')}
"""
        context_parts.append(chunk_context)
    
    # 构建完整提示
    prompt = f"""
你是一个专业的文档知识助手。请基于以下信息回答问题。

每个引用都包含了完整的文档信息，包括：
- 文档名称和类型
- 页码和块序
- 相关性评分和位置坐标
- 具体内容

请仔细分析这些信息，并根据问题找到最准确的答案。

问题: {question}

参考信息:
{''.join(context_parts)}

请根据问题，从上述信息中找到最准确的答案。要求：
1. 直接回答问题，不要说"请查看引用信息"
2. 如果问题涉及特定文档，请确保答案来自正确的文档
3. 如果问题没有指定具体文档，请基于所有相关信息给出综合回答
4. 答案要具体、准确，包含关键数据
5. 用中文回答，并说明信息来源（如"根据文档第X页"）
6. 如果提供的文档中完全没有与问题相关的信息，请明确说明"文档中未提及相关内容"或"未找到相关信息"

请开始回答：
"""
    
    return prompt


def chat_with_rag(question: str, user_id: str, source_file: Optional[str] = None, workspace: Optional[str] = None) -> ChatResponse:
    """
    基于知识库的智能问答
    """
    logger.info(f"RAG聊天请求: {question}")
    logger.info(f"接收到的参数: source_file={source_file}, workspace={workspace}")
    
    try:
        # 1. 向量搜索找到相关chunks
        logger.info(f"[DEBUG] 开始生成问题embedding: question={question}")
        # 检查问题长度，确保不超过token限制
        MAX_QUESTION_LENGTH = 1500  # 安全阈值，避免超过512 tokens
        question_text = question
        if len(question_text) > MAX_QUESTION_LENGTH:
            logger.warning(f"问题长度({len(question_text)})超过限制({MAX_QUESTION_LENGTH})，将使用大模型浓缩")
            # 使用大模型浓缩问题而不是直接截取
            condensed_question = condense_question_with_llm(question_text)
            if condensed_question:
                question_text = condensed_question
                logger.info(f"浓缩后长度: {len(question_text)}")
            else:
                logger.warning(f"浓缩失败，使用原问题")
        
        question_embedding = get_embedding(question_text)
        if question_embedding:
            logger.info(f"[DEBUG] 问题embedding生成成功: 维度={len(question_embedding)}, 前5个值={question_embedding[:5]}")
        else:
            logger.error("[DEBUG] 无法获取问题的embedding向量")
            return ChatResponse(
                answer="抱歉，无法生成问题的向量表示，请重试。",
                references=[],
                session_id=user_id
            )
        
        # 构建过滤条件 - 同时搜索内容块和元数据块
        filters = [
            {"terms": {"chunk_type": ["content", "metadata"]}}  # 搜索内容类型和元数据类型的chunk
        ]
        
        # 如果指定了工作空间，则按工作空间过滤
        if workspace:
            logger.info(f"按工作空间过滤RAG检索: {workspace}")
            # 支持多个工作空间，用逗号分隔
            workspaces = [w.strip() for w in workspace.split(",") if w.strip()]
            if workspaces:
                if len(workspaces) == 1:
                    filters.append({"term": {"workspaces.keyword": workspaces[0]}})
                else:
                    filters.append({"terms": {"workspaces.keyword": workspaces}})
        # 如果指定了特定文件，则只检索该文件的chunks
        elif source_file:
            logger.info(f"按文件名过滤RAG检索: {source_file}")
            filters.append({"term": {"source_file": source_file}})
        
        # 简化搜索逻辑 - 直接返回语义相似度最高的chunks
        # 仅检索包含embedding字段的文档，避免脚本在缺失字段时报错
        size = 10 if source_file else 5  # 针对特定文件时返回更多chunks
        
        # 执行ES搜索
        logger.info(f"[DEBUG] 执行ES搜索")
        search_results = search_es_chunks(question_embedding, filters, size)
        
        if search_results:
            logger.info(f"[DEBUG] ES搜索成功: 找到{len(search_results)}个结果")
            # 打印前3个结果的相似度分数
            for i, result in enumerate(search_results[:3]):
                source = result['source']
                score = result['score']
                logger.info(f"[DEBUG] 结果{i+1}: knowledge_id={source.get('knowledge_id')}, 相似度={score}, 文件={source.get('source_file')}")
                logger.info(f"[DEBUG] 内容片段: {source.get('content', '')[:100]}...")
        else:
            logger.info("[DEBUG] ES搜索失败: 未找到相关知识块")
            return ChatResponse(
                answer="抱歉，在知识库中没有找到相关信息。",
                references=[],
                session_id=user_id
            )
        
        # 2. 构建增强的上下文信息，为每个mini_chunk生成mc_id
        context_chunks = []
        mcid_to_entry: Dict[str, Dict] = {}
        
        for result in search_results:
            source = result['source']
            score = result['score']
            
            # 为mini_chunks添加mc_id
            mini_chunks_with_id = []
            for idx, mc in enumerate(source.get('mini_chunks', [])):
                mc_id = f"{source.get('knowledge_id', 0)}:{source.get('page_num', 0)}:{source.get('chunk_index', 0)}:{idx}"
                mc_with_id = {**mc, "mc_id": mc_id}
                mini_chunks_with_id.append(mc_with_id)
                
                # 建立全局映射
                mcid_to_entry[mc_id] = {
                    "mc_id": mc_id,
                    "page": mc.get("page"),
                    "bbox": mc.get("bbox", []),
                    "text": mc.get("text", ""),
                    "char_start": mc.get("char_start", 0),
                    "char_end": mc.get("char_end", 0),
                    "knowledge_id": source.get('knowledge_id', 0),
                    "chunk_index": source.get('chunk_index', 0)
                }
            
            # 构建每个chunk的完整上下文信息
            chunk_info = {
                "content": source.get('content', ''),
                "metadata": {
                    "knowledge_id": source.get('knowledge_id', 0),
                    "knowledge_name": source.get('knowledge_name', ''),
                    "description": source.get('description', ''),
                    "tags": source.get('tags', ''),
                    "effective_time": source.get('effective_time', ''),
                    "document_name": source.get('source_file', 'N/A'),
                    "document_type": "文档",  # 通用文档类型
                    "page_num": source.get('page_num', 'N/A'),
                    "chunk_index": source.get('chunk_index', 'N/A'),
                    "bbox": source.get('bbox', []),
                    "positions": source.get('positions', []),
                    "mini_chunks": mini_chunks_with_id,
                    "relevance_score": round(score, 3)
                }
            }
            context_chunks.append(chunk_info)
            logger.info(f"从ES获取的mini_chunks数量: {len(mini_chunks_with_id)}")
        
        # 调试：显示映射的mc_ids
        logger.info(f"构建的mcid_to_entry映射数量: {len(mcid_to_entry)}")
        if mcid_to_entry:
            sample_mc_ids = list(mcid_to_entry.keys())[:5]
            logger.info(f"映射中的示例mc_ids: {sample_mc_ids}")
        
        # 3. 构建增强的RAG提示词（包含小块清单）
        logger.info("[DEBUG] 开始构建RAG提示词")
        enhanced_prompt = build_enhanced_rag_prompt_with_mini_chunks(question, context_chunks)
        logger.info(f"[DEBUG] RAG提示词长度: {len(enhanced_prompt)}")
        logger.info(f"[DEBUG] RAG提示词前200字符: {enhanced_prompt[:200]}...")
        
        # 4. 调用大模型生成答案
        logger.info("[DEBUG] 开始调用大模型生成答案")
        answer = generate_ai_answer(enhanced_prompt)
        logger.info(f"模型回答长度: {len(answer)}")
        logger.info(f"模型回答前1500字符: {answer[:1500]}")
        
        # 4.1 解析模型返回的 used_mc_ids（在清理答案之前）
        used_mc_ids = parse_used_mc_ids(answer)
        
        # 4.2 检查AI是否明确表示无法从文档中找到相关信息
        no_relevant_info_keywords = [
            "文档中未提及", "未涉及", "未找到", "没有相关信息", "无法从文档中", 
            "文档中没有", "未包含", "未提供", "无法找到", "没有找到",
            "文档中未明确", "未在文中", "文中未", "文档未", "未在文档中"
        ]
        
        # 检查AI回答是否包含"无法找到相关信息"的表述
        answer_lower = answer.lower()
        has_no_relevant_info = any(keyword in answer_lower for keyword in no_relevant_info_keywords)
        
        if has_no_relevant_info:
            logger.info("AI明确表示无法从文档中找到相关信息，将返回空引用")
            # 清理答案中的JSON信息
            cleaned_answer = clean_json_from_answer(answer)
            return ChatResponse(
                answer=cleaned_answer,
                references=[],  # 返回空引用
                session_id=user_id
            )
        
        # 4.3 清理答案中的JSON格式信息，只保留纯文本回答
        answer = clean_json_from_answer(answer)
        
        logger.info(f"模型返回 used_mc_ids 数量: {len(used_mc_ids)}")
        if used_mc_ids:
            logger.info(f"解析到的 mc_ids: {used_mc_ids[:5]}")  # 只显示前5个
            # 检查这些mc_ids是否在映射中存在
            valid_mc_ids = []
            for mc_id in used_mc_ids:
                if mc_id in mcid_to_entry:
                    valid_mc_ids.append(mc_id)
                else:
                    logger.warning(f"mc_id {mc_id} 在映射中不存在")
            logger.info(f"有效的 mc_ids 数量: {len(valid_mc_ids)}")
            used_mc_ids = valid_mc_ids
        else:
            # 兜底策略：基于关键词匹配选择相关小块
            logger.info("模型未返回JSON，使用关键词匹配兜底策略")
            used_mc_ids = fallback_keyword_matching(question, mcid_to_entry)
            logger.info(f"兜底策略找到 {len(used_mc_ids)} 个相关小块")
        
        # 5. 基于模型选择的mc_ids构建引用信息
        references = []
        
        # 先基于 used_mc_ids 整理每个 chunk 的高亮条目
        chunk_key_to_highlights: Dict[tuple, List[Dict]] = {}
        for mcid in used_mc_ids:
            entry = mcid_to_entry.get(mcid)
            if not entry:
                continue
            key = (entry.get("knowledge_id"), entry.get("chunk_index"))
            chunk_key_to_highlights.setdefault(key, []).append({
                "mc_id": entry["mc_id"],
                "page": entry.get("page"),
                "bbox": entry.get("bbox", []),
                "text": entry.get("text", ""),
                "char_start": entry.get("char_start", 0),
                "char_end": entry.get("char_end", 0),
            })
        
        # 设置相似度阈值，过滤掉相似度过低的块
        SIMILARITY_THRESHOLD = 1.2  # 进一步降低阈值，确保更多chunk能通过
        
        # 优先选择有mini-chunks的chunk，即使相似度稍低
        # 先检查是否需要重新处理PDF文件
        need_reprocess = False
        for chunk in context_chunks:
            metadata = chunk['metadata']
            mini_chunks = metadata.get('mini_chunks', [])
            if not mini_chunks:
                knowledge_id = metadata.get('knowledge_id')
                logger.info(f"检测到知识ID为{knowledge_id}的chunk {metadata.get('chunk_index')} 没有mini-chunks，可能需要重新处理PDF")
                need_reprocess = True
                break
        
        if need_reprocess:
            logger.warning("检测到PDF没有正确生成mini-chunks，请考虑重新上传文件或重启服务")
            
        chunks_with_mini_chunks = []
        chunks_without_mini_chunks = []
        
        for chunk in context_chunks:
            metadata = chunk['metadata']
            relevance_score = metadata.get('relevance_score', 0.0)
            
            # 打印相似度信息
            logger.info(f"Chunk {metadata.get('chunk_index')} 相似度: {relevance_score:.4f}, 文档: {metadata.get('document_name', 'N/A')}")
            
            # 过滤相似度过低的块
            if relevance_score < SIMILARITY_THRESHOLD:
                logger.info(f"Chunk {metadata.get('chunk_index')} 相似度过低 ({relevance_score:.4f} < {SIMILARITY_THRESHOLD})，跳过")
                continue
            
            # 检查是否有mini-chunks
            key = (metadata.get('knowledge_id', 0), metadata.get('chunk_index', 0))
            hl_for_chunk = chunk_key_to_highlights.get(key, [])
            
            if hl_for_chunk:
                chunks_with_mini_chunks.append(chunk)
                logger.info(f"Chunk {metadata.get('chunk_index')} 有 {len(hl_for_chunk)} 个mini-chunks")
            else:
                chunks_without_mini_chunks.append(chunk)
                logger.info(f"Chunk {metadata.get('chunk_index')} 无mini-chunks")
        
        # 只选择有mini-chunks的chunk，确保引用只包含AI实际使用的信息
        selected_chunks = chunks_with_mini_chunks.copy()
        
        if not selected_chunks:
            selected_chunks = []
        logger.info(f"选择了 {len(selected_chunks)} 个chunks（有mini-chunks: {len(chunks_with_mini_chunks)}, 无mini-chunks: 0）")

        # 如果阈值过滤后没有任何chunk，或者所有选中的chunk都没有mini-chunks，通过LLM返回顺序取第一个有效的mini-chunk所属的大块作为兜底
        if not selected_chunks or all(len(chunk.get('metadata', {}).get('mini_chunks', [])) == 0 for chunk in selected_chunks):
            # 如果有LLM返回的mini-chunk IDs，尝试使用它们
            if used_mc_ids:
                for mcid in used_mc_ids:
                    # 处理可能的格式问题，如"knowledge_id:2:3:14"应该是"30:2:3:14"
                    if mcid.startswith("knowledge_id:"):
                        fixed_mcid = mcid.replace("knowledge_id:", "30:")
                        logger.warning(f"修正错误格式的mc_id: {mcid} -> {fixed_mcid}")
                        mcid = fixed_mcid
                    
                    entry = mcid_to_entry.get(mcid)
                    if entry:
                        fallback_key = (entry.get("knowledge_id"), entry.get("chunk_index"))
                        for chunk in context_chunks:
                            meta = chunk.get("metadata", {})
                            if (meta.get("knowledge_id"), meta.get("chunk_index")) == fallback_key:
                                selected_chunks = [chunk]
                                logger.info(f"使用LLM首个有效mini-chunk所属chunk作为兜底: mcid={mcid}, key={fallback_key}")
                                break
                        if selected_chunks:
                            break
            
            # 如果仍然没有找到合适的chunk，选择相似度最高的chunk
            if not selected_chunks and context_chunks:
                selected_chunks = [max(context_chunks, key=lambda x: x.get('metadata', {}).get('relevance_score', 0))]
                logger.info(f"无法找到有效mini-chunks，使用相似度最高的chunk作为兜底: chunk_index={selected_chunks[0].get('metadata', {}).get('chunk_index')}")
        
        for chunk in selected_chunks:
            # 重要：在第二次循环中重新获取本次chunk的metadata，避免沿用上一次循环的metadata
            metadata = chunk['metadata']

            # 从模型返回的 used_mc_ids 中取本 chunk 的高亮，只取属于当前chunk的mini-chunk
            key = (metadata.get('knowledge_id', 0), metadata.get('chunk_index', 0))
            hl_for_chunk = []
            for mcid in used_mc_ids:
                entry = mcid_to_entry.get(mcid)
                if entry and entry.get("knowledge_id") == metadata.get('knowledge_id') and entry.get("chunk_index") == metadata.get('chunk_index'):
                    # 只使用属于当前chunk的mini-chunk
                    hl_for_chunk.append(entry)
                    logger.info(f"找到匹配的mini-chunk: {mcid}, 页码: {entry.get('page')}, 文本: {entry.get('text')[:30]}...")
                    break

            # 如果有选中的小块，使用所有选中小块的坐标并扩大4倍；否则使用大块的坐标
            if hl_for_chunk:
                # 收集所有选中小块的坐标
                all_bboxes = [mc.get("bbox", []) for mc in hl_for_chunk if mc.get("bbox") and len(mc.get("bbox", [])) == 4]
                if all_bboxes:
                    # 为每个小块单独扩大4倍，保留多个bbox
                    expanded_bboxes = []
                    for bbox in all_bboxes:
                        x0, y0, x1, y1 = bbox
                        
                        # 计算中心点和尺寸
                        center_x = (x0 + x1) / 2
                        center_y = (y0 + y1) / 2
                        width = x1 - x0
                        height = y1 - y0

                        # 扩大倍率调整到4倍，确保短文本也能有足够大的高亮区域
                        new_width = width * 4
                        new_height = height * 4

                        # 计算新的边界框
                        new_x0 = center_x - new_width / 2
                        new_y0 = center_y - new_height / 2
                        new_x1 = center_x + new_width / 2
                        new_y1 = center_y + new_height / 2

                        expanded_bboxes.append([new_x0, new_y0, new_x1, new_y1])
                    
                    bbox_to_use = expanded_bboxes
                    logger.info(f"为 chunk {metadata.get('chunk_index')} 使用选中小块坐标并扩大4倍: {all_bboxes} -> {bbox_to_use}")
                else:
                    bbox_to_use = [metadata.get('bbox', [])] if metadata.get('bbox') else []
                    logger.info(f"为 chunk {metadata.get('chunk_index')} 小块坐标为空或格式错误，使用大块坐标")
            else:
                # 使用大块坐标
                bbox_to_use = [metadata.get('bbox', [])] if metadata.get('bbox') else []
                logger.info(f"为 chunk {metadata.get('chunk_index')} 无小块，使用大块坐标")
            
            # 如果有选中的小块，使用小块的页码；否则使用chunk的页码
            page_num_to_use = hl_for_chunk[0].get("page", metadata.get('page_num', 0)) if hl_for_chunk else metadata.get('page_num', 0)
            
            references.append(KnowledgeReference(
                knowledge_id=int(metadata.get('knowledge_id', 0)) if metadata.get('knowledge_id') is not None else 0,
                knowledge_name=metadata.get('knowledge_name', ''),
                description=metadata.get('description', ''),
                tags=[metadata.get('tags', '')] if isinstance(metadata.get('tags', ''), str) else metadata.get('tags', []),
                effective_time=metadata.get('effective_time', ''),
                attachments=[metadata.get('document_name', '')],
                relevance=relevance_score,
                source_file=metadata.get('document_name', ''),
                page_num=page_num_to_use,  # 使用选中小块的页码或大块的页码
                chunk_index=metadata.get('chunk_index', 0),
                chunk_type="content",
                bbox_union=bbox_to_use,  # 使用选中的小块坐标或大块坐标
                char_start=0,  # 不再使用字符位置
                char_end=0
            ))
        
        logger.info(f"相似度过滤后，返回 {len(references)} 个引用（阈值: {SIMILARITY_THRESHOLD}）")
        
        return ChatResponse(
            answer=answer,
            references=references,
            session_id=user_id
        )
        
    except Exception as e:
        logger.error(f"RAG聊天失败: {e}")
        return ChatResponse(
            answer=f"抱歉，处理您的问题时出现错误：{str(e)}",
            references=[],
            session_id=user_id
        )
