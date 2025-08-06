#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyMuPDF Pro 文件清理脚本
根据分析结果自动清理不需要的文件
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """清理不需要的文件"""
    print("🧹 开始清理 PyMuPDF Pro 相关文件")
    print("=" * 50)
    
    # 要删除的文件列表
    files_to_delete = [
        "test_document_processing.py",  # 临时测试文件
        "pymupdf4llm_analysis.md",  # 临时文档
        "src\main\java\com\knowledge\dto\LoginRequest.java",  # 临时文件
        "src\main\java\com\knowledge\entity\CategoryChangeLog.java",  # 临时文件
        "src\main\java\com\knowledge\vo\CategoryChangeLogVO.java",  # 临时文件
        "src\main\java\com\knowledge\vo\LoginResponse.java",  # 临时文件
        "target\classes\com\knowledge\dto\LoginRequest.class",  # 临时文件
        "target\classes\com\knowledge\entity\CategoryChangeLog.class",  # 临时文件
        "target\classes\com\knowledge\vo\CategoryChangeLogVO.class",  # 临时文件
        "target\classes\com\knowledge\vo\LoginResponse$UserVO.class",  # 临时文件
        "target\classes\com\knowledge\vo\LoginResponse.class",  # 临时文件
    ]
    
    # 要移动的文件列表（移动到backup目录）
    files_to_move = [
        "simple_pymupdf_test.py",  # 简化测试脚本
        "test_pymupdf_pro_with_key.py",  # PyMuPDF Pro功能测试
        "migration_guide_pymupdf_pro.md",  # 迁移指南
        "pymupdf_pro_analysis.md",  # 技术分析
        "pymupdf_pro_status.md",  # 状态文档
    ]
    
    # 创建backup目录
    backup_dir = Path("pymupdf_pro_backup")
    backup_dir.mkdir(exist_ok=True)
    
    # 删除文件
    deleted_count = 0
    for file_path in files_to_delete:
        path = Path(file_path)
        if path.exists():
            try:
                path.unlink()
                print(f"🗑️  已删除: {file_path}")
                deleted_count += 1
            except Exception as e:
                print(f"❌ 删除失败 {file_path}: {e}")
    
    # 移动文件
    moved_count = 0
    for file_path in files_to_move:
        path = Path(file_path)
        if path.exists():
            try:
                target_path = backup_dir / path.name
                shutil.move(str(path), str(target_path))
                print(f"📦 已移动: {file_path} -> {target_path}")
                moved_count += 1
            except Exception as e:
                print(f"❌ 移动失败 {file_path}: {e}")
    
    print(f"\n✅ 清理完成: 删除 {deleted_count} 个文件, 移动 {moved_count} 个文件")
    print(f"📁 备份文件位置: {backup_dir}")

if __name__ == "__main__":
    cleanup_files()
