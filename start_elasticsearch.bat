@echo off
echo ========================================
echo 启动 Elasticsearch
echo ========================================

echo.
echo 正在启动 Elasticsearch...
echo 请等待启动完成，通常需要30-60秒
echo.

cd /d "D:\xmc\elasticsearch-9.1.0-windows-x86_64\elasticsearch-9.1.0"
call bin\elasticsearch.bat

echo.
echo Elasticsearch 已启动
echo 访问地址: http://localhost:9200
echo 集群健康: http://localhost:9200/_cluster/health
echo.

pause 