@echo off
echo ========================================
echo 知识库管理系统启动脚本
echo ========================================

echo.
echo 1. 编译Java项目...
call mvn clean compile
if %errorlevel% neq 0 (
    echo ❌ Java项目编译失败
    pause
    exit /b 1
)
echo ✅ Java项目编译成功

echo.
echo 2. 启动Java应用...
echo 应用将在 http://localhost:8080 启动
echo Swagger UI: http://localhost:8080/swagger-ui.html
echo.
echo 按 Ctrl+C 停止应用
echo.
call mvn spring-boot:run

pause 