#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加安联美元相关知识的脚本
通过调用现有的API接口添加10条知识到数据库和Elasticsearch
"""

import requests
import json
import time
from datetime import datetime, timedelta

# API配置
BASE_URL = "http://localhost:8080"
API_ENDPOINT = f"{BASE_URL}/api/knowledge"  # 使用JSON格式的接口

# 认证token
AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiIyMjIyMiIsInJvbGUiOiJVU0VSIiwiaWF0IjoxNzU3NjYzNDQxLCJleHAiOjE3NTgyNjgyNDF9.ujG18JNg0GiyjbfvnjBz4hL9Gd1O_I7-wh2VXo51unxotPBjWsb2eGjHJmJGGWJDAPTfty94BHtiG-i4sGCQHw"

# 请求头
HEADERS = {
    'Authorization': f'Bearer {AUTH_TOKEN}',
    'Content-Type': 'application/json'
}

# 安联美元相关的知识数据
ALLIANZ_KNOWLEDGE_DATA = [
    {
        "name": "安联美元债券基金投资指南",
        "description": "安联美元债券基金是一种专注于美元债券市场的投资工具，为投资者提供稳定的收益和较低的风险。该基金主要投资于美国国债、企业债券和机构债券，适合追求稳健收益的投资者。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "债券", "基金", "投资"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元债券基金投资指南"
    },
    {
        "name": "安联美元货币市场基金产品介绍",
        "description": "安联美元货币市场基金是安联集团推出的短期投资产品，主要投资于美元货币市场工具，包括短期国债、商业票据和银行存款等。该产品具有流动性强、风险低、收益稳定的特点。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "货币市场", "基金", "短期投资"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元货币市场基金产品介绍"
    },
    {
        "name": "安联美元指数基金投资策略",
        "description": "安联美元指数基金采用被动投资策略，跟踪美元指数表现。该基金通过投资美元相关的金融工具，为投资者提供美元汇率变动的投资机会。适合看好美元走势的投资者。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "指数基金", "投资策略", "汇率"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元指数基金投资策略"
    },
    {
        "name": "安联美元高收益债券基金分析",
        "description": "安联美元高收益债券基金专注于投资高收益美元债券，包括垃圾债券和新兴市场债券。该基金追求较高的收益，但风险相对较高，适合风险承受能力较强的投资者。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "高收益债券", "垃圾债券", "新兴市场"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元高收益债券基金分析"
    },
    {
        "name": "安联美元股票基金投资组合",
        "description": "安联美元股票基金主要投资于美国股票市场，包括大盘股、中盘股和小盘股。该基金采用主动管理策略，通过精选个股和行业配置，为投资者提供长期资本增值机会。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "股票基金", "美国股市", "投资组合"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元股票基金投资组合"
    },
    {
        "name": "安联美元混合型基金配置策略",
        "description": "安联美元混合型基金同时投资于股票和债券，通过动态调整股债比例来平衡风险和收益。该基金适合追求稳健增长、风险偏好中等的投资者。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "混合型基金", "股债配置", "平衡投资"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元混合型基金配置策略"
    },
    {
        "name": "安联美元ETF产品线介绍",
        "description": "安联美元ETF产品线包括多种美元相关的交易所交易基金，涵盖债券、股票、商品等不同资产类别。ETF具有交易灵活、费用低廉、透明度高的特点。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "ETF", "交易所交易基金", "产品线"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元ETF产品线介绍"
    },
    {
        "name": "安联美元量化投资基金策略",
        "description": "安联美元量化投资基金采用量化投资策略，通过数学模型和算法进行投资决策。该基金利用大数据分析和机器学习技术，追求超越市场的超额收益。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "量化投资", "算法交易", "大数据"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元量化投资基金策略"
    },
    {
        "name": "安联美元另类投资基金",
        "description": "安联美元另类投资基金投资于非传统资产类别，包括私募股权、房地产、基础设施、商品等。该基金为投资者提供与传统投资低相关性的收益来源。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "另类投资", "私募股权", "房地产"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元另类投资基金"
    },
    {
        "name": "安联美元ESG主题投资基金",
        "description": "安联美元ESG主题投资基金专注于环境、社会和治理(ESG)因素，投资于符合可持续发展理念的美元资产。该基金在追求财务回报的同时，也关注社会和环境责任。",
        "parentId": None,
        "nodeType": "doc",
        "tags": ["安联", "美元", "ESG", "可持续发展", "社会责任投资"],
        "effectiveStartTime": "2025-01-01T00:00:00",
        "effectiveEndTime": "2025-12-31T23:59:59",
        "changeReason": "新增安联美元ESG主题投资基金"
    }
]

def add_knowledge(knowledge_data):
    """添加单条知识"""
    try:
        # 准备请求数据
        data = {
            'name': knowledge_data['name'],
            'description': knowledge_data['description'],
            'parentId': knowledge_data['parentId'],
            'nodeType': knowledge_data['nodeType'],
            'tags': knowledge_data['tags'],
            'effectiveStartTime': knowledge_data['effectiveStartTime'],
            'effectiveEndTime': knowledge_data['effectiveEndTime'],
            'changeReason': knowledge_data['changeReason'],
            'workspaces': ['default']  # 添加默认工作空间
        }
        
        # 发送POST请求
        response = requests.post(API_ENDPOINT, json=data, headers=HEADERS, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print(f"✅ 成功添加知识: {knowledge_data['name']}")
                print(f"   知识ID: {result.get('data', {}).get('id', 'N/A')}")
                return True
            else:
                print(f"❌ 添加知识失败: {knowledge_data['name']}")
                print(f"   错误信息: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ 请求失败: {knowledge_data['name']}")
            print(f"   HTTP状态码: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 添加知识异常: {knowledge_data['name']}")
        print(f"   异常信息: {str(e)}")
        return False

def test_search():
    """测试搜索功能"""
    print("\n🔍 测试搜索功能...")
    
    # 测试搜索API
    search_url = f"{BASE_URL}/api/knowledge/search"
    search_data = {
        'query': '安联美元',
        'page': 1,
        'size': 10
    }
    
    try:
        response = requests.post(search_url, json=search_data, headers=HEADERS, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                data = result.get('data', {})
                total = data.get('total', 0)
                items = data.get('items', [])
                print(f"✅ 搜索成功，找到 {total} 条相关结果")
                for i, item in enumerate(items[:5], 1):  # 只显示前5条
                    print(f"   {i}. {item.get('name', 'N/A')}")
                return True
            else:
                print(f"❌ 搜索失败: {result.get('message', 'Unknown error')}")
                return False
        else:
            print(f"❌ 搜索请求失败，HTTP状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 搜索异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 开始添加安联美元相关知识...")
    print(f"API地址: {API_ENDPOINT}")
    print(f"计划添加 {len(ALLIANZ_KNOWLEDGE_DATA)} 条知识\n")
    
    success_count = 0
    failed_count = 0
    
    # 添加知识
    for i, knowledge_data in enumerate(ALLIANZ_KNOWLEDGE_DATA, 1):
        print(f"[{i}/{len(ALLIANZ_KNOWLEDGE_DATA)}] 正在添加: {knowledge_data['name']}")
        
        if add_knowledge(knowledge_data):
            success_count += 1
        else:
            failed_count += 1
        
        # 添加间隔，避免请求过于频繁
        if i < len(ALLIANZ_KNOWLEDGE_DATA):
            time.sleep(1)
    
    print(f"\n📊 添加完成统计:")
    print(f"   成功: {success_count} 条")
    print(f"   失败: {failed_count} 条")
    print(f"   总计: {len(ALLIANZ_KNOWLEDGE_DATA)} 条")
    
    # 等待一下让ES索引完成
    if success_count > 0:
        print("\n⏳ 等待Elasticsearch索引完成...")
        time.sleep(5)
        
        # 测试搜索
        test_search()
    
    print("\n✨ 脚本执行完成！")

if __name__ == "__main__":
    main()
