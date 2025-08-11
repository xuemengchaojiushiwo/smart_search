#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于PDFLLM风格格式创建去掉位置信息的干净版本
用于对比内容完整性
"""

import re
import os

def create_clean_version_from_pdfllm(pdfllm_file_path: str, output_path: str = None) -> str:
    """从PDFLLM风格文件创建干净版本"""
    if not os.path.exists(pdfllm_file_path):
        raise FileNotFoundError(f"PDFLLM风格文件不存在: {pdfllm_file_path}")
    
    with open(pdfllm_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去掉位置信息标签
    # 匹配 <sub>pos: page=X, bbox=(...)</sub> 格式
    clean_content = re.sub(r'<sub>pos: page=\d+, bbox=\([^)]+\)</sub>', '', content)
    
    # 清理多余的空行和空格
    lines = clean_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:  # 只保留非空行
            cleaned_lines.append(line)
    
    # 重新组合内容
    final_content = '\n'.join(cleaned_lines)
    
    # 保存到文件
    if output_path is None:
        base_name = os.path.splitext(pdfllm_file_path)[0]
        output_path = f"{base_name}_clean_version.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"干净版本已保存到: {output_path}")
    return final_content

def create_clean_version_from_compact(compact_file_path: str, output_path: str = None) -> str:
    """从紧凑位置格式文件创建干净版本"""
    if not os.path.exists(compact_file_path):
        raise FileNotFoundError(f"紧凑位置格式文件不存在: {compact_file_path}")
    
    with open(compact_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去掉位置信息标签
    # 匹配 <pos page=X bbox=...>文本</pos> 格式
    clean_content = re.sub(r'<pos page=\d+ bbox=[^>]+>(.*?)</pos>', r'\1', content)
    
    # 清理多余的空行和空格
    lines = clean_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:  # 只保留非空行
            cleaned_lines.append(line)
    
    # 重新组合内容
    final_content = '\n'.join(cleaned_lines)
    
    # 保存到文件
    if output_path is None:
        base_name = os.path.splitext(compact_file_path)[0]
        output_path = f"{base_name}_clean_version.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"干净版本已保存到: {output_path}")
    return final_content

def create_clean_version_from_table_aware(table_aware_file_path: str, output_path: str = None) -> str:
    """从表格感知格式文件创建干净版本"""
    if not os.path.exists(table_aware_file_path):
        raise FileNotFoundError(f"表格感知格式文件不存在: {table_aware_file_path}")
    
    with open(table_aware_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去掉位置信息标签
    # 匹配 <pos page=X bbox=...>文本</pos> 格式
    clean_content = re.sub(r'<pos page=\d+ bbox=[^>]+>(.*?)</pos>', r'\1', content)
    
    # 清理多余的空行和空格
    lines = clean_content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if line:  # 只保留非空行
            cleaned_lines.append(line)
    
    # 重新组合内容
    final_content = '\n'.join(cleaned_lines)
    
    # 保存到文件
    if output_path is None:
        base_name = os.path.splitext(table_aware_file_path)[0]
        output_path = f"{base_name}_clean_version.md"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    print(f"干净版本已保存到: {output_path}")
    return final_content

if __name__ == "__main__":
    print("正在创建干净版本用于内容对比...")
    
    # 从PDFLLM风格格式创建干净版本
    try:
        pdfllm_clean = create_clean_version_from_pdfllm("python_service/file/安联美元_pdfllm_style.md")
        print("✅ PDFLLM风格干净版本创建完成")
    except Exception as e:
        print(f"❌ PDFLLM风格干净版本创建失败: {e}")
    
    # 从紧凑位置格式创建干净版本
    try:
        compact_clean = create_clean_version_from_compact("python_service/file/安联美元_compact_pos.md")
        print("✅ 紧凑位置格式干净版本创建完成")
    except Exception as e:
        print(f"❌ 紧凑位置格式干净版本创建失败: {e}")
    
    # 从表格感知格式创建干净版本
    try:
        table_aware_clean = create_clean_version_from_table_aware("python_service/file/安联美元_table_aware.md")
        print("✅ 表格感知格式干净版本创建完成")
    except Exception as e:
        print(f"❌ 表格感知格式干净版本创建失败: {e}")
    
    print("\n转换完成！")
    print("\n📋 文件说明:")
    print("- PDFLLM风格干净版本: 去掉位置标签，保留完整内容")
    print("- 紧凑位置格式干净版本: 去掉位置标签，保留完整内容")
    print("- 表格感知格式干净版本: 去掉位置标签，保留表格结构和完整内容")
    print("\n💡 现在您可以对比这些干净版本与原始PDF，验证内容完整性！")
