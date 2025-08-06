@echo off
echo ========================================
echo 启动知识库管理系统
echo ========================================

echo.
echo 正在编译项目...
call mvn clean compile
if %errorlevel% neq 0 (
    echo ❌ 编译失败，请检查错误信息
    pause
    exit /b 1
)
echo ✅ 编译成功

echo.
echo 正在启动应用...
echo 应用将在 http://localhost:8080 启动
echo OpenAPI UI: http://localhost:8080/swagger-ui.html
echo.
echo 按 Ctrl+C 停止应用
echo.

call mvn spring-boot:run

pause 