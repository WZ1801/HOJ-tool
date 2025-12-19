import sys
import os
from os import path as pt
from json import load as loadjson
from json import dump as dumpjson
import re
from colorama import Fore, Style

config_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')

def get_config() -> dict:
    """获取用户数据"""
    global config_path
    try:    
        try:
            with open(config_path, 'r') as f:
                config = loadjson(f)
        except Exception:
            config_path = pt.join(pt.dirname(pt.dirname(pt.normpath(sys.argv[0]))), 'user_data.json')
            with open(config_path, 'r') as f:
                config = loadjson(f)
    except Exception:
        config = {}
    return config

def validate_url(url: str) -> bool:
    """验证URL格式"""
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+]?)'  # ipv6
        r'(?::\d+)?'  # port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

def get_user_data() -> None:
    """
    获取用户数据
    """
    global config_path
    
    os.system('cls')
    
    config = {
        'OJ': {'URL': None, 'APIURL': None, 'username': None, 'password': None},
        'AI_URL': None,
        'Browser': {
            'Type': None,
            'Driver_path': None
        }
    }

    try:
        while not config['OJ']['URL']:
            url = input('OJ网址:').rstrip('/')
            if validate_url(url):
                config['OJ']['URL'] = url
            else:
                print(Fore.RED + '无效的URL格式，请重新输入。' + Style.RESET_ALL)

        while not config['OJ']['APIURL']:
            url = input('OJ API网址(如果你不知道是什么,请填上面的OJ网址):').rstrip('/')
            if validate_url(url):
                config['OJ']['APIURL'] = url
            else:
                print(Fore.RED + '无效的URL格式，请重新输入。' + Style.RESET_ALL)

        config['OJ']['username'] = input('OJ用户名:')
        config['OJ']['password'] = input('OJ密码:')
        
        with open(config_path, 'w') as file:
            dumpjson(config, file)
    except Exception as e:
        print(Fore.RED + f'配置过程中出错: {str(e)}' + Style.RESET_ALL)
