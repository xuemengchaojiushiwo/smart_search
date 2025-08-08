@echo off
echo 启动极客智坊API服务...

cd python_service

echo 安装依赖...
pip install -r requirements_geekai.txt

echo 启动服务...
python app_with_geekai.py

pause 