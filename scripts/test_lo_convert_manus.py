#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试使用 LibreOffice (soffice) 将文档转换为 PDF。
默认转换 python_service/file/manus介绍.docx 到临时目录，完成后校验PDF页数。

用法示例（逐条执行，不要用 && 串联）：
  python scripts/test_lo_convert_manus.py
  python scripts/test_lo_convert_manus.py --input python_service/file/安联美元.pdf  # 已是PDF将直接校验
  python scripts/test_lo_convert_manus.py --input python_service/file/manus介绍.docx --soffice "C:\\Program Files\\LibreOffice\\program\\soffice.exe"
"""

import argparse
import os
import sys
import tempfile
import subprocess
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as e:
    print("缺少依赖: PyMuPDF，请先安装: pip install pymupdf")
    sys.exit(1)

COMMON_SOFFICE_CANDIDATES = [
    r"C:\\Program Files\\LibreOffice\\program\\soffice.exe",
    r"C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe",
]


def find_soffice(explicit_path: str | None) -> str:
    if explicit_path:
        p = Path(explicit_path)
        if p.exists():
            return str(p)
        print(f"指定的 soffice 不存在: {explicit_path}")
    # 常见路径
    for cand in COMMON_SOFFICE_CANDIDATES:
        if Path(cand).exists():
            return cand
    # PATH 中查找
    from shutil import which
    w = which("soffice") or which("soffice.exe")
    if w:
        return w
    raise FileNotFoundError(
        "未找到 soffice，请安装 LibreOffice 或通过 --soffice 指定完整路径。\n"
        "可使用 winget 安装: winget install TheDocumentFoundation.LibreOffice"
    )


def convert_with_libreoffice(src_path: str, soffice_path: str, out_dir: str, timeout_sec: int = 180) -> str:
    src_path = os.path.abspath(src_path)
    if not os.path.exists(src_path):
        raise FileNotFoundError(src_path)
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        soffice_path,
        "--headless",
        "--norestore",
        "--nolockcheck",
        "--convert-to", "pdf",
        "--outdir", out_dir,
        src_path,
    ]
    print("运行命令:", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
    if cp.returncode != 0:
        print("LibreOffice 转换失败:")
        print("stdout:", cp.stdout)
        print("stderr:", cp.stderr)
        raise RuntimeError(f"转换失败，退出码={cp.returncode}")

    # 期望输出名：同名 .pdf
    expected = os.path.join(out_dir, Path(src_path).with_suffix('.pdf').name)
    if os.path.exists(expected):
        return expected
    # 兜底：取 out_dir 下最新的 pdf
    pdfs = [Path(out_dir) / p for p in os.listdir(out_dir) if str(p).lower().endswith('.pdf')]
    if not pdfs:
        print("stdout:", cp.stdout)
        print("stderr:", cp.stderr)
        raise FileNotFoundError("未找到转换生成的PDF")
    pdfs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return str(pdfs[0])


def validate_pdf(pdf_path: str) -> int:
    doc = fitz.open(pdf_path)
    try:
        pages = len(doc)
        return pages
    finally:
        doc.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default='python_service/file/manus介绍.docx', help='输入文件路径（docx/xlsx/pptx/pdf等）')
    ap.add_argument('--soffice', default=None, help='soffice.exe 路径，留空则自动探测')
    ap.add_argument('--outdir', default=None, help='PDF输出目录，默认临时目录')
    ap.add_argument('--timeout', type=int, default=180, help='转换超时秒数')
    args = ap.parse_args()

    src = args.input
    if not os.path.exists(src):
        print(f"输入文件不存在: {src}")
        sys.exit(1)

    # 若本身是PDF，直接校验
    if Path(src).suffix.lower() == '.pdf':
        pages = validate_pdf(src)
        print(f"输入已是PDF，无需转换: {src}  页数: {pages}")
        sys.exit(0)

    try:
        soffice = find_soffice(args.soffice)
        outdir = args.outdir or tempfile.mkdtemp(prefix='lo_pdf_')
        pdf_path = convert_with_libreoffice(src, soffice, outdir, timeout_sec=args.timeout)
        pages = validate_pdf(pdf_path)
        print(f"转换成功: {pdf_path}")
        print(f"页数: {pages}")
    except Exception as e:
        print(f"❌ 转换失败: {e}")
        sys.exit(2)


if __name__ == '__main__':
    main()

