@echo off
echo ========================================
echo 智能知识库系统启动脚本
echo ========================================

echo.
echo 启动智能知识库系统...
echo 集成功能：
echo - PyMuPDF Pro 文档处理
echo - PyMuPDF4LLM 结构化分块
echo - LangChain 向量化
echo - Elasticsearch 存储
echo - 极客智坊API 智能问答
echo.
echo 服务将在 http://localhost:8000 启动
echo.
echo 按 Ctrl+C 停止服务
echo.

cd python_service
python app_main.py

pause 