from colorama import Fore, Style, init, Back
from os import path as pt
from os import system
from json import load
import requests, sys

def send_log(type: str = 'info', message: str = '', mode: int=1) -> None:
    try:
        match type:
            case 'info':
                match mode:
                    case 1:
                        print(message)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': 'info', 'message': message})
            case 'success':
                match mode:
                    case 1:
                        print(Fore.GREEN + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': 'success', 'message': message})
            case 'warning':
                match mode:
                    case 1:
                        print(Fore.YELLOW + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': 'warning', 'message': message})
            case 'error':
                match mode:
                    case 1:
                        print(Fore.RED + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': 'error', 'message': message})
            case 'debug':
                match mode:
                    case 1:
                        print(Fore.BLUE + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/ban_account/log', json={'type': 'debug', 'message': message})
    except: return

# 初始化颜色
init(autoreset=True)

# 导入配置
user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')
is_user_data_read = True
try:
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = load(file)
        url = user_data['OJ']['APIURL']
except FileNotFoundError:
    is_user_data_read = False
    user_data = None

# 封号函数
def ban(username, log_mode=1) -> None:
    for i in range(25):
        if login(username, 'esnb') == '对不起！登录失败次数过多！您的账号有风险，半个小时内暂时无法登录！':
            send_log(type='success', message=f"{username}封禁成功！", mode=log_mode)
            return
    send_log(type='warning', message=f"{username}可能是空号号不存在或平台禁用封禁。", mode=log_mode)
    

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

def ban_account(mode: str, arg=None) ->  None:
    if mode == 'all':
        if arg == None:
            log_mode = 1
            white_list = input('请输入封禁白名单，以逗号分隔: ').split(',')
        else:
            log_mode = 2
            white_list = arg.split(',')
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json', 
            'Url-Type': 'general', 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
        } 
        response = requests.get(f'{url}/api/get-rank-list?currentPage=1&limit=114514&type=1',  headers=headers)
        
        # 检查响应状态码 
        if response.status_code  != 200:
            send_log(type='error', message=f"获取排行榜请求失败，状态码：{response.status_code}", mode=log_mode)
            return
        
        try:
            json_data = response.json() 
        except requests.exceptions.JSONDecodeError:
            send_log(type='error', message=f"排行榜请求JSON解析失败。原始响应：{response.text}", mode=log_mode)
            return
        
        # 检查JSON结构 
        if 'data' not in json_data or 'records' not in json_data['data']:
            send_log(type='error', message=f"获取排行榜响应JSON结构不符合预期：{json_data}", mode=log_mode)
            return
        
        for i in json_data['data']['records']: 
            if i['username'] in white_list:
                continue
            ban(i['username'], log_mode)
    elif mode == 'assign':
        if arg == None:
            username = input('封禁账号名称，用逗号分隔:').split(',')
            log_mode = 1
        else:
            username = arg.split(',')
            log_mode = 2
            
        send_log(type='info', message=f"开始封禁指定用户：{', '.join(username)}", mode=log_mode)
        
        for i in username:
            ban(i, log_mode)

def main() -> None:
    if is_user_data_read:
        mode = None
        while mode != 3:
            system('cls')
            print(Fore.BLUE + '欢迎使用HOJtool-一键封号！\n作者：WZ一只蚊子\nGitee仓库: https://gitee.com/wzokee/hoj-tool\n' + Back.RED + Fore.WHITE + '仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.封所有账户\n2.封指定账户\n3.退出\n' + Style.RESET_ALL)
            mode = input('请输入序号:')
            system('cls')
            if is_user_data_read:
                if mode == '1':
                    ban_account(mode='all')
                    print(Fore.GREEN + '已退出' + Style.RESET_ALL)
                    system('pause')
                elif mode == '2':
                    ban_account(mode='assign')
                    print(Fore.GREEN + '已退出' + Style.RESET_ALL)
                    system('pause')
            else:
                print(Fore.RED + '请先配置用户数据。' + Style.RESET_ALL)
            if mode == '3':
                return
if __name__ == '__main__':
    main()