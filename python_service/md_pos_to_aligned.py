#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将包含 <sub>pos: page=..., bbox=x0,y0,x1,y1</sub> 的 Markdown 转为 aligned_positions.json。
规则：
- 逐行扫描：遇到非空文本行，若下一行是 <sub>pos: ...</sub>，则作为一条 item
- 输出字段：text, page_num, bbox_union, bboxes([bbox]), char_start=-1, char_end=-1, para_index
"""
import re
import os
import json
import argparse
from typing import List, Dict, Any


POS_RE = re.compile(r"<sub>\s*pos:\s*page\s*=\s*(\d+)\s*,\s*bbox\s*=\s*([\d\.,-]+)\s*</sub>", re.IGNORECASE)


def parse_md_with_pos(md_path: str) -> List[Dict[str, Any]]:
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = [ln.rstrip("\n") for ln in f]

    items: List[Dict[str, Any]] = []
    i = 0
    para_index = 0
    while i < len(lines):
        text_line = lines[i].strip()
        if text_line and not text_line.startswith('<sub>pos:'):
            # 向前查看最近的非空行是否为 pos 标签（跳过空行），最多前看 5 行
            j = i + 1
            steps = 0
            m = None
            while j < len(lines) and steps < 5:
                nxt = lines[j].strip()
                if nxt:
                    m = POS_RE.search(nxt)
                    break
                j += 1
                steps += 1
            if m:
                page_num = int(m.group(1))
                bbox_vals = [float(x) for x in m.group(2).split(',') if x]
                bbox = bbox_vals[:4] if len(bbox_vals) >= 4 else []
                items.append({
                    'para_index': para_index,
                    'text': text_line,
                    'page_num': page_num,
                    'bbox_union': bbox,
                    'bboxes': [bbox] if bbox else [],
                    'char_start': -1,
                    'char_end': -1,
                })
                para_index += 1
                i = j + 1
                continue
        i += 1
    return items


def save_aligned(items: List[Dict[str, Any]], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'items': items}, f, ensure_ascii=False, indent=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--md', required=True, help='带 <sub>pos: ...</sub> 的 Markdown 路径')
    ap.add_argument('--out', required=True, help='输出 aligned_positions.json 路径')
    args = ap.parse_args()
    items = parse_md_with_pos(args.md)
    save_aligned(items, args.out)
    print(json.dumps({'ok': True, 'count': len(items), 'out': args.out}, ensure_ascii=False))


if __name__ == '__main__':
    main()


