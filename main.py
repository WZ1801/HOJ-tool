from selenium.webdriver.chrome.service import Service
from colorama import Fore, Back, Style, init
import auto_solver, ban_account, sys
from selenium import webdriver
from os import path as pt
from os import system
from json import dump

user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')

def get_user_data() -> None:
    global user_data_path, options, user_data
    user_data = {
        'OJ': {'URL': None, 'APIURL': None, 'username': None, 'password': None},
        'AI_cookies': None,
        'AI_URL': None,
        'ChromeDriver_path': None
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
            url = input('OJ API网址(如果你不知道是什么,请填上面的OJ网址,这是为防止防爬虫的OJ设计的):').rstrip('/')
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

        while not user_data['ChromeDriver_path']:
            chrome_driver_path = input('ChromeDriver路径:')
            if validate_file_path(chrome_driver_path):
                user_data['ChromeDriver_path'] = chrome_driver_path
            else:
                print(Fore.RED + '文件路径不存在，请重新输入。' + Style.RESET_ALL)

        driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']), options=options)
        print('请自行操作登录AI，完成后回车', end='')
        driver.get('https://bot.n.cn/')
        system('pause')
        driver.refresh()
        cookies = driver.get_cookies()
        cookie_list = [cookie for cookie in cookies]
        user_data['AI_cookies'] = cookie_list
        with open(user_data_path, 'w') as file:
            dump(user_data, file)
        driver.quit()
    except Exception as e:
        print(Fore.RED + f'配置过程中出错: {str(e)}' + Style.RESET_ALL)
        if 'driver' in locals():
            driver.quit()

def main():
    init(autoreset=True)
    mode = None
    while mode != 4:
        system('cls')
        print(Fore.BLUE + '欢迎使用HOJtool！\n作者：WZ一只蚊子\nGitee仓库: https://gitee.com/wzokee/hoj-tool\n' + Back.RED + Fore.WHITE + '仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.配置信息\n2.自动刷题\n3.一键封号\n4.退出\n' + Style.RESET_ALL)
        mode = input('请输入序号:')
        system('cls')
        if mode == '1':
            get_user_data()
            print(f'{Fore.GREEN}配置成功{Style.RESET_ALL}')
            system('pause')
        elif mode == '2':
            try:
                auto_solver.main()
            except Exception as e:
                print(Fore.RED + f'啊？这都报错:{e}' + Style.RESET_ALL)
        elif mode == '3':
            ban_account.main()
            
if __name__ == '__main__':
    main()