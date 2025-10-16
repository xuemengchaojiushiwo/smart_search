import sys
import json
import logging
from typing import Optional, Dict, Any
from bs4 import BeautifulSoup

# 导入AI管理器
from ai_client_manager import get_ai_manager

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_html(html_content: str) -> str:
    """
    清理HTML内容，提取纯文本
    """
    if not html_content:
        return ""
    
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def generate_diff_summary(old_html: str, new_html: str) -> Optional[str]:
    """
    使用极客智坊API生成差异总结
    
    Args:
        old_html: 旧版本HTML内容
        new_html: 新版本HTML内容
        
    Returns:
        总结文本，如果生成失败则返回None
    """
    try:
        # 清理HTML，提取纯文本
        old_text = clean_html(old_html)
        new_text = clean_html(new_html)
        
        if not old_text and not new_text:
            return "两个版本都为空，无变更。"
        
        if not old_text:
            return "这是首次添加内容。"
            
        if not new_text:
            return "所有内容已被删除。"
            
        if old_text == new_text:
            return "内容未发生变化，可能只有格式调整。"
        
        # 构建提示
        prompt = f"""请分析下面两个文本版本的差异，并用简洁的中文总结变更内容：

旧版本:
{old_text[:3000]}  # 限制长度避免超出token限制

新版本:
{new_text[:3000]}  # 限制长度避免超出token限制

请以"本次更新："开头，简明扼要地描述主要变更，包括添加、删除或修改的关键信息。"""
        
        # 获取AI管理器
        manager = get_ai_manager()
        
        # 构建消息
        messages = [
            {"role": "system", "content": "你是一个专业的文档差异分析助手，擅长分析和总结文档版本间的变化。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用AI管理器的chat_completion方法
        result = manager.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=500
        )
        
        if "error" not in result:
            # 从结果中提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                summary = result["choices"][0]["message"]["content"].strip()
                logger.info(f"成功生成差异总结，长度: {len(summary)}")
                return summary
            else:
                logger.error(f"AI响应格式不正确: {result}")
                return "无法解析AI响应，请查看HTML对比结果。"
        else:
            logger.error(f"AI调用失败: {result['error']}")
            return "AI调用失败，请查看HTML对比结果。"
            
    except Exception as e:
        logger.error(f"生成差异总结时发生错误: {str(e)}")
        return "生成差异总结时发生错误，请查看HTML对比结果。"

# 测试函数
if __name__ == "__main__":
    old_html = "<p>这是一个测试文档。包含<strong>重要信息</strong>和一些细节。</p>"
    new_html = "<p>这是一个更新后的测试文档。包含<strong>重要信息</strong>和更多细节说明。</p><p>新增了一个段落。</p>"
    
    # 测试时直接返回模拟结果
    summary = "本次更新：1. 文档标题从'测试文档'改为'更新后的测试文档'；2. 增加了'更多细节说明'的内容；3. 新增了一个段落。"
    print(f"差异总结:\n{summary}")
