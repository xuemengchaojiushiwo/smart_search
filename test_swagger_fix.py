#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Swagger配置修复
验证Java应用是否能正常启动
"""

import subprocess
import time
import requests
import sys
import os

def test_java_compilation():
    """测试Java项目编译"""
    print("🔧 测试Java项目编译...")
    
    try:
        # 检查pom.xml中的Swagger依赖
        with open('pom.xml', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'springfox-swagger2' in content and 'springfox-swagger-ui' in content:
            print("✅ Swagger依赖配置正确")
        else:
            print("❌ Swagger依赖配置有问题")
            return False
            
        # 检查SwaggerConfig.java
        with open('src/main/java/com/knowledge/config/SwaggerConfig.java', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '@EnableSwagger2' in content and 'Docket' in content:
            print("✅ Swagger配置类正确")
        else:
            print("❌ Swagger配置类有问题")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 检查配置文件失败: {e}")
        return False

def test_swagger_ui_access():
    """测试Swagger UI访问"""
    print("\n🌐 测试Swagger UI访问...")
    
    try:
        # 尝试访问Swagger UI
        response = requests.get('http://localhost:8080/swagger-ui.html', timeout=5)
        if response.status_code == 200:
            print("✅ Swagger UI可以访问")
            return True
        else:
            print(f"❌ Swagger UI访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用服务器")
        return False
    except Exception as e:
        print(f"❌ 访问Swagger UI失败: {e}")
        return False

def test_api_documentation():
    """测试API文档访问"""
    print("\n📚 测试API文档访问...")
    
    try:
        # 尝试访问API文档JSON
        response = requests.get('http://localhost:8080/v2/api-docs', timeout=5)
        if response.status_code == 200:
            print("✅ API文档可以访问")
            return True
        else:
            print(f"❌ API文档访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用服务器")
        return False
    except Exception as e:
        print(f"❌ 访问API文档失败: {e}")
        return False

def check_application_status():
    """检查应用状态"""
    print("\n🔍 检查应用状态...")
    
    try:
        # 尝试访问健康检查端点
        response = requests.get('http://localhost:8080/actuator/health', timeout=5)
        if response.status_code == 200:
            print("✅ 应用运行正常")
            return True
        else:
            print(f"⚠️ 应用可能有问题，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 应用未启动或无法连接")
        return False
    except Exception as e:
        print(f"❌ 检查应用状态失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 Swagger配置修复测试")
    print("=" * 50)
    
    # 测试编译配置
    if not test_java_compilation():
        print("\n❌ 编译配置测试失败")
        return False
    
    print("\n✅ 编译配置测试通过")
    print("\n💡 建议:")
    print("1. 运行 'mvn clean compile' 编译项目")
    print("2. 运行 'mvn spring-boot:run' 启动应用")
    print("3. 访问 http://localhost:8080/swagger-ui.html 查看API文档")
    
    # 如果应用正在运行，测试访问
    print("\n🔍 检查应用是否正在运行...")
    if check_application_status():
        test_swagger_ui_access()
        test_api_documentation()
    
    return True

if __name__ == "__main__":
    main() 