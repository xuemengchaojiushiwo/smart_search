# 启动知识库管理系统
Write-Host "========================================" -ForegroundColor Green
Write-Host "启动知识库管理系统" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "正在编译项目..." -ForegroundColor Yellow
mvn clean compile

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 编译失败，请检查错误信息" -ForegroundColor Red
    Read-Host "按任意键继续"
    exit 1
}

Write-Host "✅ 编译成功" -ForegroundColor Green

Write-Host ""
Write-Host "正在启动应用..." -ForegroundColor Yellow
Write-Host "应用将在 http://localhost:8080 启动" -ForegroundColor Cyan
Write-Host "OpenAPI UI: http://localhost:8080/swagger-ui.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Yellow
Write-Host ""

mvn spring-boot:run

Read-Host "按任意键继续" 