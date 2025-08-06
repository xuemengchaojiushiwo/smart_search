@echo off
echo ========================================
echo Python服务启动脚本
echo ========================================

echo.
echo 启动Python文档处理服务...
echo 服务将在 http://localhost:8000 启动
echo.
echo 按 Ctrl+C 停止服务
echo.

cd python_service
python app_pymupdf_pro.py

pause 