#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
"""

import logging
import re
import json
import os
import tempfile
import subprocess
from pathlib import Path
from shutil import which
import shutil
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)


def clean_json_from_answer(answer: str) -> str:
    """
    清理AI回答中的JSON格式信息，只保留纯文本回答
    """
    if not answer:
        return answer
    
    original_answer = answer
    
    # 移除所有JSON代码块
    if "```json" in answer:
        answer = answer.split("```json")[0].strip()
    if "```" in answer:
        answer = answer.split("```")[0].strip()
    
    # 移除所有包含used_mc_ids的JSON格式信息（包括空数组和非空数组）
    if "{" in answer and "used_mc_ids" in answer:
        # 匹配各种格式的used_mc_ids JSON
        answer = re.sub(r'\{[^}]*"used_mc_ids"[^}]*\}', '', answer).strip()
        # 匹配多行JSON格式
        answer = re.sub(r'\{[^}]*"used_mc_ids"[^}]*\}', '', answer, flags=re.DOTALL).strip()
    
    # 清理各种提示语
    answer = re.sub(r'以下是相关的JSON格式响应：', '', answer).strip()
    answer = re.sub(r'以下是JSON格式的响应：', '', answer).strip()
    answer = re.sub(r'JSON格式的响应：', '', answer).strip()
    answer = re.sub(r'相关JSON格式响应：', '', answer).strip()
    
    # 清理可能残留的JSON片段
    answer = re.sub(r'^\s*\{.*\}\s*$', '', answer).strip()
    answer = re.sub(r'^\s*\[.*\]\s*$', '', answer).strip()
    
    if answer != original_answer:
        logger.info(f"已清理JSON信息，原始长度: {len(original_answer)}, 清理后长度: {len(answer)}")
    
    return answer


def parse_used_mc_ids(answer: str) -> List[str]:
    """从模型回答中解析 used_mc_ids JSON"""
    if not answer:
        return []
    
    logger.info(f"开始解析回答: {answer[-200:]}")  # 显示最后200个字符
    
    # 方法1: 直接查找JSON格式的used_mc_ids
    # 使用更宽松的正则表达式
    json_patterns = [
        r'\{[^}]*"used_mc_ids"[^}]*\[[^\]]*\][^}]*\}',  # 原模式
        r'\{[^}]*"used_mc_ids"[^}]*\}',  # 简化模式
        r'"used_mc_ids"\s*:\s*\[[^\]]*\]',  # 只匹配数组部分
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, answer, re.DOTALL)
        logger.info(f"模式 {pattern} 匹配到: {matches}")
        for match in matches:
            try:
                # 如果匹配的不是完整JSON，尝试构造完整JSON
                if not match.startswith('{'):
                    match = '{' + match + '}'
                data = json.loads(match)
                if isinstance(data.get("used_mc_ids"), list):
                    logger.info(f"成功解析JSON: {data['used_mc_ids']}")
                    return data["used_mc_ids"]
            except Exception as e:
                logger.warning(f"JSON解析失败: {e}, 匹配内容: {match}")
                continue
    
    # 方法2: 尝试提取类似 "kid:page:chunk:i" 格式的ID
    id_pattern = r'[0-9]+:[0-9]+:[0-9]+:[0-9]+'
    ids = re.findall(id_pattern, answer)
    if ids:
        logger.info(f"通过正则提取到IDs: {ids}")
        return ids
    
    # 方法3: 兜底策略
    logger.warning("模型未返回标准JSON格式，尝试关键词匹配")
    return []


def fallback_keyword_matching(question: str, mcid_to_entry: Dict[str, Dict]) -> List[str]:
    """兜底策略：基于关键词匹配选择相关小块"""
    if not question or not mcid_to_entry:
        return []
    
    # 提取问题中的关键词
    keywords = []
    
    # 中文关键词提取
    if re.search(r'[\u4e00-\u9fff]', question):
        # 简单的中文关键词提取
        chinese_keywords = ['基金', '总值', '价值', '净值', '资产', '规模', '金额', '美元', '投资', '债券']
        for kw in chinese_keywords:
            if kw in question:
                keywords.append(kw)
    else:
        # 英文关键词提取
        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if len(w) > 2]
    
    if not keywords:
        return []
    
    # 为每个小块计算匹配分数
    scored_chunks = []
    for mc_id, entry in mcid_to_entry.items():
        text = entry.get('text', '').lower()
        score = 0
        
        for keyword in keywords:
            if keyword.lower() in text:
                score += 1
        
        if score > 0:
            scored_chunks.append((mc_id, score))
    
    # 按分数排序，返回前3个
    scored_chunks.sort(key=lambda x: x[1], reverse=True)
    return [mc_id for mc_id, score in scored_chunks[:3]]


def extract_keywords_from_content(content: str) -> List[str]:
    """从内容提取关键标识词（通用版本）"""
    keywords = []
    content_lower = content.lower()
    
    # 通用关键词
    general_keywords = ["投资", "管理", "风险", "收益", "费用", "日期", "目标", "策略", "报告", "分析"]
    for keyword in general_keywords:
        if keyword in content_lower:
            keywords.append(keyword)
    
    # 文档结构关键词
    structure_keywords = ["标题", "章节", "表格", "图表", "附录", "摘要", "结论"]
    for keyword in structure_keywords:
        if keyword in content_lower:
            keywords.append(keyword)
    
    return keywords[:8]  # 限制关键词数量


def _find_soffice_path() -> Optional[str]:
    """查找LibreOffice的soffice路径"""
    candidates = [
        r"C:\\Program Files\\LibreOffice\\program\\soffice.exe",
        r"C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    w = which("soffice") or which("soffice.exe")
    return w


def convert_with_libreoffice_safe(src_path: str, timeout_sec: int = 180, out_dir: Optional[str] = None) -> str:
    """使用LibreOffice将任意Office文档转为PDF，输出到临时文件夹，返回PDF路径。"""
    soffice = _find_soffice_path()
    if not soffice:
        raise RuntimeError("未找到LibreOffice的soffice.exe，请安装或配置PATH后重试")

    if not out_dir:
        out_dir = tempfile.mkdtemp(prefix="lo_pdf_")
    else:
        os.makedirs(out_dir, exist_ok=True)
    cmd = [
        soffice,
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        os.path.abspath(src_path),
    ]
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    if cp.returncode != 0:
        raise RuntimeError(f"LibreOffice 转换失败: rc={cp.returncode}\nstdout={cp.stdout}\nstderr={cp.stderr}")

    # 期望同名pdf
    expected = os.path.join(out_dir, Path(src_path).with_suffix('.pdf').name)
    if os.path.exists(expected):
        return expected
    # 兜底找最新pdf
    pdfs = [p for p in os.listdir(out_dir) if p.lower().endswith('.pdf')]
    if not pdfs:
        raise RuntimeError(f"LibreOffice 未生成PDF。stdout={cp.stdout}\nstderr={cp.stderr}")
    pdfs.sort(key=lambda n: os.path.getmtime(os.path.join(out_dir, n)), reverse=True)
    return os.path.join(out_dir, pdfs[0])


def build_converted_pdf_path(knowledge_id: int, original_filename: str) -> str:
    """构建转换后的PDF路径"""
    base = Path(original_filename).stem + '.pdf'
    target_dir = os.path.join(os.path.dirname(__file__), 'static', 'converted', str(knowledge_id))
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, base)


def calculate_chunk_bbox(positions: List[Dict]) -> List[float]:
    """计算chunk的边界框：先按span所在页聚类，取位置最多的页作为主页面，再对该页的positions求并集"""
    if not positions:
        return [0, 0, 0, 0]

    # 位置里需要带上page信息；若没有，默认页=1
    page_to_positions: Dict[int, List[Dict]] = {}
    for pos in positions:
        page = int(pos.get('page', 1)) if isinstance(pos, dict) else 1
        page_to_positions.setdefault(page, []).append(pos)

    # 选择位置最多的页作为主页面
    main_page = max(page_to_positions.items(), key=lambda kv: len(kv[1]))[0]
    main_positions = page_to_positions[main_page]

    x0 = min(p["bbox"][0] for p in main_positions)
    y0 = min(p["bbox"][1] for p in main_positions)
    x1 = max(p["bbox"][2] for p in main_positions)
    y1 = max(p["bbox"][3] for p in main_positions)

    return [x0, y0, x1, y1]
