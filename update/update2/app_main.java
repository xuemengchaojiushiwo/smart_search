#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能知识库系统 - 主应用
整合PyMuPDF Pro + PyMuPDF4LLM + LangChain + 极客智坊API
"""

import logging
import uvicorn
from fastapi import FastAPI

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="智能知识库系统", version="2.0.0")

# 导入路由
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from routes import router

# 注册路由
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)