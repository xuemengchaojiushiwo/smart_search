import requests
import os

def test_upload_pdf():
    """测试重新上传PDF文档"""
    url = "http://localhost:8080/api/knowledge/29/document"
    pdf_path = "python_service/file/安联美元.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF文件不存在: {pdf_path}")
        return
    
    print(f"📁 上传文件: {pdf_path}")
    print(f"🌐 请求URL: {url}")
    
    try:
        with open(pdf_path, 'rb') as f:
            files = {"file": ("安联美元.pdf", f, "application/pdf")}
            response = requests.post(url, files=files, timeout=60)
            
        print(f"📊 状态码: {response.status_code}")
        print(f"📄 响应: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                print("✅ PDF上传成功")
                data = result.get('data', {})
                print(f"📊 处理结果: {data}")
            else:
                print(f"⚠️  PDF处理失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 上传异常: {e}")

if __name__ == "__main__":
    test_upload_pdf()
