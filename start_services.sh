#!/bin/bash

echo "启动知识库管理系统服务..."

echo
echo "1. 启动Python服务..."
cd python_service
python app.py &
PYTHON_PID=$!
cd ..

echo
echo "2. 启动Java服务..."
mvn spring-boot:run &
JAVA_PID=$!

echo
echo "服务启动中..."
echo "Java服务地址: http://localhost:8080"
echo "Python服务地址: http://localhost:8000"
echo
echo "按 Ctrl+C 停止所有服务..."

# 等待用户中断
trap "echo '正在停止服务...'; kill $PYTHON_PID $JAVA_PID; exit" INT
wait 