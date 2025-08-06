#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Spring Security修复
验证API访问是否正常
"""

import requests
import time

def test_swagger_ui_access():
    """测试Swagger UI访问"""
    print("🌐 测试Swagger UI访问...")
    
    try:
        response = requests.get('http://localhost:8080/swagger-ui.html', timeout=10)
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

def test_api_docs_access():
    """测试API文档访问"""
    print("\n📚 测试API文档访问...")
    
    try:
        response = requests.get('http://localhost:8080/v3/api-docs', timeout=10)
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

def test_health_check():
    """测试健康检查"""
    print("\n🏥 测试健康检查...")
    
    try:
        response = requests.get('http://localhost:8080/actuator/health', timeout=10)
        if response.status_code == 200:
            print("✅ 健康检查可以访问")
            return True
        else:
            print(f"❌ 健康检查访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用服务器")
        return False
    except Exception as e:
        print(f"❌ 访问健康检查失败: {e}")
        return False

def test_root_access():
    """测试根路径访问"""
    print("\n🏠 测试根路径访问...")
    
    try:
        response = requests.get('http://localhost:8080/', timeout=10)
        if response.status_code in [200, 404]:  # 404也是正常的，表示路径存在但内容为空
            print("✅ 根路径可以访问")
            return True
        else:
            print(f"❌ 根路径访问失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到应用服务器")
        return False
    except Exception as e:
        print(f"❌ 访问根路径失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Spring Security修复测试")
    print("=" * 40)
    
    # 等待应用启动
    print("⏳ 等待应用启动...")
    time.sleep(15)
    
    # 测试各种访问
    results = []
    results.append(test_swagger_ui_access())
    results.append(test_api_docs_access())
    results.append(test_health_check())
    results.append(test_root_access())
    
    # 总结
    print("\n" + "=" * 40)
    if all(results):
        print("✅ 所有测试通过！Spring Security配置正确")
        print("\n💡 可以正常访问:")
        print("- Swagger UI: http://localhost:8080/swagger-ui.html")
        print("- API文档: http://localhost:8080/v3/api-docs")
        print("- 健康检查: http://localhost:8080/actuator/health")
    else:
        print("❌ 部分测试失败，请检查Spring Security配置")
        print("可能需要重启应用以应用新的安全配置")

if __name__ == "__main__":
    main() 