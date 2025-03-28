import os
import sys

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(current_dir)

import asyncio
from hypercorn.config import Config
from hypercorn.asyncio import serve
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.api import init_app
from app.config.settings import settings
from app.config.logging_config import setup_logging
from pkg.core.context.context_vars import set_app

# 设置应用名称
set_app(settings.APP_NAME)

# 设置日志
setup_logging()

app = FastAPI()
init_app(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://192.168.0.188:3000",
        "https://be-my-eyes.vercel.app",
        "https://be-my-eyes-y3nw.vercel.app"
    ],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头部
)

async def main():
    """Main async function to run both timer and server"""
   
    # 配置服务器
    config = Config()
    config.bind = [f"{settings.HOST}:{settings.PORT}"]
    config.use_reloader = True
    config.workers = settings.WORKERS
    config.accesslog = "-"

    # 同时运行服务器
    await serve(app, config)

if __name__ == "__main__":
    asyncio.run(main())