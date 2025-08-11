from typing import Dict, Any, List
import requests
import json
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
                f"{self.base_url}/api/categories/tree",
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
                    if result.get('code') == 200:
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
                    if result.get('code') == 200:
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
                    if result.get('code') == 200:
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
            'recommendations': False,
            'search_suggestions': False
        }
        
        try:
            # 1. 测试基础搜索
            print("1. 测试基础搜索...")
            search_data = {
                "query": "测试",
                "page": 1,
                "size": 10
            }
            
            response = requests.post(
                f"{self.base_url}/api/search",
                headers=self.headers,
                json=search_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("✅ 基础搜索成功")
                    results['basic_search'] = True
                else:
                    print(f"❌ 基础搜索失败: {result.get('message')}")
            else:
                print(f"❌ 基础搜索请求失败: {response.status_code}")
            
            # 2. 测试推荐问题
            print("2. 测试推荐问题...")
            response = requests.get(
                f"{self.base_url}/api/search/recommendations?limit=3",
                headers=self.headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("✅ 推荐问题成功")
                    results['recommendations'] = True
                else:
                    print(f"❌ 推荐问题失败: {result.get('message')}")
            else:
                print(f"❌ 推荐问题请求失败: {response.status_code}")
            
            # 3. 测试搜索建议
            print("3. 测试搜索建议...")
            response = requests.get(
                f"{self.base_url}/api/search/suggest?q=测试",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("✅ 搜索建议成功")
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
            'es_search': False
        }
        
        try:
            # 1. 测试Elasticsearch搜索（按Swagger定义使用GET+query params）
            print("1. 测试Elasticsearch搜索...")
            response = requests.get(
                f"{self.base_url}/api/elasticsearch/search",
                params={"query": "测试", "page": 1, "size": 10},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print("✅ ES搜索成功")
                    results['es_search'] = True
                else:
                    print(f"❌ ES搜索失败: {result.get('message')}")
            else:
                print(f"❌ ES搜索请求失败: {response.status_code}")
            
            # 不测健康检查与索引信息
                
        except Exception as e:
            print(f"❌ Elasticsearch集成测试异常: {e}")
        
        return results
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始完整系统功能测试")
        print("="*60)
        
        # 健康检查
        if not self.test_health_check():
            print("❌ 服务不可用，停止测试")
            return
        
        # 运行各模块测试
        self.test_results['category_management'] = self.test_category_management()
        self.test_results['knowledge_management'] = self.test_knowledge_management()
        self.test_results['search_functionality'] = self.test_search_functionality()
        self.test_results['elasticsearch_integration'] = self.test_elasticsearch_integration()

        # 退出登录接口（无状态，这里只做一次调用验证接口存在）
        try:
            resp = requests.post(f"{self.base_url}/api/auth/logout", timeout=5)
            if resp.status_code == 200:
                print("✅ 退出登录接口可用")
            else:
                print(f"⚠️  退出登录接口返回码: {resp.status_code}")
        except Exception as e:
            print(f"⚠️  退出登录接口调用异常: {e}")

        # RAG 对话测试（非严格验证，跑通链路即可）
        try:
            print("\n" + "="*50)
            print("测试RAG对话")
            print("="*50)
            # 先将PDF作为附件处理到某个知识ID（通过Java转调Python服务）
            pdf_path = os.path.join("python_service", "file", "安联美元.pdf")
            if os.path.exists(pdf_path):
                try:
                    with open(pdf_path, 'rb') as f:
                        files = {"file": ("安联美元.pdf", f, "application/pdf")}
                        # 这里使用知识ID=1，亦可改为上面创建的知识ID
                        r = requests.post(
                            f"{self.base_url}/api/knowledge/1/document",
                            files=files,
                            timeout=60
                        )
                    if r.status_code == 200:
                        body = r.json()
                        if body.get('code') == 200:
                            print("✅ PDF已处理并入库(经Java→Python)")
                        else:
                            print(f"⚠️  PDF处理失败: {body.get('message')}")
                    else:
                        print(f"⚠️  PDF处理返回码: {r.status_code}")
                except Exception as e:
                    print(f"⚠️  PDF处理异常: {e}")

            chat_req = {
                "question": "请基于安联美元这份PDF回答：这份文档的核心要点是什么？并标注引用的页码位置。",
                "sessionId": None
            }
            resp = requests.post(
                f"{self.base_url}/api/chat/rag",
                headers=self.headers,
                json=chat_req,
                timeout=15
            )
            if resp.status_code == 200:
                body = resp.json()
                if body.get("code") == 200:
                    print("✅ RAG对话成功")
                else:
                    print(f"⚠️  RAG对话返回: {body.get('message')}")
            else:
                print(f"⚠️  RAG对话请求失败: {resp.status_code}")
        except Exception as e:
            print(f"⚠️  RAG对话调用异常: {e}")
        
        # 生成测试报告
        self.generate_test_report()
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("完整系统功能测试报告")
        print("="*60)
        
        # 计算各模块成功率
        category_success = sum([
            self.test_results['category_management']['create_category'],
            self.test_results['category_management']['get_categories'],
            self.test_results['category_management']['update_category'],
            self.test_results['category_management']['delete_category']
        ])
        
        knowledge_success = sum([
            self.test_results['knowledge_management']['create_knowledge'],
            self.test_results['knowledge_management']['get_knowledge'],
            self.test_results['knowledge_management']['update_knowledge'],
            self.test_results['knowledge_management']['delete_knowledge']
        ])
        
        search_success = sum([
            self.test_results['search_functionality']['basic_search'],
            self.test_results['search_functionality']['recommendations'],
            self.test_results['search_functionality']['search_suggestions']
        ])
        
        es_success = sum([
            self.test_results['elasticsearch_integration']['es_search']
        ])
        
        total_tests = 12
        total_success = category_success + knowledge_success + search_success + es_success
        
        # 输出报告
        print(f"\n📋 Category Management:")
        print(f"  create_category: {'✅ 成功' if self.test_results['category_management']['create_category'] else '❌ 失败'}")
        print(f"  get_categories: {'✅ 成功' if self.test_results['category_management']['get_categories'] else '❌ 失败'}")
        print(f"  update_category: {'✅ 成功' if self.test_results['category_management']['update_category'] else '❌ 失败'}")
        print(f"  delete_category: {'✅ 成功' if self.test_results['category_management']['delete_category'] else '❌ 失败'}")
        print(f"  模块成功率: {category_success/4*100:.1f}% ({category_success}/4)")
        
        print(f"\n📋 Knowledge Management:")
        print(f"  create_knowledge: {'✅ 成功' if self.test_results['knowledge_management']['create_knowledge'] else '❌ 失败'}")
        print(f"  get_knowledge: {'✅ 成功' if self.test_results['knowledge_management']['get_knowledge'] else '❌ 失败'}")
        print(f"  update_knowledge: {'✅ 成功' if self.test_results['knowledge_management']['update_knowledge'] else '❌ 失败'}")
        print(f"  delete_knowledge: {'✅ 成功' if self.test_results['knowledge_management']['delete_knowledge'] else '❌ 失败'}")
        print(f"  模块成功率: {knowledge_success/4*100:.1f}% ({knowledge_success}/4)")
        
        print(f"\n📋 Search Functionality:")
        print(f"  basic_search: {'✅ 成功' if self.test_results['search_functionality']['basic_search'] else '❌ 失败'}")
        print(f"  recommendations: {'✅ 成功' if self.test_results['search_functionality']['recommendations'] else '❌ 失败'}")
        print(f"  search_suggestions: {'✅ 成功' if self.test_results['search_functionality']['search_suggestions'] else '❌ 失败'}")
        print(f"  模块成功率: {search_success/3*100:.1f}% ({search_success}/3)")
        
        print(f"\n📋 Elasticsearch Integration:")
        print(f"  es_search: {'✅ 成功' if self.test_results['elasticsearch_integration']['es_search'] else '❌ 失败'}")
        print(f"  模块成功率: {es_success/1*100:.1f}% ({es_success}/1)")
        
        print(f"\n📊 总体测试结果:")
        print(f"  总测试数: {total_tests}")
        print(f"  通过数: {total_success}")
        print(f"  失败数: {total_tests - total_success}")
        print(f"  总体成功率: {total_success/total_tests*100:.1f}%")
        
        # 保存详细报告
        report_file = "complete_system_test_report_fixed.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 详细测试报告已保存到: {report_file}")
        
        # 输出结论
        if total_success == total_tests:
            print("\n🎉 测试结论: 所有功能测试通过，系统运行正常！")
        elif total_success >= total_tests * 0.8:
            print(f"\n⚠️  测试结论: 系统基本正常，但存在一些问题，总体成功率{total_success/total_tests*100:.1f}%")
        elif total_success >= total_tests * 0.5:
            print(f"\n❌ 测试结论: 系统存在较多问题，需要修复，总体成功率{total_success/total_tests*100:.1f}%")
        else:
            print(f"\n❌ 测试结论: 系统存在严重问题，需要修复，总体成功率{total_success/total_tests*100:.1f}%")

def main():
    """主函数"""
    tester = CompleteSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
