"""
HOJ Tool Web Server
"""
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
import sys
from pathlib import Path
from lib.port_utils import get_port

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

from routers import pages, api

# 创建FastAPI实例
app = FastAPI(
    title="HOJ Tool Web API",
    description="HOJ Tool Web API",
    version="1.0.0"
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)

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

# 挂载根路径静态文件
app.mount("/", StaticFiles(directory="static", html=True, check_dir=False), name="static")

# 静态文件配置
static_paths = {
    "/home": "home",
    "/auto_solver": "auto_solver",
    "/ban_account": "ban_account",
    "/statistics": "statistics",
    "/css": "css"
}

for route_path, dir_name in static_paths.items():
    app.mount(
        route_path,
        StaticFiles(directory=os.path.join('static', dir_name), check_dir=False),
        name=f"static_{dir_name}"
    )

def start_server(port=None) -> None:
    """启动FastAPI服务器
    
    Args:
        port: 指定端口号，如果为None则使用随机可用端口
    """
    if port is None:
        port = get_port()
    
    
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=port, 
        log_level="error", 
        access_log=False, 
        loop="asyncio",
    )

if __name__ == "__main__":
    start_server()