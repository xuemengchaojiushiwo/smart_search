#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
清理重复的APP文件脚本
保留最有用的版本，删除重复文件
"""

import os
import shutil
from pathlib import Path

def analyze_app_files():
    """分析APP文件"""
    python_service_dir = Path("python_service")
    
    app_files = {
        "app.py": {
            "description": "基础版本 - 传统文档处理",
            "features": ["基础文档处理", "传统分块", "简单配置"],
            "status": "legacy"
        },
        "app_pymupdf_pro.py": {
            "description": "当前使用版本 - PyMuPDF Pro集成",
            "features": ["PyMuPDF Pro", "PyMuPDF4LLM", "结构化分块", "多格式支持"],
            "status": "current"
        },
        "app_with_geekai.py": {
            "description": "极客智坊API集成版本",
            "features": ["极客智坊API", "外部LLM", "高级对话"],
            "status": "alternative"
        },
        "app_with_pymupdf_pro.py": {
            "description": "另一个PyMuPDF Pro版本",
            "features": ["PyMuPDF Pro", "混合处理", "回退机制"],
            "status": "duplicate"
        }
    }
    
    print("=== APP文件分析 ===")
    for filename, info in app_files.items():
        file_path = python_service_dir / filename
        if file_path.exists():
            size = file_path.stat().st_size / 1024  # KB
            print(f"✅ {filename}")
            print(f"   描述: {info['description']}")
            print(f"   功能: {', '.join(info['features'])}")
            print(f"   大小: {size:.1f} KB")
            print(f"   状态: {info['status']}")
            print()
        else:
            print(f"❌ {filename} - 文件不存在")
            print()
    
    return app_files

def recommend_cleanup():
    """推荐清理方案"""
    print("=== 清理建议 ===")
    
    # 保留的文件
    keep_files = [
        "app_pymupdf_pro.py",  # 当前使用的版本，功能最完整
        "app_with_geekai.py",  # 极客智坊集成版本，作为备选
    ]
    
    # 可以删除的文件
    delete_files = [
        "app.py",  # 基础版本，功能较简单
        "app_with_pymupdf_pro.py",  # 重复的PyMuPDF Pro版本
    ]
    
    print("📁 建议保留的文件:")
    for file in keep_files:
        print(f"   ✅ {file}")
    
    print("\n🗑️ 建议删除的文件:")
    for file in delete_files:
        print(f"   ❌ {file}")
    
    print("\n📋 清理理由:")
    print("1. app_pymupdf_pro.py - 当前使用的版本，功能最完整")
    print("2. app_with_geekai.py - 极客智坊集成，作为备选方案")
    print("3. app.py - 基础版本，功能已被其他版本覆盖")
    print("4. app_with_pymupdf_pro.py - 与app_pymupdf_pro.py功能重复")
    
    return keep_files, delete_files

def backup_files(files_to_delete):
    """备份要删除的文件"""
    backup_dir = Path("backup_apps")
    backup_dir.mkdir(exist_ok=True)
    
    print(f"\n📦 备份文件到: {backup_dir}")
    
    for filename in files_to_delete:
        src_path = Path("python_service") / filename
        if src_path.exists():
            dst_path = backup_dir / filename
            shutil.copy2(src_path, dst_path)
            print(f"   ✅ 已备份: {filename}")
        else:
            print(f"   ⚠️ 文件不存在: {filename}")

def delete_files_list(files_to_delete):
    """删除文件"""
    print(f"\n🗑️ 删除重复文件:")
    
    for filename in files_to_delete:
        file_path = Path("python_service") / filename
        if file_path.exists():
            file_path.unlink()
            print(f"   ✅ 已删除: {filename}")
        else:
            print(f"   ⚠️ 文件不存在: {filename}")

def update_start_scripts():
    """更新启动脚本"""
    print(f"\n🔧 更新启动脚本:")
    
    # 更新主启动脚本
    start_script = Path("start_python_service.bat")
    if start_script.exists():
        with open(start_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 确保使用app_pymupdf_pro.py
        if 'app_pymupdf_pro.py' not in content:
            content = content.replace('python app.py', 'python app_pymupdf_pro.py')
            with open(start_script, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ 已更新: {start_script}")
        else:
            print(f"   ✅ 无需更新: {start_script}")

def create_geekai_start_script():
    """创建极客智坊启动脚本"""
    geekai_script = Path("start_geekai_service.bat")
    
    if not geekai_script.exists():
        content = """@echo off
echo ========================================
echo 极客智坊API服务启动脚本
echo ========================================

echo.
echo 启动极客智坊API集成服务...
echo 服务将在 http://localhost:8000 启动
echo.
echo 按 Ctrl+C 停止服务
echo.

cd python_service
python app_with_geekai.py

pause
"""
        with open(geekai_script, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ 已创建: {geekai_script}")

def update_readme():
    """更新README文件"""
    readme_path = Path("python_service/README.md")
    
    if readme_path.exists():
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 添加APP文件说明
        app_section = """

## APP文件说明

### 主要应用文件

1. **app_pymupdf_pro.py** (推荐使用)
   - 集成PyMuPDF Pro和PyMuPDF4LLM
   - 支持多种文档格式的智能处理
   - 结构化分块和语义保持
   - 启动命令: `python app_pymupdf_pro.py`

2. **app_with_geekai.py** (备选方案)
   - 集成极客智坊API
   - 外部LLM服务支持
   - 高级对话功能
   - 启动命令: `python app_with_geekai.py`

### 已删除的重复文件

- `app.py` - 基础版本，功能已被其他版本覆盖
- `app_with_pymupdf_pro.py` - 与app_pymupdf_pro.py功能重复

### 启动方式

```bash
# 使用PyMuPDF Pro版本 (推荐)
python app_pymupdf_pro.py

# 使用极客智坊API版本
python app_with_geekai.py
```
"""
        
        if "APP文件说明" not in content:
            content += app_section
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ 已更新: {readme_path}")

def main():
    """主函数"""
    print("🧹 开始清理重复的APP文件...")
    print()
    
    # 分析文件
    app_files = analyze_app_files()
    
    # 获取清理建议
    keep_files, delete_files = recommend_cleanup()
    
    # 询问用户确认
    print("\n❓ 是否执行清理操作？")
    print("输入 'y' 确认清理，其他键取消:")
    
    user_input = input().strip().lower()
    
    if user_input == 'y':
        print("\n🚀 开始执行清理...")
        
        # 备份文件
        backup_files(delete_files)
        
        # 删除文件
        delete_files_list(delete_files)
        
        # 更新启动脚本
        update_start_scripts()
        
        # 创建极客智坊启动脚本
        create_geekai_start_script()
        
        # 更新README
        update_readme()
        
        print("\n✅ 清理完成！")
        print("\n📋 清理总结:")
        print(f"- 保留了 {len(keep_files)} 个核心文件")
        print(f"- 删除了 {len(delete_files)} 个重复文件")
        print(f"- 备份文件保存在 backup_apps/ 目录")
        print(f"- 更新了启动脚本和文档")
        
    else:
        print("\n❌ 取消清理操作")

if __name__ == "__main__":
    main()
