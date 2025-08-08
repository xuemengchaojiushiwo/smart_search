#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 PDF 解析为 Markdown（含：标题层级、文本块、图片、页码与粗定位），用于验证接近 PDFLLM 的效果。
- 仅使用开源 PyMuPDF（fitz），无需 Pro
- 按页面顺序提取 block（文本/图片），保持版式顺序
- 通过字体大小分级，启发式生成 #/##/### 标题
- 图片抽取并在 Markdown 中就地引用
- 输出：
  - <out_dir>/document.md         结构化 Markdown
  - <out_dir>/images/...          页内图片资源
  - <out_dir>/layout_report.json  统计报告（页数/图片数/标题数等）
用法：
  python pdf_layout_to_markdown.py --pdf path/to/file.pdf --out out_dir
"""

import os
import json
import math
import argparse
from typing import List, Dict, Any, Tuple
import re
import difflib
from collections import deque

import fitz  # PyMuPDF（开源版）

try:
    import pdfplumber  # 表格抽取补充
    PDFPLUMBER_AVAILABLE = True
except Exception:
    PDFPLUMBER_AVAILABLE = False


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def collect_font_sizes(doc: fitz.Document) -> List[float]:
    sizes = []
    for page in doc:
        raw = page.get_text("rawdict")
        for block in raw.get("blocks", []):
            if block.get("type") == 0:  # text
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        size = float(span.get("size", 0) or 0)
                        if size > 0:
                            sizes.append(size)
    return sizes


def size_to_heading_levels(sizes: List[float]) -> List[float]:
    """返回从大到小的3个阈值，用于H1/H2/H3切分（简单分位数法）。"""
    if not sizes:
        return []
    sizes_sorted = sorted(sizes)
    n = len(sizes_sorted)
    # 90/75/60 分位点作阈值
    q90 = sizes_sorted[int(0.9 * (n - 1))]
    q75 = sizes_sorted[int(0.75 * (n - 1))]
    q60 = sizes_sorted[int(0.6 * (n - 1))]
    return [q90, q75, q60]


def infer_heading(size: float, thresholds: List[float], font_name: str) -> int:
    """根据字体大小与字体名（含Bold）估计标题级别。返回 0 表示正文。"""
    if not thresholds:
        return 0
    bold = "bold" in (font_name or "").lower()
    if size >= thresholds[0] or (bold and size >= thresholds[1]):
        return 1
    if size >= thresholds[1]:
        return 2
    if size >= thresholds[2]:
        return 3
    return 0


def extract_blocks(page: fitz.Page) -> List[Dict[str, Any]]:
    """从页面获得按版式顺序的block列表（文本/图片），带 bbox 等基础信息。
    包含多重回退：rawdict → blocks(sort) → 整页text。
    """
    blocks: List[Dict[str, Any]] = []

    # 1) 首选 rawdict（可拿到字体大小用于标题启发）
    try:
        raw = page.get_text("rawdict")
        total_chars = 0
        for bi, block in enumerate(raw.get("blocks", [])):
            btype = block.get("type")  # 0=text, 1=image
            bbox = block.get("bbox")
            if btype == 0:
                lines_joined: List[str] = []
                spans_meta = []
                for line in block.get("lines", []):
                    line_parts = []
                    for span in line.get("spans", []):
                        stext = span.get("text", "")
                        if stext:
                            line_parts.append(stext)
                            spans_meta.append({
                                "size": float(span.get("size", 0) or 0),
                                "font": span.get("font", ""),
                            })
                    if line_parts:
                        lines_joined.append("".join(line_parts))
                text = "\n".join(lines_joined).strip()
                # 连字符换行修复：将 "-\n" 合并为 ""
                text = re.sub(r"-\n(?=\w)", "", text)
                total_chars += len(text)
                max_size = max([m["size"] for m in spans_meta], default=0.0)
                any_font = spans_meta[0]["font"] if spans_meta else ""
                if text:
                    blocks.append({
                        "type": "text",
                        "bbox": bbox,
                        "text": text,
                        "max_size": max_size,
                        "font": any_font,
                        "block_index": bi
                    })
            elif btype == 1:
                blocks.append({
                    "type": "image",
                    "bbox": bbox,
                    "image_name": block.get("image"),
                    "block_index": bi
                })
        if any(b.get("type") == "text" for b in blocks) and total_chars > 0:
            return blocks
    except Exception:
        pass

    # 2) 回退到 blocks（简化，只能得到文本与bbox）
    try:
        blk = page.get_text("blocks", sort=True)
        for bi, b in enumerate(blk):
            x0, y0, x1, y1, text, block_no, block_type = b
            if block_type == 0 and text and text.strip():
                fixed = re.sub(r"-\n(?=\w)", "", text.strip())
                blocks.append({
                    "type": "text",
                    "bbox": [x0, y0, x1, y1],
                    "text": fixed,
                    "max_size": 0.0,
                    "font": "",
                    "block_index": bi
                })
        if any(b.get("type") == "text" for b in blocks):
            return blocks
    except Exception:
        pass

    # 3) 最后回退整页 text（无版式，保证至少有可读文本）
    try:
        text = page.get_text("text") or ""
        if text.strip():
            fixed = re.sub(r"-\n(?=\w)", "", text.strip())
            blocks.append({
                "type": "text",
                "bbox": list(page.rect),
                "text": fixed,
                "max_size": 0.0,
                "font": "",
                "block_index": 0
            })
            return blocks
    except Exception:
        pass

    # 4) 若确为扫描件或无可提取文本，仅返回图片信息（若有）
    try:
        images = page.get_images(full=True)
        for bi, img in enumerate(images):
            blocks.append({
                "type": "image",
                "bbox": [],
                "image_name": f"xref:{img[0]}",
                "block_index": bi
            })
    except Exception:
        pass
    return blocks


def export_image(page: fitz.Page, image_dir: str, bbox: List[float], index_hint: int) -> str:
    """导出页面中与 bbox 匹配度最高的图像（近似法）。返回相对路径。"""
    ensure_dir(image_dir)
    # 简化：遍历 page.get_images，取第一张像素图导出
    # 更好的做法是根据 bbox 与图像矩阵做几何匹配，这里以近似为主用于验证
    images = page.get_images(full=True)
    if not images:
        return ""
    idx = max(0, min(index_hint, len(images) - 1))
    xref = images[idx][0]
    pix = fitz.Pixmap(page.parent, xref)
    # 转成RGB避免带alpha的CMYK等
    if pix.n >= 5:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    out_name = f"img_p{page.number+1}_{index_hint}.png"
    out_path = os.path.join(image_dir, out_name)
    pix.save(out_path)
    return os.path.join("images", out_name)


def extract_tables_by_pdfplumber(pdf_path: str) -> Dict[int, List[List[str]]]:
    """用 pdfplumber 抽取表格，返回 {page_number: [table_rows]}。失败则返回空。"""
    results: Dict[int, List[List[str]]] = {}
    if not PDFPLUMBER_AVAILABLE:
        return results
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                try:
                    tables = page.extract_tables() or []
                    merged: List[List[str]] = []
                    for table in tables:
                        # 规范化为字符串
                        for row in table:
                            merged.append([(cell if cell is not None else '').strip() for cell in row])
                    if merged:
                        results[i + 1] = merged
                except Exception:
                    continue
    except Exception:
        return {}
    return results


def detect_repeating_headers_footers(doc: fitz.Document) -> Tuple[set, set]:
    """启发式检测跨页重复的页眉/页脚文本（用于清洗）。"""
    headers: Dict[str, int] = {}
    footers: Dict[str, int] = {}
    total_pages = len(doc)

    for page in doc:
        blocks = extract_blocks(page)
        # 取前两个与后两个文本块作为候选
        text_blocks = [b for b in blocks if b.get("type") == "text" and b.get("text")]
        if text_blocks:
            head_txt = text_blocks[0]["text"].strip()[:80]
            if head_txt:
                headers[head_txt] = headers.get(head_txt, 0) + 1
            if len(text_blocks) >= 2:
                head_txt2 = text_blocks[1]["text"].strip()[:80]
                if head_txt2:
                    headers[head_txt2] = headers.get(head_txt2, 0) + 1
        if text_blocks:
            tail_txt = text_blocks[-1]["text"].strip()[:80]
            if tail_txt:
                footers[tail_txt] = footers.get(tail_txt, 0) + 1
            if len(text_blocks) >= 2:
                tail_txt2 = text_blocks[-2]["text"].strip()[:80]
                if tail_txt2:
                    footers[tail_txt2] = footers.get(tail_txt2, 0) + 1

    # 选择出现频率 >= 60% 页的文本作为页眉/页脚
    threshold = max(2, int(0.6 * total_pages))
    header_set = {t for t, c in headers.items() if c >= threshold}
    footer_set = {t for t, c in footers.items() if c >= threshold}
    return header_set, footer_set


def make_markdown(doc: fitz.Document, out_dir: str, pdf_path: str) -> Dict[str, Any]:
    ensure_dir(out_dir)
    image_dir = os.path.join(out_dir, "images")
    ensure_dir(image_dir)

    sizes = collect_font_sizes(doc)
    thresholds = size_to_heading_levels(sizes)

    md_lines: List[str] = []
    report = {
        "pages": len(doc),
        "images": 0,
        "text_blocks": 0,
        "headings": {"h1": 0, "h2": 0, "h3": 0},
        "tables": 0
    }

    # 预抽取表格
    tables_map: Dict[int, List[List[str]]] = extract_tables_by_pdfplumber(pdf_path)

    # 页眉/页脚候选，用于清洗
    header_set, footer_set = detect_repeating_headers_footers(doc)

    # 近重复文本抑制（全局级别）：避免跨页/双栏导致的大段重复
    def normalize_text(s: str) -> str:
        s2 = s.lower().strip()
        # 去除空白与常见标点，保留中文/英文/数字
        s2 = re.sub(r"[\s\u3000]+", "", s2)
        s2 = re.sub(r"[\-—–·•\.,;:!\?\(\)\[\]\{\}<>\|\/\\\*\^\$\#\+_=~`'\"]+", "", s2)
        return s2

    seen_norm = set()
    recent_norm = deque(maxlen=500)

    for page in doc:
        pno = page.number + 1
        md_lines.append(f"\n\n<!-- Page {pno} -->\n")
        blocks = extract_blocks(page)
        img_idx = 0
        # 基于Y坐标稳定排序（少数PDF rawdict顺序可能错乱）
        # 同时进行双栏启发式：按照 x 中值分左右栏，先左列再右列
        width = float(page.rect.width or 0)
        centers = []
        for b in blocks:
            bbox = b.get("bbox") or [0, 0, 0, 0]
            centers.append((b, (bbox[0] + bbox[2]) / 2.0))
        xs = [c for _, c in centers if c > 0]
        mid = (min(xs) + max(xs)) / 2.0 if xs else width / 2.0
        # 判定是否存在明显双列：左右两侧都有足量文本块
        left_cnt = sum(1 for _, c in centers if c < mid - 20)
        right_cnt = sum(1 for _, c in centers if c > mid + 20)
        two_cols = left_cnt >= 3 and right_cnt >= 3

        def sort_key(b: Dict[str, Any]):
            bbox = b.get("bbox") or [0, 0, 0, 0]
            y = round(bbox[1], 1)
            x = round(bbox[0], 1)
            col = 0
            if two_cols:
                cx = (bbox[0] + bbox[2]) / 2.0
                col = 0 if cx < mid else 1
            return (col, y, x, b.get("block_index", 0))

        blocks_sorted = sorted(blocks, key=sort_key)
        for b in blocks_sorted:
            if b["type"] == "text":
                txt = b["text"]
                if not txt:
                    continue
                # 页眉/页脚清洗
                head_key = txt.strip()[:80]
                if head_key in header_set or head_key in footer_set:
                    continue
                # 近重复抑制：对较长文本做规范化去重
                norm = normalize_text(txt)
                if len(txt) >= 30:
                    if norm in seen_norm:
                        continue
                    # 与最近窗口内条目做相似度近重复判定
                    skip = False
                    for prev in recent_norm:
                        if len(prev) < 20:
                            continue
                        if difflib.SequenceMatcher(None, norm[:200], prev[:200]).ratio() >= 0.97:
                            skip = True
                            break
                    if skip:
                        continue
                    seen_norm.add(norm)
                    recent_norm.append(norm)
                h = infer_heading(b.get("max_size", 0.0), thresholds, b.get("font", ""))
                # 合并过短行，避免标题被切碎
                if len(txt) <= 2 and md_lines and md_lines[-1] and not md_lines[-1].startswith('#'):
                    md_lines[-1] = md_lines[-1].rstrip() + txt
                    continue
                if h == 1:
                    md_lines.append(f"# {txt}")
                    report["headings"]["h1"] += 1
                elif h == 2:
                    md_lines.append(f"## {txt}")
                    report["headings"]["h2"] += 1
                elif h == 3:
                    md_lines.append(f"### {txt}")
                    report["headings"]["h3"] += 1
                else:
                    md_lines.append(txt)
                report["text_blocks"] += 1
                bbox = b.get("bbox") or []
                if bbox:
                    md_lines.append(f"\n<sub>pos: page={pno}, bbox={','.join([str(round(x,1)) for x in bbox])}</sub>")
            else:
                rel_path = export_image(page, image_dir, b.get("bbox") or [], img_idx)
                if rel_path:
                    md_lines.append(f"\n![page {pno} image]({rel_path})\n")
                    report["images"] += 1
                img_idx += 1

        # 在页面尾部追加该页的表格（如有）
        page_tables = tables_map.get(pno) or []
        if page_tables:
            md_lines.append(f"\n**表格（第 {pno} 页）**\n")
            table_seen = set()
            for table in page_tables:
                if not table:
                    continue
                # 生成 Markdown 表格
                header = table[0]
                sig = normalize_text("|".join(header[:6])) if header else ""
                if sig and sig in table_seen:
                    continue
                if sig:
                    table_seen.add(sig)
                md_lines.append("| " + " | ".join([c or '' for c in header]) + " |")
                md_lines.append("| " + " | ".join(["---" for _ in header]) + " |")
                for row in table[1:]:
                    md_lines.append("| " + " | ".join([c or '' for c in row]) + " |")
                md_lines.append("")
                report["tables"] += 1

    md_path = os.path.join(out_dir, "document.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    with open(os.path.join(out_dir, "layout_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return {"md_path": md_path, "report": report}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="PDF文件路径")
    parser.add_argument("--out", required=True, help="输出目录")
    args = parser.parse_args()

    if not os.path.exists(args.pdf):
        raise SystemExit(f"❌ PDF不存在: {args.pdf}")

    doc = fitz.open(args.pdf)
    res = make_markdown(doc, args.out, args.pdf)
    print(json.dumps({"ok": True, **res}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
