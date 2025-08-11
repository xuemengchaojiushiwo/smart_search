#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统功能测试脚本
测试Java服务的类目管理、知识管理、搜索功能
"""

import requests
import json
import time
from typing import Dict, Any, List
import os

class CompleteSystemTester:
    def __init__(self):
        self.base_url = "http://localhost:8080"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.test_results = {}
        
    def test_health_check(self) -> bool:
        """测试服务健康状态"""
        try:
            # 尝试访问Swagger端点来验证服务可用性
            response = requests.get(f"{self.base_url}/swagger-ui.html", timeout=5)
            if response.status_code == 200:
                print("✅ Java服务健康检查通过 (通过Swagger端点)")
                return True
            else:
                print(f"❌ Java服务健康检查失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Java服务连接失败: {e}")
            return False
    
    def test_category_management(self) -> Dict[str, Any]:
        """测试类目管理功能"""
        print("\n" + "="*50)
        print("测试类目管理功能")
        print("="*50)
        
        results = {
            'create_category': False,
            'get_categories': False,
            'update_category': False,
            'delete_category': False,
            'category_id': None
        }
        
        try:
            # 1. 创建类目
            print("1. 测试创建类目...")
            category_data = {
                "name": "测试类目",
                "level": 1,
                "description": "这是一个测试类目",
                "parentId": None,
                "sortOrder": 1
            }
            
            response = requests.post(
                f"{self.base_url}/api/categories",
                headers=self.headers,
                json=category_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    category_id = result['data']['id']
                    results['category_id'] = category_id
                    results['create_category'] = True
                    print(f"✅ 创建类目成功，ID: {category_id}")
                else:
                    print(f"❌ 创建类目失败: {result.get('message')}")
            else:
                print(f"❌ 创建类目请求失败: {response.status_code}")
            
            # 2. 获取类目列表
            print("2. 测试获取类目列表...")
            response = requests.get(
                f"{self.base_url}/api/categories",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    categories = result['data']
                    print(f"✅ 获取类目列表成功，共{len(categories)}个类目")
                    results['get_categories'] = True
                else:
                    print(f"❌ 获取类目列表失败: {result.get('message')}")
            else:
                print(f"❌ 获取类目列表请求失败: {response.status_code}")
            
            # 3. 更新类目
            if results['category_id']:
                print("3. 测试更新类目...")
                update_data = {
                    "name": "更新后的测试类目",
                    "level": 1,
                    "description": "这是更新后的测试类目描述",
                    "parentId": None,
                    "sortOrder": 2
                }
                
                response = requests.put(
                    f"{self.base_url}/api/categories/{results['category_id']}",
                    headers=self.headers,
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        print("✅ 更新类目成功")
                        results['update_category'] = True
                    else:
                        print(f"❌ 更新类目失败: {result.get('message')}")
                else:
                    print(f"❌ 更新类目请求失败: {response.status_code}")
            
            # 4. 删除类目
            if results['category_id']:
                print("4. 测试删除类目...")
                response = requests.delete(
                    f"{self.base_url}/api/categories/{results['category_id']}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        print("✅ 删除类目成功")
                        results['delete_category'] = True
                    else:
                        print(f"❌ 删除类目失败: {result.get('message')}")
                else:
                    print(f"❌ 删除类目请求失败: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ 类目管理测试异常: {e}")
        
        return results
    
    def test_knowledge_management(self) -> Dict[str, Any]:
        """测试知识管理功能"""
        print("\n" + "="*50)
        print("测试知识管理功能")
        print("="*50)
        
        results = {
            'create_knowledge': False,
            'get_knowledge': False,
            'update_knowledge': False,
            'delete_knowledge': False,
            'knowledge_id': None
        }
        
        try:
            # 1. 创建知识
            print("1. 测试创建知识...")
            knowledge_data = {
                "name": "测试知识标题",
                "description": "这是测试知识的内容，包含一些重要的信息用于测试。",
                "categoryId": 1,
                "tags": ["测试", "示例"]
            }
            
            response = requests.post(
                f"{self.base_url}/api/knowledge",
                headers=self.headers,
                json=knowledge_data,
                timeout=10
            )
            
                            if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == 200:
                        knowledge_id = result['data']['id']
                        results['knowledge_id'] = knowledge_id
                        results['create_knowledge'] = True
                        print(f"✅ 创建知识成功，ID: {knowledge_id}")
                    else:
                        print(f"❌ 创建知识失败: {result.get('message')}")
            else:
                print(f"❌ 创建知识请求失败: {response.status_code}")
            
            # 2. 获取知识详情
            if results['knowledge_id']:
                print("2. 测试获取知识详情...")
                response = requests.get(
                    f"{self.base_url}/api/knowledge/{results['knowledge_id']}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("✅ 获取知识详情成功")
                        results['get_knowledge'] = True
                    else:
                        print(f"❌ 获取知识详情失败: {result.get('message')}")
                else:
                    print(f"❌ 获取知识详情请求失败: {response.status_code}")
            
            # 3. 更新知识
            if results['knowledge_id']:
                print("3. 测试更新知识...")
                update_data = {
                    "name": "更新后的测试知识标题",
                    "description": "这是更新后的测试知识内容，包含更多信息。",
                    "categoryId": 1,
                    "tags": ["测试", "示例", "更新"]
                }
                
                response = requests.put(
                    f"{self.base_url}/api/knowledge/{results['knowledge_id']}",
                    headers=self.headers,
                    json=update_data,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("✅ 更新知识成功")
                        results['update_knowledge'] = True
                    else:
                        print(f"❌ 更新知识失败: {result.get('message')}")
                else:
                    print(f"❌ 更新知识请求失败: {response.status_code}")
            
            # 4. 删除知识
            if results['knowledge_id']:
                print("4. 测试删除知识...")
                response = requests.delete(
                    f"{self.base_url}/api/knowledge/{results['knowledge_id']}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        print("✅ 删除知识成功")
                        results['delete_knowledge'] = True
                    else:
                        print(f"❌ 删除知识失败: {result.get('message')}")
                else:
                    print(f"❌ 删除知识请求失败: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ 知识管理测试异常: {e}")
        
        return results
    
    def test_search_functionality(self) -> Dict[str, Any]:
        """测试搜索功能"""
        print("\n" + "="*50)
        print("测试搜索功能")
        print("="*50)
        
        results = {
            'basic_search': False,
            'advanced_search': False,
            'search_suggestions': False
        }
        
        try:
            # 1. 基础搜索
            print("1. 测试基础搜索...")
            search_params = {
                "query": "测试",
                "page": 1,
                "size": 10
            }
            
            response = requests.get(
                f"{self.base_url}/api/search",
                headers=self.headers,
                params=search_params,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    search_results = result['data']
                    print(f"✅ 基础搜索成功，找到{len(search_results.get('content', []))}条结果")
                    results['basic_search'] = True
                else:
                    print(f"❌ 基础搜索失败: {result.get('message')}")
            else:
                print(f"❌ 基础搜索请求失败: {response.status_code}")
            
            # 2. 高级搜索
            print("2. 测试高级搜索...")
            advanced_search_data = {
                "query": "测试",
                "categoryId": None,
                "tags": ["测试"],
                "startDate": None,
                "endDate": None,
                "page": 1,
                "size": 10
            }
            
            response = requests.post(
                f"{self.base_url}/api/search/advanced",
                headers=self.headers,
                json=advanced_search_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    search_results = result['data']
                    print(f"✅ 高级搜索成功，找到{len(search_results.get('content', []))}条结果")
                    results['advanced_search'] = True
                else:
                    print(f"❌ 高级搜索失败: {result.get('message')}")
            else:
                print(f"❌ 高级搜索请求失败: {response.status_code}")
            
            # 3. 搜索建议
            print("3. 测试搜索建议...")
            response = requests.get(
                f"{self.base_url}/api/search/suggestions",
                headers=self.headers,
                params={"query": "测试"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    suggestions = result['data']
                    print(f"✅ 搜索建议成功，获得{len(suggestions)}条建议")
                    results['search_suggestions'] = True
                else:
                    print(f"❌ 搜索建议失败: {result.get('message')}")
            else:
                print(f"❌ 搜索建议请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 搜索功能测试异常: {e}")
        
        return results
    
    def test_elasticsearch_integration(self) -> Dict[str, Any]:
        """测试Elasticsearch集成"""
        print("\n" + "="*50)
        print("测试Elasticsearch集成")
        print("="*50)
        
        results = {
            'es_health': False,
            'es_search': False,
            'es_index_info': False
        }
        
        try:
            # 1. 检查ES健康状态
            print("1. 检查Elasticsearch健康状态...")
            response = requests.get(
                f"{self.base_url}/api/elasticsearch/health",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    es_status = result['data']
                    print(f"✅ ES健康检查成功: {es_status}")
                    results['es_health'] = True
                else:
                    print(f"❌ ES健康检查失败: {result.get('message')}")
            else:
                print(f"❌ ES健康检查请求失败: {response.status_code}")
            
            # 2. ES搜索测试
            print("2. 测试Elasticsearch搜索...")
            es_search_data = {
                "query": "测试",
                "index": "knowledge",
                "size": 5
            }
            
            response = requests.post(
                f"{self.base_url}/api/elasticsearch/search",
                headers=self.headers,
                json=es_search_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    es_results = result['data']
                    print(f"✅ ES搜索成功，找到{len(es_results.get('hits', []))}条结果")
                    results['es_search'] = True
                else:
                    print(f"❌ ES搜索失败: {result.get('message')}")
            else:
                print(f"❌ ES搜索请求失败: {response.status_code}")
            
            # 3. 获取索引信息
            print("3. 获取索引信息...")
            response = requests.get(
                f"{self.base_url}/api/elasticsearch/indices",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    indices_info = result['data']
                    print(f"✅ 获取索引信息成功: {indices_info}")
                    results['es_index_info'] = True
                else:
                    print(f"❌ 获取索引信息失败: {result.get('message')}")
            else:
                print(f"❌ 获取索引信息请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Elasticsearch集成测试异常: {e}")
        
        return results
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整系统功能测试")
        print("="*60)
        
        # 检查服务健康状态
        if not self.test_health_check():
            print("❌ 服务不可用，停止测试")
            return
        
        # 测试各个功能模块
        self.test_results['category_management'] = self.test_category_management()
        self.test_results['knowledge_management'] = self.test_knowledge_management()
        self.test_results['search_functionality'] = self.test_search_functionality()
        self.test_results['elasticsearch_integration'] = self.test_elasticsearch_integration()
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("完整系统功能测试报告")
        print("="*60)
        
        # 计算总体成功率
        total_tests = 0
        passed_tests = 0
        
        for module_name, module_results in self.test_results.items():
            print(f"\n📋 {module_name.replace('_', ' ').title()}:")
            module_tests = 0
            module_passed = 0
            
            for test_name, test_result in module_results.items():
                if test_name != 'category_id' and test_name != 'knowledge_id':
                    module_tests += 1
                    total_tests += 1
                    if test_result:
                        module_passed += 1
                        passed_tests += 1
                        status = "✅ 通过"
                    else:
                        status = "❌ 失败"
                    print(f"  {test_name}: {status}")
            
            success_rate = (module_passed / module_tests * 100) if module_tests > 0 else 0
            print(f"  模块成功率: {success_rate:.1f}% ({module_passed}/{module_tests})")
        
        # 总体统计
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\n📊 总体测试结果:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过数: {passed_tests}")
        print(f"  失败数: {total_tests - passed_tests}")
        print(f"  总体成功率: {overall_success_rate:.1f}%")
        
        # 保存详细报告
        report_file = "complete_system_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        print(f"\n📄 详细测试报告已保存到: {report_file}")
        
        # 测试结论
        if overall_success_rate >= 80:
            print(f"\n🎉 测试结论: 系统功能正常，总体成功率{overall_success_rate:.1f}%")
        elif overall_success_rate >= 60:
            print(f"\n⚠️ 测试结论: 系统基本可用，但存在一些问题，总体成功率{overall_success_rate:.1f}%")
        else:
            print(f"\n❌ 测试结论: 系统存在严重问题，需要修复，总体成功率{overall_success_rate:.1f}%")

def main():
    """主函数"""
    tester = CompleteSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 