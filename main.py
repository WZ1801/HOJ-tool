#coding=utf-8
from time import time, sleep

Start_time = time()

import requests, pyperclip, hashlib, re, logging, sys, json
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from colorama import init, Fore, Back, Style
from json import dump, load, dumps
from dotenv import load_dotenv
from datetime import datetime
from os import path as pt
from os import system

# 加载环境变量
load_dotenv()

# 禁用所有日志输出 
logging.getLogger('tensorflow').disabled = True 
logging.getLogger('selenium').setLevel(logging.CRITICAL)
options = Options()
options.add_argument("--log-level=3")
options.add_argument("--disable-infobars")
options.add_argument("excludeswitches")
options.add_argument("--enable-automation")

user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')
init(autoreset=True)

# 导入配置
is_user_data_read = True
try:
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = load(file)
except FileNotFoundError:
    is_user_data_read = False
    user_data = None
# 示例转换格式
def example_conversion_format(examples: str) -> str:
    """
    示例转换格式 

    :param examples: 原始示例内容 
    :return: 返回转换后的示例格式 
    """
    pattern = r"<input>(.*?)</input><output>(.*?)</output>"
    matches = re.findall(pattern, examples, re.DOTALL)
    formatted_examples = []
    for match in matches:
        input_part = match[0].strip().replace("\n", " ")
        output_part = match[1].strip().replace("\n", " ")
        formatted_example = f"输入{input_part}，输出{output_part}"
        formatted_examples.append(formatted_example)
    
    out_example = '示例:'
    for example in formatted_examples:
        out_example += example + '；'
    return out_example

# 等待页面上没有任何元素变化
def is_page_stable(driver: webdriver.Chrome, timeout: int = 60 * 5, interval: float = 1.5) -> bool:
    """
    等待页面上没有任何元素变化

    :param driver: Selenium WebDriver实例
    :param timeout: 超时时间（秒）
    :param interval: 检查间隔（秒）
    :return: 如果页面在指定时间内稳定，则返回True，否则返回False
    """
    start_time = time()
    while time() - start_time < timeout:
        current_hash = _get_page_hash(driver)
        sleep(interval)
        new_hash = _get_page_hash(driver)
        if current_hash == new_hash:
            break
    return current_hash == _get_page_hash(driver)

def _get_page_hash(driver: webdriver.Chrome) -> str:
    """
    捕获页面的DOM快照，并生成一个哈希值

    :param driver: Selenium WebDriver实例
    :return: 返回页面哈希值
    """
    page_source = driver.page_source
    return hashlib.md5(page_source.encode()).hexdigest()

# 添加cookie
def add_driver_cookie(driver: webdriver.Chrome, website: str, cookies: list) -> None:
    """
    添加指定域名下的所有cookie

    :param driver: Selenium WebDriver实例
    :param website: 要添加cookie的网址
    :param cookies: 要添加的cookie列表
    """
    try:
        driver.get(website)
        driver.delete_all_cookies()
        for cookie in cookies:
            if 'name' in cookie and 'value' in cookie and 'domain' in cookie:
                cookie['path'] = '/'
                driver.add_cookie(cookie)
    except Exception as e:
        print(Fore.RED + f"添加cookie时错误:{str(e)}" + Style.RESET_ALL)

# 获取题目+AI话术
def get_problem_saying(pid: str, notes: str) -> str:
    '''
    获取题目+AI话术

    :param pid: 题目ID
    :param notes: 额外提示
    :return: AI话术
    '''
    global user_data
    problem_url = f"{user_data['OJ']['URL']}/api/get-problem-detail?problemId={pid}"
    try:
        response = requests.get(problem_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})
        problem = response.json()['data']['problem']
        problem_str = (
            f"请编写可运行完整程序:{problem['description']}输入:{problem['input']}输出:{problem['output']}"
            .replace("\r", "")
            .replace("<code>", "")
            .replace("</code>", "")
            .replace("<input>", "")
            .replace("</input>", "")
            .replace("<output>", "")
            .replace("</output>", "")
            .replace("\\", "")
        )
        example_str = example_conversion_format(problem['examples'])
        return (
            f"{problem_str}。{example_str}。帮我编写c++程序，不要有其他赘述，并直接输出程序,代码中不要有注释，可开头直接声明std命名空间。{notes}"
            .replace("\n", " ")
        )
    except Exception as e:
        print(Fore.RED + f'获取问题时出错:{str(e)}' + Style.RESET_ALL)
        return ""

def get_training_pids(tid: int, jsessionid_cookie: str) -> list:
    '''
    获取训练集题目ID

    :param tid: 训练集ID
    :param jsessionid_cookie: JSESSIONID的cookie
    :return: 训练集题目ID列表
    '''
    global user_data
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'JSESSIONID={jsessionid_cookie}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(f"{user_data['OJ']['URL']}/api/get-training-problem-list?tid={tid}", headers=headers).json()
    internalpids = [i['pid'] for i in response['data']]

    data={
        'cid': 'null',
        'containsEnd': 'false',
        'gid': 'null',
        'isContestProblemList': 'false',
        'pidList': internalpids
    }
    response2 = requests.post(url=f"{user_data['OJ']['URL']}/api/get-user-problem-status", headers=headers, data=json.dumps(data)).json()
    pids = []
    for i in response['data']:
        if response2['data'][str(i['pid'])]['status'] != 0:
            pids.append(i['problemId'])
    return pids

# 复制代码
def copy_code(driver: webdriver.Chrome) -> None:
    '''
    复制代码

    :param driver: Selenium WebDriver实例
    '''
    try:
        divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='ml-[4px]']")
        target_divs = [div for div in divs if "复制" in div.text]
        if target_divs:
            last_target_div = target_divs[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", last_target_div)
            last_target_div.click()
    except Exception as e:
        print(Fore.YELLOW + '复制时出错,尝试抢修' + Style.RESET_ALL)
        try:
            driver.refresh()
            driver.implicitly_wait(10)
            divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='ml-[4px]']")
            target_divs = [div for div in divs if "复制" in div.text]
            if target_divs:
                last_target_div = target_divs[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_target_div)
                last_target_div.click()
        except Exception as e:
            print(Fore.RED + '抢修失败' + str(e) + Style.RESET_ALL)

def all_code() -> None:
    global driver, user_data, options
    driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']), options=options)
    username = user_data['OJ']['username']
    password = user_data['OJ']['password']
    driver.get(f"{user_data['OJ']['URL']}/home")
    driver.maximize_window()
    driver.implicitly_wait(10)
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary el-button--medium is-round']"))
    )
    login_button.click()
    find_boby = driver.find_element(By.XPATH, "//input[@placeholder='用户名']")
    find_boby.send_keys(username)
    find_boby = driver.find_element(By.XPATH, "//input[@placeholder='密码']")
    find_boby.send_keys(password)
    sleep(0.1)
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary']"))
    )
    submit_button.click()
    sleep(1)

    # 获取cookile
    driver.refresh()
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), {}).get('value')

    # AI
    add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    i = 1
    while True:
        tids = []
        response = requests.get(f"http://82.156.246.133/api/get-training-list?currentPage={i}", headers=headers).json()
        for j in response['data']['records']:
            tids.append(j['id'])
        if len(tids) == 0:
            break
        tids_str = ','.join(map(str, tids))
        training_code(driver=driver, tids=tids_str, jsessionid_cookie=jsessionid_cookie,is_call=True)
        i += 1

def training_code(driver: webdriver.Chrome = None, tids: str = None, jsessionid_cookie: str = None, notes: str = '', is_call: bool = False) -> None:
    global user_data, options
    if not is_call:
        driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']), options=options)
        tids = input('请输入训练编号,用逗号隔开:')
        notes = input('备注:')  # 代码后添加的东西
        
    AI_URL = user_data['AI_URL']

    # 登录
    if not is_call:
        username = user_data['OJ']['username']
        password = user_data['OJ']['password']
        driver.get(f"{user_data['OJ']['URL']}/home")
        driver.maximize_window()
        driver.implicitly_wait(10)
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary el-button--medium is-round']"))
        )
        login_button.click()
        find_boby = driver.find_element(By.XPATH, "//input[@placeholder='用户名']")
        find_boby.send_keys(username)
        find_boby = driver.find_element(By.XPATH, "//input[@placeholder='密码']")
        find_boby.send_keys(password)
        sleep(0.1)
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary']"))
        )
        submit_button.click()
        sleep(1)

        # 获取cookile
        driver.refresh()
        cookies = driver.get_cookies()
        jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), {}).get('value')

        # AI
        add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])

    tidlist = tids.split(',')
    if tidlist[0] != '':
        for tid in tidlist:
            print('start,tid:', str(tid))
            try:
                pids = get_training_pids(tid, jsessionid_cookie)
            except Exception as e:
                print(f'{Fore.RED}获取训练题目ID时出错:{str(e)}{Style.RESET_ALL}')
                continue
            driver.get(AI_URL)
            for i in pids:
                try:
                    problem = get_problem_saying(i, notes)
                except Exception as e:
                    print(Fore.RED + f'获取问题时出错:{str(e)}' + Style.RESET_ALL)
                    continue
                sleep(0.5)
                textarea = driver.find_element(By.XPATH, "//textarea[@placeholder='输入任何问题，Enter发送，Shift + Enter 换行']")
                textarea.click()
                textarea.send_keys(problem)
                sleep(1)
                textarea.send_keys("\n")
                sleep(10)
                if not is_page_stable(driver):
                    print(Fore.RED + "页面不稳定超时" + Style.RESET_ALL)
                    driver.refresh()
                    continue
                copy_code(driver)
                sleep(0.5)
                code = pyperclip.paste()

                headers = {
                    'Content-Type': 'application/json',
                    'Cookie': f'JSESSIONID={jsessionid_cookie}',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                data = {
                    'cid': 0,
                    'code': code,
                    'gid': None,
                    'isRemote': False,
                    'language': 'C++',
                    'pid': i,
                    'tid': None
                }
                response = requests.post(url=f"{user_data['OJ']['URL']}/api/submit-problem-judge", headers=headers, data=dumps(data))
                if response.status_code != 200:
                    print(Fore.RED + f'提交请求异常,status:{response.status_code}' + Style.RESET_ALL)
                now = datetime.now()
                formatted_time = now.strftime("%H:%M:%S")
                print(f"{formatted_time},pid:{i}")
    if not is_call:
        driver.quit()

def problem_code() -> None:
    global options, user_data
    driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']), options=options)
    pids = input('请输入题目ID,用逗号隔开:')
    AI_URL = user_data['AI_URL']
    notes = input('备注:')  # 代码后添加的东西

    # 登录
    username = user_data['OJ']['username']
    password = user_data['OJ']['password']
    driver.get(f"{user_data['OJ']['URL']}/home")
    driver.maximize_window()
    driver.implicitly_wait(10)
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary el-button--medium is-round']"))
    )
    login_button.click()
    find_boby = driver.find_element(By.XPATH, "//input[@placeholder='用户名']")
    find_boby.send_keys(username)
    find_boby = driver.find_element(By.XPATH, "//input[@placeholder='密码']")
    find_boby.send_keys(password)
    sleep(0.1)
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@class='el-button el-button--primary']"))
    )
    submit_button.click()
    sleep(1)

    # 获取cookile
    driver.refresh()
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), {}).get('value')

    # AI
    add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])

    driver.get(AI_URL)
    pidlist = pids.split(',')
    if pidlist[0] != '':
        for pid in pidlist:
            try:
                problem = get_problem_saying(pid, notes)
            except Exception as e:
                print(Fore.RED + f'获取问题时出错:{str(e)}' + Style.RESET_ALL)
                continue
            sleep(0.5)
            textarea = driver.find_element(By.XPATH, "//textarea[@placeholder='输入任何问题，Enter发送，Shift + Enter 换行']")
            textarea.click()
            textarea.send_keys(problem)
            sleep(1)
            textarea.send_keys("\n")
            sleep(10)
            if not is_page_stable(driver):
                print(Fore.RED + "页面不稳定超时" + Style.RESET_ALL)
                driver.refresh()
                continue
            copy_code(driver)
            sleep(0.5)
            code = pyperclip.paste()

            headers = {
                'Content-Type': 'application/json',
                'Cookie': f'JSESSIONID={jsessionid_cookie}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            data = {
                'cid': 0,
                'code': code,
                'gid': None,
                'isRemote': False,
                'language': 'C++',
                'pid': pid,
                'tid': None
            }
            response = requests.post(url=f"{user_data['OJ']['URL']}/api/submit-problem-judge", headers=headers, data=dumps(data))
            if response.status_code != 200:
                print(Fore.RED + f'提交请求异常,status:{response.status_code}' + Style.RESET_ALL)
                driver.quit()
                return
            now = datetime.now()
            formatted_time = now.strftime("%H:%M:%S")
            print(f"{formatted_time},pid:{pid}")
    driver.quit()

def get_user_data() -> None:
    global user_data_path, options, user_data
    user_data = {
        'OJ': {'URL': None, 'username': None, 'password': None},
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

if __name__ == '__main__':
    mode = None
    print(Fore.GREEN + '启动时间:' + str(int((time() - Start_time) * 100) / 100))
    while(mode != '5'):
        print(Fore.BLUE + 'Copyright (c) 2025 WZ一只蚊子\nGitee仓库: https://gitee.com/wzokee/oj-auto-problem-solver-bot' + Back.RED + Fore.WHITE + '\n仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.配置信息\n2.刷训练题目\n3.刷个题\n4.一键刷所有题\n5.退出\n' + Style.RESET_ALL)
        mode = input('请输入序号:')
        system('cls')
        if mode == '1':
            get_user_data()
            system('cls')
            print(f'{Fore.GREEN}配置成功{Style.RESET_ALL}')
            system('pause')
            is_user_data_read = True
        elif mode == '2':
            if is_user_data_read:
                training_code()
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')
        elif mode == '3':
            if is_user_data_read:
                problem_code()
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')
        elif mode == '4':
            if is_user_data_read:
                all_code()
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')