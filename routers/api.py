"""
API路由模块
"""

from fastapi.responses import JSONResponse
from fastapi import APIRouter
from fastapi import Request
from os import path as pt
from json import load
from sys import argv
from module.statistics import get_statistics, clear_cache
router = APIRouter()
user_data_path = pt.join(pt.dirname(pt.normpath(argv[0])), 'user_data.json')

auto_solver_status = {
    'is_running': False,
    'stop_flag': False,
    'is_login_360ai': False
}

ban_account_status = {
    'is_banning': False,
    'stop_flag': False
}

@router.get("/config_ok", summary="检查用户配置是否合法")
async def config_ok():
    """检查用户配置文件是否存在且合法"""
    try:
        with open(user_data_path, 'r', encoding='utf-8') as file:
            user_data = load(file)
        
        # 检查必要字段是否存在
        required_fields = ['OJ', 'AI_URL', 'Browser']
        for field in required_fields:
            if field not in user_data:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "msg": f"配置文件缺少必要字段: {field}"}
                )
        
        # 检查OJ配置的必要字段
        required_oj_fields = ['URL', 'APIURL', 'username', 'password']
        for field in required_oj_fields:
            if field not in user_data['OJ']:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "msg": f"OJ配置缺少必要字段: {field}"}
                )
        
        # 检查Browser配置的必要字段
        required_browser_fields = ['Type', 'Driver_path']
        for field in required_browser_fields:
            if field not in user_data['Browser']:
                return JSONResponse(
                    status_code=400,
                    content={"status": "error", "msg": f"Browser配置缺少必要字段: {field}"}
                )
        
        # 检查爬虫程序是否存在
        driver_path = user_data['Browser']['Driver_path']
        if not pt.exists(driver_path):
            return JSONResponse(
                status_code=400,
                content={"status": "error", "msg": f"浏览器驱动文件不存在: {driver_path}"}
            )
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "msg": "配置文件合法"}
        )
    except FileNotFoundError:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "msg": "配置文件不存在"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"检查配置文件时发生错误：{e}"}
        )

@router.get("/config/get", summary="获取用户配置")
async def get_config():
    """获取用户配置信息"""
    try:
        with open(user_data_path, 'r', encoding='utf-8') as file:
            user_data = load(file)
    except Exception as e:
        return {"status": "error", "message": f"读取用户数据时发生错误：{e}"}
    return user_data


    
@router.post("/config/save", summary="保存用户配置")
async def save_config(request: Request):
    import json
    try:
        # 检查请求体是否为空
        request_data = await request.json()
        if not request_data:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "msg": "请求体不能为空"}
            )
        config = json.dumps(request_data, ensure_ascii=False, indent=2)
        with open(user_data_path, 'w', encoding='utf-8') as file:
            file.write(config)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "msg": "配置保存成功"}
        )
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=400,
            content={"status": "error", "msg": f"JSON格式错误：{e}"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"保存用户数据时发生错误：{e}"}
        )

@router.get("/auto_solver/all_code", summary="开始刷全部题")
async def all_code_() -> JSONResponse:
    if auto_solver_status['is_running']: return JSONResponse(
        status_code=400,
        content={"status": "error", "msg": "当前有任务正在运行"}
    )
    try:
        import module.auto_solver, threading
        act = threading.Thread(target=module.auto_solver.all_code, args=(True,))
        act.start()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f'发生未知错误:{e}'}
        )
    auto_solver_status['is_running'] = True
    auto_solver_status['is_login_360ai'] = False
    auto_solver_status['stop_flag']  = False
    return JSONResponse(
        status_code=200,
        content={"status": "success", "msg": "已启动刷题线程"}
    )

@router.post("/auto_solver/training_code", summary="开始刷训练题")
async def training_code_(request: Request) -> JSONResponse:
    if auto_solver_status['is_running']: return JSONResponse(
        status_code=400,
        content={"status": "error", "msg": "当前有任务正在运行"}
    )
    try:
        import module.auto_solver, threading
        resjson = await request.json()
        act = threading.Thread(target=module.auto_solver.training_code, args=(None, resjson['tids'], None, resjson['notes'], True, True, 2))
        act.start()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f'发生未知错误:{e}'}
        )
    auto_solver_status['is_running'] = True
    auto_solver_status['is_login_360ai'] = False
    auto_solver_status['stop_flag']  = False
    return JSONResponse(
        status_code=200,
        content={"status": "success", "msg": "已启动刷题线程"}
    )

@router.post("/auto_solver/problem_code", summary="开始刷个题")
async def problem_code_(request: Request) -> JSONResponse:
    if auto_solver_status['is_running']: return JSONResponse(
        status_code=400,
        content={"status": "error", "msg": "当前有任务正在运行"}
    )
    try:
        import module.auto_solver, threading
        resjson = await request.json()
        act = threading.Thread(target=module.auto_solver.problem_code, args=(None, resjson['pids'], resjson['notes'], None, True, True, 2))
        act.start()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f'发生未知错误:{e}'}
        )
    auto_solver_status['is_running'] = True
    auto_solver_status['is_login_360ai'] = False
    auto_solver_status['stop_flag']  = False
    return JSONResponse(
        status_code=200,
        content={"status": "success", "msg": "已启动刷题线程"}
    )

@router.get("/auto_solver/status", summary="刷题状态")
async def get_auto_solver_status() -> JSONResponse:
    """获取刷题状态"""
    try:
        return JSONResponse(
            status_code=200,
            content=auto_solver_status
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"获取状态失败: {str(e)}"}
        )
    
@router.get("/auto_solver/login_360ai", summary="登录360AIflag立")
async def login_360ai() -> JSONResponse:
    try:
        auto_solver_status['is_login_360ai'] = True
    except Exception as e:
       return JSONResponse(
           status_code=500,
           content={"status": "error", "msg": str(e)}
       )
    return JSONResponse(
        status_code=200,
        content={"status": "success"}
    )

@router.get("/auto_solver/stop", summary="停止刷题")
async def stop_auto_solver() -> JSONResponse:
    try:
        auto_solver_status["stop_flag"] = True
    except Exception as e:
       return JSONResponse(
           status_code=500,
           content={"status": "error", "msg": str(e)}
       )
    return JSONResponse(
        status_code=200,
        content={"status": "success"}
    )

@router.get("/auto_solver/stopp", summary="is_running倒")
async def auto_solver_stopp() -> JSONResponse:
    try:
        auto_solver_status["is_running"] = False
    except Exception as e:
       return JSONResponse(
           status_code=500,
           content={"status": "error", "msg": str(e)}
       )
    return JSONResponse(
        status_code=200,
        content={"status": "success"}
    )

@router.post("/ban_account/ban_account", summary="封禁账号")
async def ban_account_(request: Request) -> JSONResponse:
    try:
        global ban_account_status
        ban_account_status["is_banning"] = True
        resjson = await request.json()
        if 'mode' not in resjson:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "msg": "请求体缺少必要字段"}
            )
        mode = resjson['mode']
        if mode == 'assign' and 'username' not in resjson:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "msg": "请求体缺少必要字段"}
            )
        if mode == 'all' and 'white_list' not in resjson:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "msg": "请求体缺少必要字段"}
            )
        from threading import Thread
        if mode == 'all':
            import module.ban_account
            Thread(target=module.ban_account.ban_account, args=(str(mode), resjson['white_list'])).start()
        elif mode == 'assign':
            import module.ban_account
            Thread(target=module.ban_account.ban_account, args=(str(mode), resjson['username'])).start()
        
        return JSONResponse(
            status_code=200,
            content={"status": "success"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"封禁账号失败: {str(e)}"}
        )

@router.get("/ban_account/status", summary="封禁账号状态")
async def get_ban_account_status() -> JSONResponse:
    try:
        global ban_account_status
        return JSONResponse(
            status_code=200,
            content=ban_account_status
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"更新封禁账号状态失败: {str(e)}"}
        )

@router.get("/ban_account/stop", summary="停止封禁账号")
async def stop_ban_account() -> JSONResponse:
    try:
        global ban_account_status
        ban_account_status['stop_flag'] = True
        return JSONResponse(
            status_code=200,
            content={"status": "success", "msg": "已发送停止封禁账号操作信号"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"停止封禁账号失败: {str(e)}"}
        )

@router.get("/ban_account/stopp", summary="已停止封禁账号")
async def stopp_ban_account() -> JSONResponse:
    try:
        global ban_account_status
        ban_account_status["is_banning"] = False
        return JSONResponse(
            status_code=200,
            content={"status": "success", "msg": "已发送封禁账号操作已停止信号"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"已停止封禁账号失败: {str(e)}"}
        )


from collections import deque
import asyncio

# 限制日志
logs1 = deque(maxlen=10000)
logs_lock1 = asyncio.Lock()

@router.post("/ban_account/log", summary="记录日志")
async def log1(request: Request) -> JSONResponse:
    try:
        resjson = await request.json()
        async with logs_lock1:
            logs1.append(resjson)
        import json
        return JSONResponse(
            status_code=200,
            content={"status": "success", "loglong": len(json.dumps(resjson))}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"记录日志失败: {str(e)}"}
        )
    
@router.get("/ban_account/get_logs", summary="读取日志")
async def get_log1() -> JSONResponse:
    try:
        import json
        async with logs_lock1:
            logs_copy = list(logs1)
        return_log = json.dumps(logs_copy, ensure_ascii=False) if logs_copy else ""
        logs1.clear()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "log": return_log}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"获取日志失败: {str(e)}"}
        )

# 限制日志
logs2 = deque(maxlen=10000)
logs_lock2 = asyncio.Lock()

@router.post("/auto_solver/log", summary="记录日志")
async def log2(request: Request) -> JSONResponse:
    try:
        resjson = await request.json()
        async with logs_lock2:
            logs2.append(resjson)
        import json
        return JSONResponse(
            status_code=200,
            content={"status": "success", "loglong": len(json.dumps(resjson))}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"记录日志失败: {str(e)}"}
        )
    
@router.get("/auto_solver/get_logs", summary="读取日志")
async def get_log1() -> JSONResponse:
    try:
        import json
        async with logs_lock2:
            logs_copy = list(logs2)
        return_log = json.dumps(logs_copy, ensure_ascii=False) if logs_copy else ""
        logs2.clear()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "log": return_log}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "msg": f"获取日志失败: {str(e)}"}
        )

@router.get("/statistics", summary="获取统计信息")
async def statistics(username: str = None):
    """获取统计信息"""
    result = get_statistics(username)
    return result

@router.get("/statistics/clear_cache", summary="清空统计信息缓存")
async def clear_statistics_cache():
    """清空统计信息缓存"""
    clear_cache()
    return {"status": "success", "msg": "缓存已清空"}
