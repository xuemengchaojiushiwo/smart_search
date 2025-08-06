#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Swagger API 测试脚本
用于测试Java项目的API接口
"""

import requests
import json
import time

class SwaggerAPITester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_swagger_ui(self):
        """测试Swagger UI是否可访问"""
        print("🔍 测试 Swagger UI 访问...")
        try:
            response = self.session.get(f"{self.base_url}/swagger-ui/index.html")
            if response.status_code == 200:
                print("✅ Swagger UI 可访问")
                return True
            else:
                print(f"❌ Swagger UI 访问失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Swagger UI 访问异常: {e}")
            return False
    
    def test_api_docs(self):
        """测试API文档JSON是否可访问"""
        print("🔍 测试 API 文档 JSON...")
        try:
            response = self.session.get(f"{self.base_url}/v2/api-docs")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 文档获取成功，包含 {len(data.get('paths', {}))} 个接口")
                return True
            else:
                print(f"❌ API 文档获取失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 文档获取异常: {e}")
            return False
    
    def test_api_status(self):
        """测试API状态接口"""
        print("🔍 测试 API 状态接口...")
        try:
            response = self.session.get(f"{self.base_url}/api/test/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 状态正常: {data.get('data', {}).get('service', 'Unknown')}")
                return True
            else:
                print(f"❌ API 状态检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API 状态检查异常: {e}")
            return False
    
    def test_sample_data(self):
        """测试示例数据接口"""
        print("🔍 测试示例数据接口...")
        
        sample_endpoints = [
            "/api/test/knowledge/sample",
            "/api/test/knowledge/list/sample",
            "/api/test/chat/request/sample",
            "/api/test/search/request/sample",
            "/api/test/knowledge/dto/sample"
        ]
        
        success_count = 0
        for endpoint in sample_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    print(f"✅ {endpoint} - 成功")
                    success_count += 1
                else:
                    print(f"❌ {endpoint} - 失败 ({response.status_code})")
            except Exception as e:
                print(f"❌ {endpoint} - 异常: {e}")
        
        print(f"📊 示例数据接口测试完成: {success_count}/{len(sample_endpoints)} 成功")
        return success_count == len(sample_endpoints)
    
    def test_simulate_endpoints(self):
        """测试模拟接口"""
        print("🔍 测试模拟接口...")
        
        # 测试聊天模拟
        try:
            chat_request = {
                "question": "什么是知识库管理系统？",
                "userId": "test_user"
            }
            response = self.session.post(
                f"{self.base_url}/api/test/chat/simulate",
                json=chat_request
            )
            if response.status_code == 200:
                print("✅ 聊天模拟接口 - 成功")
            else:
                print(f"❌ 聊天模拟接口 - 失败 ({response.status_code})")
        except Exception as e:
            print(f"❌ 聊天模拟接口 - 异常: {e}")
        
        # 测试搜索模拟
        try:
            search_request = {
                "query": "知识管理",
                "page": 1,
                "size": 10,
                "categoryId": 1
            }
            response = self.session.post(
                f"{self.base_url}/api/test/search/simulate",
                json=search_request
            )
            if response.status_code == 200:
                print("✅ 搜索模拟接口 - 成功")
            else:
                print(f"❌ 搜索模拟接口 - 失败 ({response.status_code})")
        except Exception as e:
            print(f"❌ 搜索模拟接口 - 异常: {e}")
    
    def test_auth_endpoint(self):
        """测试认证接口"""
        print("🔍 测试认证接口...")
        try:
            login_request = {
                "username": "admin",
                "password": "password"
            }
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_request
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    print("✅ 认证接口 - 成功")
                    return True
                else:
                    print(f"❌ 认证接口 - 业务失败: {data.get('message')}")
                    return False
            else:
                print(f"❌ 认证接口 - HTTP失败 ({response.status_code})")
                return False
        except Exception as e:
            print(f"❌ 认证接口 - 异常: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 Swagger API 测试")
        print("=" * 50)
        
        tests = [
            ("Swagger UI 访问", self.test_swagger_ui),
            ("API 文档 JSON", self.test_api_docs),
            ("API 状态检查", self.test_api_status),
            ("示例数据接口", self.test_sample_data),
            ("模拟接口", self.test_simulate_endpoints),
            ("认证接口", self.test_auth_endpoint)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ 测试异常: {e}")
                results.append((test_name, False))
        
        # 输出测试结果
        print("\n" + "=" * 50)
        print("📊 测试结果汇总")
        print("=" * 50)
        
        success_count = 0
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                success_count += 1
        
        print(f"\n总计: {success_count}/{len(results)} 项测试通过")
        
        if success_count == len(results):
            print("🎉 所有测试通过！Swagger API 配置正常")
        else:
            print("⚠️  部分测试失败，请检查配置")
        
        return success_count == len(results)

def main():
    """主函数"""
    print("🔧 Swagger API 测试工具")
    print("=" * 50)
    
    # 创建测试器
    tester = SwaggerAPITester()
    
    # 运行测试
    success = tester.run_all_tests()
    
    if success:
        print("\n💡 使用说明:")
        print("1. 访问 Swagger UI: http://localhost:8080/swagger-ui/index.html")
        print("2. 查看 API 文档: http://localhost:8080/v2/api-docs")
        print("3. 使用测试接口获取示例数据")
        print("4. 在 Swagger UI 中测试 API 功能")
    else:
        print("\n🔧 故障排除:")
        print("1. 确保 Java 应用已启动")
        print("2. 检查端口 8080 是否被占用")
        print("3. 查看应用日志获取错误信息")
        print("4. 确认 Swagger 依赖已正确配置")

if __name__ == "__main__":
    main() 