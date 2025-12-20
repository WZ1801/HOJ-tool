"""
页面路由模块
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
import os

router = APIRouter()

def read_html_file(path: str) -> HTMLResponse:
    """读取HTML文件并返回HTMLResponse"""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        return HTMLResponse(content)
    else:
        return HTMLResponse("<h1>404 Not Found</h1><p>Page not found</p>", status_code=404)

# 页面路由配置
PAGES = {
    "/": ("frame", "index.html"),
    "/about": ("about", "index.html"),
    "/auto_solver": ("auto_solver", "index.html"),
    "/ban_account": ("ban_account", "index.html"),
    "/settings": ("settings", "index.html"),
    "/statistics": ("statistics", "index.html")
}

# 统一的页面路由处理
def create_page_handler(folder: str, file: str):
    """创建页面处理函数"""
    async def page_handler():
        """返回页面HTML文件"""
        index_path = os.path.join("static", folder, file)
        return read_html_file(index_path)
    return page_handler

for route, (folder, file) in PAGES.items():
    func_name = f"read_{folder}_page"
    handler = create_page_handler(folder, file)
    handler.__name__ = func_name
    handler.__doc__ = f"返回{folder}页面"
    
    router.get(route, response_class=HTMLResponse, summary=f"{folder}页面")(handler)

@router.get("/favicon.ico")
async def favicon():
    """提供favicon.ico文件"""
    favicon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    else:
        return HTMLResponse("", status_code=404)