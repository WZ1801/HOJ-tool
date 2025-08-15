"""
HOJ Tool Web Server

基于FastAPI的Web服务器，为HOJ Tool提供Web界面
支持静态文件服务和API接口
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

import sys
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from routers import pages, api

# 创建FastAPI实例
app = FastAPI(
    title="HOJtool Web API",
    description="HOJ Tool的Web界面API",
    version="1.0.0"
)

# 添加CORS中间件，允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(pages.router)
app.include_router(api.router, prefix="/api")

# 挂载根路径静态文件服务，用于加载CSS和JS等文件
app.mount("/", StaticFiles(directory="static", html=True, check_dir=False), name="static")

# 静态文件配置
static_paths = {
    "/home": "home",
    "/auto_solver": "auto_solver",
    "/ban_account": "ban_account",
    "/css": "css"
}

for route_path, dir_name in static_paths.items():
    app.mount(
        route_path,
        StaticFiles(directory=os.path.join('static', dir_name), check_dir=False),
        name=f"static_{dir_name}"
    )

def start_server() -> None:
    """启动FastAPI服务器"""
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=1146,
        log_level="error",
        access_log=False
    )

if __name__ == "__main__":
    start_server()