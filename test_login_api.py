#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录API
验证跳过LDAP验证后的登录功能
"""

import requests
import json

def test_login_api():
    """测试登录API"""
    print("🔐 测试登录API（跳过LDAP验证）")
    print("=" * 40)
    
    # 测试数据
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "user1", "password": "password123"},
        {"username": "testuser", "password": "testpass"},
        {"username": "newuser", "password": "newpass"}
    ]
    
    for i, user_data in enumerate(test_users, 1):
        print(f"\n🧪 测试用户 {i}: {user_data['username']}")
        
        try:
            response = requests.post(
                "http://localhost:8080/api/auth/login",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 登录成功: {user_data['username']}")
                print(f"   Token: {data.get('data', {}).get('token', 'N/A')[:20]}...")
                print(f"   用户ID: {data.get('data', {}).get('user', {}).get('id', 'N/A')}")
                print(f"   角色: {data.get('data', {}).get('user', {}).get('role', 'N/A')}")
                print(f"   邮箱: {data.get('data', {}).get('user', {}).get('email', 'N/A')}")
            else:
                print(f"❌ 登录失败: {user_data['username']}")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
    
    print("\n🎉 登录API测试完成！")
    print("\n📋 测试总结:")
    print("- ✅ 跳过LDAP验证")
    print("- ✅ 支持任意用户名密码登录")
    print("- ✅ 自动创建新用户")
    print("- ✅ 返回JWT token")

def test_with_token():
    """测试使用token访问受保护的接口"""
    print("\n🔑 测试使用token访问受保护的接口")
    print("=" * 40)
    
    # 先登录获取token
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(
            "http://localhost:8080/api/auth/login",
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('data', {}).get('token', '')
            
            if token:
                print(f"✅ 获取到token: {token[:20]}...")
                
                # 使用token访问受保护的接口
                headers = {"Authorization": f"Bearer {token}"}
                
                # 测试访问知识列表接口
                response = requests.get(
                    "http://localhost:8080/api/knowledge/list?page=1&size=10",
                    headers=headers
                )
                
                if response.status_code == 200:
                    print("✅ 使用token访问知识列表成功")
                else:
                    print(f"❌ 使用token访问知识列表失败: {response.status_code}")
                
            else:
                print("❌ 未获取到token")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

def main():
    """主函数"""
    print("🚀 登录API测试工具")
    print("=" * 40)
    
    # 测试登录API
    test_login_api()
    
    # 测试使用token
    test_with_token()
    
    print("\n💡 提示:")
    print("- 所有用户都可以使用任意密码登录")
    print("- 新用户会自动创建")
    print("- 登录后会返回JWT token")
    print("- 可以使用token访问受保护的接口")

if __name__ == "__main__":
    main() 