@echo off
echo ========================================
echo 简化启动脚本 - 测试OpenAPI配置
echo ========================================

echo.
echo 启动Java应用...
echo 应用将在 http://localhost:8080 启动
echo OpenAPI UI: http://localhost:8080/swagger-ui.html
echo.
echo 按 Ctrl+C 停止应用
echo.

mvn spring-boot:run

pause 