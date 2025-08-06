@echo off
echo 启动知识库管理系统服务...

echo.
echo 1. 启动Python服务...
cd python_service
start "Python Service" cmd /k "python app.py"
cd ..

echo.
echo 2. 启动Java服务...
start "Java Service" cmd /k "mvn spring-boot:run"

echo.
echo 服务启动中...
echo Java服务地址: http://localhost:8080
echo Python服务地址: http://localhost:8000
echo.
echo 按任意键退出...
pause > nul 