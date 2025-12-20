from os import path as pt
from json import load
import requests
import sys
import threading
import queue
import time

# 日志
def send_log(type: str = 'info', message: str = '', pid: str = None, submit_id: str = None) -> None:
    try:
        formatted_message = message
        if pid:
            formatted_message = f"{formatted_message} -> {pid}"
        if submit_id:
            formatted_message = f"{formatted_message} -> {submit_id}"
        
        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': type, 'message': formatted_message})
    except:
        return

# 读取配置文件
user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')
is_user_data_read = True
user_data = None
url = None

try:
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = load(file)
        url = user_data['OJ']['APIURL']
except FileNotFoundError:
    is_user_data_read = False
    send_log('error', f'未找到配置文件 {user_data_path}')
except Exception as e:
    is_user_data_read = False
    send_log('error', f'读取用户数据时发生错误：{e}')

# 封号的主要操作
def ban(username) -> None:
    for i in range(25):
        if login(username, 'Attack from HOJ Tool') == '对不起！登录失败次数过多！您的账号有风险，半个小时内暂时无法登录！':
            send_log('success', f"{username}封禁成功！")
            return
    send_log('warning', f"{username}可能不存在。")

# 线程工作函数：负责处理用户名封禁
def worker_thread(username_queue, stop_event):
    while not stop_event.is_set():
        try:
            username = username_queue.get_nowait()
        except queue.Empty:
            break
            
        if stop_event.is_set():
            break
            
        ban(username)
        username_queue.task_done()

# 线程池管理
def process_with_threads(usernames, thread_count=5):
    username_queue = queue.Queue()
    stop_event = threading.Event()
    threads = []
    
    # 将用户名添加到队列
    for username in usernames:
        username_queue.put(username)
    
    # 创建并启动线程
    for _ in range(thread_count):
        thread = threading.Thread(target=worker_thread, args=(username_queue, stop_event))
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # 等待所有任务完成或停止事件
    try:
        while not username_queue.empty() and not stop_event.is_set():
            try:
                status_response = requests.get("http://127.0.0.1:1146/api/ban_account/status", timeout=2)
                if status_response.json().get('stop_flag') == True:
                    stop_event.set()
                    requests.get("http://127.0.0.1:1146/api/ban_account/stopp")
                    break
            except:
                pass
            time.sleep(0.1)
    except KeyboardInterrupt:
        stop_event.set()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=1)
    
    return stop_event.is_set()

# 发送登录请求
def login(username, password):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Url-Type': 'general',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }

    data = {
        'username': f'{username}',
        'password': f'{password}',
    }

    response = requests.post(f'{url}/api/login', headers=headers, json=data)
    return response.json()['msg']

# 封禁用户
def ban_account(mode: str, arg=None) -> None:
    if mode == 'all':
        if arg is None:
            white_list = []
        else:
            white_list = arg.split(',')
            
        headers = {
            'Accept': 'application/json', 
            'Content-Type': 'application/json', 
            'Url-Type': 'general', 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        }
        
        try:
            response = requests.get(f'{url}/api/get-rank-list?currentPage=1&limit=114514&type=1', headers=headers)
        except requests.RequestException as e:
            send_log('error', f"获取排行榜请求失败: {e}")
            return
        
        if response.status_code != 200:
            send_log('error', f"获取排行榜请求失败，状态码：{response.status_code}")
            return
        
        try:
            json_data = response.json()
        except requests.exceptions.JSONDecodeError:
            send_log('error', f"排行榜请求JSON解析失败。原始响应：{response.text}")
            return
        
        # 检查JSON结构
        if 'data' not in json_data or 'records' not in json_data['data']:
            send_log('error', f"获取排行榜响应JSON结构不符合预期：{json_data}")
            return
        
        # 收集需要封禁的用户名
        usernames_to_ban = []
        for i in json_data['data']['records']:
            try:
                status_response = requests.get("http://127.0.0.1:1146/api/ban_account/status", timeout=2)
                if status_response.json().get('stop_flag') == True:
                    requests.get("http://127.0.0.1:1146/api/ban_account/stopp")
                    return
            except:
                pass
            
            if i['username'] in white_list:
                continue
            usernames_to_ban.append(i['username'])
        
        # 使用线程池处理封禁
        if usernames_to_ban:
            send_log('info', f"开始使用5线程封禁 {len(usernames_to_ban)} 个用户...")
            stopped = process_with_threads(usernames_to_ban, 5)
            if stopped:
                send_log('warning', "封禁过程被用户停止")
            else:
                send_log('success', f"已完成封禁 {len(usernames_to_ban)} 个用户")
        else:
            send_log('info', "没有需要封禁的用户")
            
    elif mode == 'assign':
        if arg is None:
            username = []
        else:
            username = arg.split(',')
            
        send_log('info', f"开始使用5线程封禁指定用户：{', '.join(username)}")
        
        # 使用线程池处理封禁
        if username:
            stopped = process_with_threads(username, 5)
            if stopped:
                send_log('warning', "封禁过程被用户停止")
            else:
                send_log('success', f"已完成封禁 {len(username)} 个指定用户")
    # 发送停止信号
    requests.get("http://127.0.0.1:1146/api/ban_account/stopp")