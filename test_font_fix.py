#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 PyMuPDF Pro 字体路径修复
"""

import sys
import os
import logging

# 添加 python_service 目录到路径
sys.path.append('python_service')

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_font_fix():
    """测试字体路径修复"""
    print("🔧 测试 PyMuPDF Pro 字体路径修复")
    print("=" * 50)
    
    try:
        # 导入字体修复工具
        from python_service.pymupdf_font_fix import (
            find_system_fonts, 
            setup_pymupdf_pro_environment, 
            test_pymupdf_pro_initialization
        )
        
        print("1. 查找系统字体目录...")
        font_dirs = find_system_fonts()
        if font_dirs:
            print(f"✅ 找到 {len(font_dirs)} 个有效字体目录:")
            for font_dir in font_dirs:
                print(f"   - {font_dir}")
        else:
            print("❌ 未找到有效字体目录")
        
        print("\n2. 设置 PyMuPDF Pro 环境...")
        if setup_pymupdf_pro_environment():
            print("✅ 环境设置成功")
        else:
            print("❌ 环境设置失败")
        
        print("\n3. 测试 PyMuPDF Pro 初始化...")
        if test_pymupdf_pro_initialization():
            print("✅ PyMuPDF Pro 初始化成功")
        else:
            print("❌ PyMuPDF Pro 初始化失败")
        
        print("\n4. 测试文档处理功能...")
        try:
            import pymupdf
            print("✅ PyMuPDF 导入成功")
            
            # 创建一个简单的测试文档
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((50, 50), "测试文档")
            doc.save("test_output.pdf")
            doc.close()
            
            if os.path.exists("test_output.pdf"):
                print("✅ 文档创建成功")
                os.remove("test_output.pdf")
            else:
                print("❌ 文档创建失败")
                
        except Exception as e:
            print(f"❌ 文档处理测试失败: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_with_trial_key():
    """使用试用密钥测试"""
    print("\n🔑 使用试用密钥测试")
    print("=" * 30)
    
    try:
        import pymupdf.pro
        
        # 试用密钥
        TRIAL_KEY = "HZ1A5z94wQ9+85/85z+jkMX3"
        
        print(f"试用密钥: {TRIAL_KEY}")
        
        # 设置环境
        from python_service.pymupdf_font_fix import setup_pymupdf_pro_environment
        setup_pymupdf_pro_environment()
        
        # 尝试解锁
        try:
            pymupdf.pro.unlock(TRIAL_KEY)
            print("✅ PyMuPDF Pro 解锁成功")
            
            # 测试功能
            import pymupdf
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((50, 50), "PyMuPDF Pro 测试")
            doc.save("test_pro_output.pdf")
            doc.close()
            
            if os.path.exists("test_pro_output.pdf"):
                print("✅ PyMuPDF Pro 功能测试成功")
                os.remove("test_pro_output.pdf")
            else:
                print("❌ PyMuPDF Pro 功能测试失败")
                
        except Exception as e:
            print(f"❌ PyMuPDF Pro 解锁失败: {e}")
            
    except Exception as e:
        print(f"❌ 试用密钥测试失败: {e}")

if __name__ == "__main__":
    print("🚀 PyMuPDF Pro 字体路径修复测试")
    print("=" * 60)
    
    # 基本测试
    success = test_font_fix()
    
    if success:
        print("\n✅ 基本测试通过")
        # 试用密钥测试
        test_with_trial_key()
    else:
        print("\n❌ 基本测试失败")
    
    print("\n" + "=" * 60)
    print("测试完成") 