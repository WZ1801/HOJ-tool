import module.auto_solver, module.ban_account, sys
from colorama import Fore, Back, Style, init
from os import path as pt
from os import system
from json import dump
from sys import argv

# 配置文件路径
user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')

def get_user_data() -> None:
    '''
    获取用户数据
    '''
    global user_data_path, options, user_data
    user_data = {
        'OJ': {'URL': None, 'APIURL': None, 'username': None, 'password': None},
        'AI_URL': None,
        'Browser': {
            'Type': None,
            'Driver_path': None
        }
    }

    def validate_url(url: str) -> bool:
        import re
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
            r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None

    def validate_file_path(path: str) -> bool:
        import os
        return os.path.exists(path)

    try:
        while not user_data['OJ']['URL']:
            url = input('OJ网址:').rstrip('/')
            if validate_url(url):
                user_data['OJ']['URL'] = url
            else:
                print(Fore.RED + '无效的URL格式，请重新输入。' + Style.RESET_ALL)

        while not user_data['OJ']['APIURL']:
            url = input('OJ API网址(如果你不知道是什么,请填上面的OJ网址):').rstrip('/')
            if validate_url(url):
                user_data['OJ']['APIURL'] = url
            else:
                print(Fore.RED + '无效的URL格式，请重新输入。' + Style.RESET_ALL)

        user_data['OJ']['username'] = input('OJ用户名:')
        user_data['OJ']['password'] = input('OJ密码:')

        while not user_data['AI_URL']:
            ai_url = input('AI对话地址:')
            if validate_url(ai_url):
                user_data['AI_URL'] = ai_url
            else:
                print(Fore.RED + '无效的URL格式，请重新输入。' + Style.RESET_ALL)

        while not user_data['Browser']['Type']:
            browser_type = input('浏览器类型(Chrome/Edge/Firefox):').strip().lower()
            if browser_type in ['chrome', 'edge', 'firefox']:
                user_data['Browser']['Type'] = browser_type
            else:
                print(Fore.RED + '无效的浏览器类型，请重新输入。' + Style.RESET_ALL)

        while not user_data['Browser']['Driver_path']:
            driver_path = input('爬虫驱动路径:')
            if validate_file_path(driver_path):
                user_data['Browser']['Driver_path'] = driver_path
            else:
                print(Fore.RED + '文件路径不存在，请重新输入。' + Style.RESET_ALL)

        with open(user_data_path, 'w') as file:
            dump(user_data, file)
    except Exception as e:
        print(Fore.RED + f'配置过程中出错: {str(e)}' + Style.RESET_ALL)

def main():
    init(autoreset=True)
    system('cls')
    system('title HOJtool v4.0.2')
    # print(Fore.BLUE + '欢迎使用HOJtool v4.0\n作者：EchoSearch\nGitee仓库: https://gitee.com/wzokee/hoj-tool\n' + Back.RED + Fore.WHITE + '仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n回车进入WebGUI模式\n' + Style.RESET_ALL)
    if '-console' in argv:
        mode = None
        while mode != '4':
            system('cls')
            print(Fore.BLUE + '欢迎使用HOJtool v4.0 Console Mode！\n作者：EchoSearch\nGitee仓库: https://gitee.com/wzokee/hoj-tool\n' + Back.RED + Fore.WHITE + '仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.配置信息\n2.自动刷题\n3.封禁他人账号\n4.退出\n' + Style.RESET_ALL)
            mode = input('请输入序号:')
            system('cls')
            if mode == '1':
                get_user_data()
                print(f'{Fore.GREEN}配置成功{Style.RESET_ALL}')
                system('pause')
            elif mode == '2':
                try:
                    module.auto_solver.main()
                except Exception as e:
                    print(Fore.RED + f'啊？这都报错:{e}' + Style.RESET_ALL)
            elif mode == '3':
                module.ban_account.main()
        return
    else:
        
        system('cls')
        print(f'{Fore.RED}此为开发者日志页面,仅错误显示!{Style.RESET_ALL}')
        import webview
        import server
        from threading import Thread

        server_thread = Thread(target=server.start_server)
        server_thread.daemon = True
        server_thread.start()

        def on_closing():
            """关闭窗口退出程序"""
            import os
            os._exit(0)

        try:
            window = webview.create_window('HOJ tool', 'http://127.0.0.1:1146', maximized=True)
            window.events.closing += on_closing
            webview.start()
        except Exception as e:
            import tkinter
            import tkinter.messagebox
            root = tkinter.Tk()
            root.withdraw()
            tkinter.messagebox.showerror("HOJ tool Error", f"打开浏览页面发生错误:{e}\n请确认是否安装WebView2或IE COM组件，Win7/8需自行安装组件。如无法解决，请向HOJ tool反馈")
            root.destroy()

if __name__ == '__main__':
    main()