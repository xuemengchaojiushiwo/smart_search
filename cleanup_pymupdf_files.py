#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyMuPDF Pro 相关文件清理工具
分析当前项目中的PyMuPDF Pro相关文件，帮助决定哪些需要保留
"""

import os
import shutil
from pathlib import Path

def analyze_pymupdf_files():
    """分析PyMuPDF Pro相关文件"""
    print("🔍 分析 PyMuPDF Pro 相关文件")
    print("=" * 60)
    
    # 当前目录
    current_dir = Path(".")
    
    # 分类文件
    files_by_category = {
        "核心应用文件": [],
        "配置文件": [],
        "测试文件": [],
        "文档文件": [],
        "临时文件": [],
        "其他": []
    }
    
    # 扫描文件
    for file_path in current_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            file_name = file_path.name.lower()
            
            # 核心应用文件
            if any(keyword in file_name for keyword in ["app", "service", "main"]):
                if "pymupdf" in file_name or "pro" in file_name:
                    files_by_category["核心应用文件"].append(file_path)
                else:
                    files_by_category["其他"].append(file_path)
            
            # 配置文件
            elif any(keyword in file_name for keyword in ["config", "requirements"]):
                if "pymupdf" in file_name or "pro" in file_name:
                    files_by_category["配置文件"].append(file_path)
                else:
                    files_by_category["其他"].append(file_path)
            
            # 测试文件
            elif any(keyword in file_name for keyword in ["test", "demo", "example"]):
                if "pymupdf" in file_name or "pro" in file_name:
                    files_by_category["测试文件"].append(file_path)
                else:
                    files_by_category["其他"].append(file_path)
            
            # 文档文件
            elif any(keyword in file_name for keyword in ["readme", "guide", "analysis", "status", "migration"]):
                if "pymupdf" in file_name or "pro" in file_name:
                    files_by_category["文档文件"].append(file_path)
                else:
                    files_by_category["其他"].append(file_path)
            
            # 临时文件
            elif any(keyword in file_name for keyword in ["temp", "tmp", "cache", "log"]):
                files_by_category["临时文件"].append(file_path)
            
            # 其他
            else:
                files_by_category["其他"].append(file_path)
    
    return files_by_category

def print_file_analysis(files_by_category):
    """打印文件分析结果"""
    for category, files in files_by_category.items():
        if files:
            print(f"\n📁 {category} ({len(files)} 个文件):")
            for file_path in sorted(files):
                size = file_path.stat().st_size
                size_str = f"{size:,} bytes" if size < 1024 else f"{size/1024:.1f} KB"
                print(f"   📄 {file_path} ({size_str})")

def get_recommendations(files_by_category):
    """获取文件保留建议"""
    print("\n💡 文件保留建议:")
    print("=" * 60)
    
    recommendations = {
        "保留": [],
        "可选保留": [],
        "可删除": [],
        "需要评估": []
    }
    
    # 核心应用文件 - 保留
    for file_path in files_by_category["核心应用文件"]:
        if "app_pymupdf_pro.py" in str(file_path):
            recommendations["保留"].append((file_path, "主要的PyMuPDF Pro应用文件"))
        elif "app_with_pymupdf_pro.py" in str(file_path):
            recommendations["保留"].append((file_path, "混合处理策略应用文件"))
        else:
            recommendations["需要评估"].append((file_path, "需要根据实际使用情况决定"))
    
    # 配置文件 - 保留
    for file_path in files_by_category["配置文件"]:
        if "requirements_pymupdf_pro.txt" in str(file_path):
            recommendations["保留"].append((file_path, "PyMuPDF Pro依赖配置"))
        elif "config_pymupdf_pro.py" in str(file_path):
            recommendations["保留"].append((file_path, "PyMuPDF Pro配置文件"))
        else:
            recommendations["需要评估"].append((file_path, "需要根据实际使用情况决定"))
    
    # 测试文件 - 可选保留
    for file_path in files_by_category["测试文件"]:
        if "test_pymupdf_pro_with_key.py" in str(file_path):
            recommendations["可选保留"].append((file_path, "PyMuPDF Pro功能测试"))
        elif "test_font_fix.py" in str(file_path):
            recommendations["保留"].append((file_path, "字体路径修复测试"))
        elif "simple_pymupdf_test.py" in str(file_path):
            recommendations["可选保留"].append((file_path, "简化测试脚本"))
        else:
            recommendations["可删除"].append((file_path, "临时测试文件"))
    
    # 文档文件 - 可选保留
    for file_path in files_by_category["文档文件"]:
        if "pymupdf_pro_status.md" in str(file_path):
            recommendations["可选保留"].append((file_path, "状态文档"))
        elif "migration_guide_pymupdf_pro.md" in str(file_path):
            recommendations["可选保留"].append((file_path, "迁移指南"))
        elif "pymupdf_pro_analysis.md" in str(file_path):
            recommendations["可选保留"].append((file_path, "技术分析"))
        else:
            recommendations["可删除"].append((file_path, "临时文档"))
    
    # 临时文件 - 可删除
    for file_path in files_by_category["临时文件"]:
        recommendations["可删除"].append((file_path, "临时文件"))
    
    return recommendations

def print_recommendations(recommendations):
    """打印建议"""
    for category, files in recommendations.items():
        if files:
            print(f"\n{category.upper()}:")
            for file_path, reason in files:
                print(f"   📄 {file_path}")
                print(f"      💬 {reason}")

def create_cleanup_script(recommendations):
    """创建清理脚本"""
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyMuPDF Pro 文件清理脚本
根据分析结果自动清理不需要的文件
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    \"\"\"清理不需要的文件\"\"\"
    print("🧹 开始清理 PyMuPDF Pro 相关文件")
    print("=" * 50)
    
    # 要删除的文件列表
    files_to_delete = [
'''
    
    for category, files in recommendations.items():
        if category == "可删除":
            for file_path, reason in files:
                script_content += f'        "{file_path}",  # {reason}\n'
    
    script_content += '''    ]
    
    # 要移动的文件列表（移动到backup目录）
    files_to_move = [
'''
    
    for category, files in recommendations.items():
        if category == "可选保留":
            for file_path, reason in files:
                script_content += f'        "{file_path}",  # {reason}\n'
    
    script_content += '''    ]
    
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
    
    print(f"\\n✅ 清理完成: 删除 {deleted_count} 个文件, 移动 {moved_count} 个文件")
    print(f"📁 备份文件位置: {backup_dir}")

if __name__ == "__main__":
    cleanup_files()
'''
    
    with open("cleanup_pymupdf_auto.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"\n📝 已生成自动清理脚本: cleanup_pymupdf_auto.py")

def main():
    """主函数"""
    print("🚀 PyMuPDF Pro 文件清理分析工具")
    print("=" * 60)
    
    # 分析文件
    files_by_category = analyze_pymupdf_files()
    
    # 打印分析结果
    print_file_analysis(files_by_category)
    
    # 获取建议
    recommendations = get_recommendations(files_by_category)
    
    # 打印建议
    print_recommendations(recommendations)
    
    # 创建清理脚本
    create_cleanup_script(recommendations)
    
    print("\n" + "=" * 60)
    print("📋 总结:")
    print("1. 保留核心应用文件 (app_pymupdf_pro.py, pymupdf_font_fix.py)")
    print("2. 保留配置文件 (requirements_pymupdf_pro.txt)")
    print("3. 可选保留测试和文档文件")
    print("4. 删除临时文件")
    print("\n💡 建议:")
    print("- 如果决定使用PyMuPDF Pro: 保留所有相关文件")
    print("- 如果决定不使用PyMuPDF Pro: 可以删除大部分相关文件")
    print("- 如果不确定: 先移动到backup目录，需要时可以恢复")

if __name__ == "__main__":
    main() 