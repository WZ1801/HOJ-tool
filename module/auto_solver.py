from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from colorama import Fore, Back, Style, init
from selenium.webdriver.common.by import By
from selenium import webdriver
from dotenv import load_dotenv
from urllib.parse import quote
from time import sleep, time
from threading import Thread
from os import path as pt
from os import system
import requests
import pyperclip
import hashlib
import logging
import json
import sys
import re

# 加载环境变量
load_dotenv()

log_mode = 1  # 是否是网页请求模式,2启用,1禁用

# 禁用所有日志输出 
logging.getLogger('tensorflow').disabled = True 
logging.getLogger('selenium').setLevel(logging.CRITICAL)
user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')
init(autoreset=True)

# 提交相关
last_submit_time = time()
submit_T = None
submit_list = []

# 导入配置
is_user_data_read = True
user_data = None
try:
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = json.load(file)
except FileNotFoundError:
    print(f'{Fore.RED}未找到配置文件 {user_data_path}{Style.RESET_ALL}')
    system('pause')
    exit()
except Exception as e:
    print(f'{Fore.RED}读取用户数据时发生错误：{e}{Style.RESET_ALL}')
    system('pause')
    exit()

# 爬虫驱动初始化
options = None
try:
    driver_path = user_data['Browser']['Driver_path']
    if not pt.exists(driver_path):
        print(f"{Fore.RED}驱动路径不存在，请检查配置文件{Style.RESET_ALL}")
        
    if user_data['Browser']['Type'] == 'chrome':
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
    elif user_data['Browser']['Type'] == 'edge':
        from selenium.webdriver.edge.service import Service
        from selenium.webdriver.edge.options import Options
    elif user_data['Browser']['Type'] == 'Firefox':
        from selenium.webdriver.firefox.service import Service
        from selenium.webdriver.firefox.options import Options
    else:
        print(f"{Fore.RED}浏览器类型错误，请重新配置并检查配置文件{Style.RESET_ALL}")
        system('pause')
        exit()
        
    options = Options()
    options.add_argument("--log-level=3")
    options.add_argument("--disable-infobars")
    options.add_argument("excludeswitches")
    options.add_argument("--enable-automation")
    
except Exception as e:
    print(f"{Fore.RED}配置文件有误，请重新配置并检查:{e}{Style.RESET_ALL}")
    system('pause')
    exit()

def send_log(type: str = 'info', message: str = '', mode: int = 1) -> None:
    try:
        match type:
            case 'info':
                match mode:
                    case 1:
                        print(message)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': 'info', 'message': message})
            case 'success':
                match mode:
                    case 1:
                        print(Fore.GREEN + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': 'success', 'message': message})
            case 'warning':
                match mode:
                    case 1:
                        print(Fore.YELLOW + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': 'warning', 'message': message})
            case 'error':
                match mode:
                    case 1:
                        print(Fore.RED + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': 'error', 'message': message})
            case 'debug':
                match mode:
                    case 1:
                        print(Fore.BLUE + message + Style.RESET_ALL)
                    case 2:
                        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': 'debug', 'message': message})
    except: 
        pass

# 获取driver
def get_driver():
    global user_data, options, log_mode
    if user_data['Browser']['Type'] == 'chrome':
        service = Service(user_data['Browser']['Driver_path'])
        return webdriver.Chrome(service=service, options=options)
    elif user_data['Browser']['Type'] == 'edge':
        service = Service(user_data['Browser']['Driver_path'])
        return webdriver.Edge(service=service, options=options)
    elif user_data['Browser']['Type'] == 'Firefox':
        service = Service(user_data['Browser']['Driver_path'])
        return webdriver.Firefox(service=service, options=options)
    else:
        send_log('error', '浏览器类型错误，请重新配置并检查配置文件', log_mode)

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
        input_part = match[0].strip()
        output_part = match[1].strip()
        formatted_example = f"输入{input_part}，输出{output_part}"
        formatted_examples.append(formatted_example)
    
    out_example = '示例:'
    for example in formatted_examples:
        out_example += example + '；'
    return out_example

# 等待页面上没有任何元素变化
def is_page_stable(driver: webdriver.Chrome, timeout: int = 60 * 10, interval: float = 1) -> bool:
    """
    等待页面上没有任何元素变化

    :param driver: Selenium WebDriver实例
    :param timeout: 超时时间（秒）
    :param interval: 检查间隔（秒）
    :return: 如果页面在指定时间内稳定，则返回True，否则返回False
    """
    driver.timeouts.implicit_wait = 0.5
    start_time = time()
    while True:
        if time() - start_time > timeout:
            return False
        current_hash = _get_page_hash(driver)
        sleep(interval)
        try:
            driver.find_element(By.XPATH, '//button[@class="size-32px rounded-full cursor-pointer flex justify-center items-center border-1px  bg-[#fff] hover:bg-[#F6F7F9] border-[rgba(0,0,0,0.1)] absolute -top-12px transform -translate-y-full"]').click()
            current_hash = _get_page_hash(driver)
        except: 
            pass
        new_hash = _get_page_hash(driver)
        if current_hash == new_hash:
            break
    return True

# 获取页面的哈希值
def _get_page_hash(driver: webdriver.Chrome) -> str:
    """
    捕获页面的DOM快照，并生成一个哈希值

    :param driver: Selenium WebDriver实例
    :return: 返回页面哈希值
    """
    page_source = driver.page_source
    return hashlib.md5(page_source.encode()).hexdigest()

# 获取题目+AI话术
def get_problem_saying(pid: str, notes: str) -> str:
    '''
    获取题目+AI话术

    :param pid: 题目ID
    :param notes: 额外提示
    :return: AI话术
    '''
    global user_data, log_mode
    problem_url = f"{user_data['OJ']['APIURL']}/api/get-problem-detail?problemId={quote(pid)}"
    try:
        response = requests.get(problem_url, headers={'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'})
        
        # 检查HTTP响应状态
        if response.status_code != 200:
            send_log('error', f'获取问题失败，HTTP状态码: {response.status_code}', log_mode)
            return ""
        
        # 解析JSON响应
        response_data = response.json()
        
        # 检查响应结构
        if not response_data or 'data' not in response_data or 'problem' not in response_data['data']:
            send_log('error', f'响应数据结构不正确: {response_data}', log_mode)
            return ""
        
        problem = response_data['data']['problem']
        
        # 检查problem是否为None
        if problem is None:
            send_log('error', '获取到的problem数据为None', log_mode)
            return ""
        
        # 检查必要的字段是否存在
        required_fields = ['description', 'input', 'output', 'examples']
        for field in required_fields:
            if field not in problem:
                send_log('error', f'problem数据缺少必要字段: {field}', log_mode)
                return ""
        
        problem_str = (
            f"请编写可运行完整程序,以下描述\\n代表换行:{problem['description']}输入:{problem['input']}输出:{problem['output']}"
            .replace("\r", "")
            .replace("<code>", "")
            .replace("</code>", "")
            .replace("<input>", "")
            .replace("</input>", "")
            .replace("<output>", "")
            .replace("</output>", "")
            .replace("\\", "")
            .replace("<pre>", "")
            .replace("</pre>", "")
            .replace("$", "")
        )
        example_str = example_conversion_format(problem['examples'])
        if problem.get('isFileIO', False):
            fileIOstr = f"程序为文件IO输入输出，输入文件名为：{problem.get('ioReadFileName', '')}，输出文件名为：{problem.get('ioWriteFileName', '')}。"
        else:
            fileIOstr = ""
        return (
            f"{problem_str}。{fileIOstr}{example_str}。帮我编写C++程序，不要有其他赘述，并直接输出程序,代码中不要有注释，可开头直接声明std命名空间，尽可能优化，达到数据极限。{notes}"
            .replace("\n", "\\n")
        )
    except requests.RequestException as e:
        send_log('error', f'网络请求出错: {str(e)}', log_mode)
        return ""
    except KeyError as e:
        send_log('error', f'响应数据缺少键值: {str(e)}', log_mode)
        return ""
    except Exception as e:
        send_log('error', f'获取问题时出错: {str(e)}', log_mode)
        return ""

# 获取训练集题目ID
def get_training_pids(tid: int, jsessionid_cookie: str) -> list:
    '''
    获取训练集题目ID

    :param tid: 训练集ID
    :param jsessionid_cookie: JSESSIONID的cookie
    :return: 训练集题目ID列表
    '''
    global user_data
    try:
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={jsessionid_cookie}',
            'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'
        }
        response = requests.get(f"{user_data['OJ']['APIURL']}/api/get-training-problem-list?tid={tid}", headers=headers).json()
        internalpids = [i['pid'] for i in response['data']]

        data = {
            'cid': 'null',
            'containsEnd': 'false',
            'gid': 'null',
            'isContestProblemList': 'false',
            'pidList': internalpids
        }
        response2 = requests.post(url=f"{user_data['OJ']['APIURL']}/api/get-user-problem-status", headers=headers, json=data).json()
        pids = []
        for i in response['data']:
            if response2['data'][str(i['pid'])]['status'] != 0:
                pids.append(i['problemId'])
        return pids
    except Exception as e:
        send_log('error', f'训练获取题目时出错:{e}', 1)
        return []

# 复制代码
def copy_code(driver: webdriver.Chrome) -> None:
    '''
    复制代码

    :param driver: Selenium WebDriver实例
    '''
    try:
        divs = driver.find_elements(By.XPATH, '//div[@class="ml-[4px]"]')
        target_divs = [div for div in divs if "复制" in div.text]
        if target_divs:
            last_target_div = target_divs[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", last_target_div)
            last_target_div.click()
    except Exception as e:
        global log_mode
        send_log('warning', '复制时出错,尝试抢修', log_mode)
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
            send_log('error', '抢修失败', log_mode)

# 登录并获取JSESSIONID cookie
def login_and_get_cookie(driver: webdriver.Chrome, url: str, username: str, password: str) -> str:
    """
    登录并获取JSESSIONID cookie

    :param driver: Selenium WebDriver实例
    :param url: 登录APIURL
    :param username: 用户名
    :param password: 密码
    :return: JSESSIONID cookie值
    """
    driver.get(url)
    # 尝试最大化窗口，如果失败则忽略
    try:
        driver.maximize_window()
    except Exception as e:
        global log_mode
        send_log("warning", f"无法最大化窗口:{e}", log_mode)
        try:
            driver.set_window_size(1920, 1080)
        except Exception:
            pass
    
    driver.implicitly_wait(10)
    login_button = driver.find_element(By.XPATH, '//*[@id="header"]/ul/div[2]/button')
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
    driver.refresh()
    sleep(1)
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), {}).get('value')
    return jsessionid_cookie

def submit_code_thread() -> None:
    global last_submit_time, submit_list
    while True:
        if time() - last_submit_time > 10 and len(submit_list) > 0:
            submit_codee = submit_code(*submit_list[0][:4])
            last_submit_time = time()
            if submit_list[0][4] == True:
                callback_submission(submit_list[0][1], submit_codee, submit_list[0][2])
            submit_list.pop(0)
        sleep(1)

def submit_code(code: str, JESSIONID: str, pid: str, lang: str) -> int:
    try:
        global user_data, log_mode
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={JESSIONID}',
            'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'
        }
        data = {
            'cid': 0,
            'code': code,
            'gid': None,
            'isRemote': False,
            'language': lang,
            'pid': pid,
            'tid': None
        }
        response = requests.post(url=f"{user_data['OJ']['APIURL']}/api/submit-problem-judge", headers=headers, json=data)
        if response.status_code != 200:
            send_log('error', f'提交代码请求失败,状态码：{response.status_code}', log_mode)
            return False
        return response.json()['data']['submitId']
    except Exception as e:
        send_log('warning', f'提交代码失败{e}', log_mode)
        return False

def callback_submission(JSESSIONID: str, submitId: int, pid: str, timeout: int = 30, interval: float = 1): 
    '''回调提交'''
    
    global user_data, log_mode
    cookies = {
        'JSESSIONID': f'{JSESSIONID}',
    }
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Url-Type': 'general',
        'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00',
    }
    params = {
        'submitId': f'{submitId}',
    }
    response = None
    start_time = time()
    try:
        while response is None or response.json()['data']['submission']['status'] == 7:
            response = requests.get(
                f'{user_data["OJ"]["APIURL"]}/api/get-submission-detail',
                params=params,
                cookies=cookies,
                headers=headers,
            )
            sleep(interval)
            if time() - start_time > timeout:
                send_log('warning', f'回调查询超时', log_mode)
                return
    except Exception as e:
        send_log('warning', f'回调查询失败:{e}', log_mode)
        return
    
    response = requests.get(
        f'{user_data["OJ"]["APIURL"]}/api/get-submission-detail',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    try:
        if str(response.json()['data']['submission']['status']) != '0':
            send_log('warning', f'{pid}:AI Wrong Answer!', log_mode)
            response = requests.get(
                f'{user_data["OJ"]["APIURL"]}/api/get-all-case-result',
                params=params,
                cookies=cookies,
                headers=headers,
            )
            judgeCaseList = []
            for judgeCase in response.json()['data']['judgeCaseList']:
                judgeCaseList.append((judgeCase['inputData'], judgeCase['outputData']))
            
            KillerCode = 'import hashlib,sys\na=hashlib.md5(sys.stdin.read().replace(\'\\n\', \'\').encode()).hexdigest()\n'
            is_first_if = True
            for judgeCase in judgeCaseList:
                hash_value = hashlib.md5((judgeCase[0].replace('\n', '')).encode()).hexdigest()
                if is_first_if:
                    KillerCode += f'a=="{hash_value}"'
                    is_first_if = False
                else:
                    KillerCode += f'or a=="{hash_value}"'
                KillerCode += f'and print("{judgeCase[1].replace(chr(92), chr(92)*2).replace(chr(10), chr(92)+"n").replace(chr(39), chr(92)+chr(39)).replace(chr(34), chr(92)+chr(34))}")'
            
            if is_first_if:
                send_log('warning', f'回调提交失败: 数据点过长', log_mode)
                return

            submit_list.append([KillerCode, JSESSIONID, pid, 'Python3', False])
            send_log('success', f'回调抢救成功,结果未知', log_mode)
        else:
            send_log('success', f'AI Accepted!', log_mode)
            
    except Exception as e:
        send_log('warning', f'回调提交失败: {e}', log_mode)

def all_code(is_web_call=False) -> None:
    global driver, user_data, submit_T, log_mode
    if submit_T is None:
        submit_T = Thread(target=submit_code_thread)
        submit_T.start()
    
    driver = get_driver()

    # 登录
    jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])

    if not is_web_call:
        print('请自行操作登录360bot')
        
    driver.get('https://bot.n.cn/')
    
    if not is_web_call:
        system('pause')
    else:
        log_mode = 2
        while True:
            sleep(0.5)
            try:
                response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
                if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                    break
            except Exception as e:
                exit()
                
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'
    }
    i = 1
    while True:
        tids = []
        response = requests.get(f"{user_data['OJ']['APIURL']}/api/get-training-list?currentPage={i}", headers=headers).json()
        for j in response['data']['records']:
            tids.append(j['id'])
        if len(tids) == 0:
            break
        tids_str = ','.join(map(str, tids))
        training_code(driver=driver, tids=tids_str, jsessionid_cookie=jsessionid_cookie, is_call=True, is_web_call=is_web_call)
        i += 1
        
    if is_web_call:
        try:
            requests.get("http://127.0.0.1:1146/api/auto_solver/stopp")
        except:
            pass
        driver.quit()
        exit()

def training_code(driver=None, tids: str = None, jsessionid_cookie: str = None, notes: str = '', is_call: bool = False, is_web_call=False, web_call_mode=1) -> None:
    global user_data, submit_T, log_mode
    if submit_T is None: 
        submit_T = Thread(target=submit_code_thread)
        submit_T.start()
        
    if not is_call:
        tids = input('请输入训练编号,用逗号隔开:')
        notes = input('备注:')  # 代码后添加的东西
        
        # 登录
        driver = get_driver()
        jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])

        print('请自行操作登录360bot')
        driver.get('https://bot.n.cn/')
        system('pause')
        
    if is_web_call and web_call_mode == 2 and driver is None:
        log_mode = 2
        # 登录
        driver = get_driver()
        jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        driver.get('https://bot.n.cn/')
        while True:
            sleep(0.5)
            try:
                response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
                if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                    break
            except Exception as e:
                try:
                    pass  # 发送错误包
                except: 
                    exit()

    tidlist = tids.split(',')
    if tidlist[0] != '':
        for tid in tidlist:
            send_log('info', f'开始训练:{tid}', log_mode)
            try:
                pids = get_training_pids(tid, jsessionid_cookie)
            except Exception as e:
                send_log('error', f'获取训练题目ID时出错:{str(e)}', log_mode)
                continue
            # 调用 problem_code 处理每个 pid
            problem_code(driver=driver, pids=",".join(map(str, pids)), notes=notes, jsessionid_cookie=jsessionid_cookie, is_call=True, is_web_call=is_web_call)
            
    if not is_call:
        driver.quit()
        
    if is_web_call and web_call_mode == 2:
        try:
            requests.get("http://127.0.0.1:1146/api/auto_solver/stopp")
        except:
            pass

def problem_code(driver=None, pids: str = None, notes: str = '', jsessionid_cookie: str = None, is_call: bool = False, is_web_call=False, web_call_mode=1) -> None:
    global log_mode
    # 提交代码线程
    global submit_T
    if submit_T is None: 
        submit_T = Thread(target=submit_code_thread)
        submit_T.start()
    
    global user_data, submit_list
    if not is_call:
        pids = input("请输入题目编号，用逗号分隔：")
        driver = get_driver()

        # 登录
        jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        
        print('请自行操作登录360bot')
        driver.get('https://bot.n.cn/')
        system('pause')
        
    if web_call_mode == 2 and is_web_call:
        driver = get_driver()
        log_mode = 2

        # 登录
        jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        driver.get('https://bot.n.cn/')

        while True:
            sleep(0.5)
            try:
                response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
                if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                    break
            except Exception as e:
                try:
                    pass  # 发送错误包
                except: 
                    exit()
                    
    if is_web_call:
        try:
            if requests.get("http://127.0.0.1:1146/api/auto_solver/status").json()['stop_flag'] == True:
                requests.get("http://127.0.0.1:1146/api/auto_solver/stopp")
                driver.quit()
                exit()
        except:
            pass

    driver.get(user_data['AI_URL'])
    pidlist = pids.split(',')
    if pidlist[0] != '':
        for pid in pidlist:
            try:
                problem = get_problem_saying(pid, notes)
            except Exception as e:
                send_log('error', f'获取问题时出错:{str(e)}', log_mode)
                continue
            sleep(0.5)
            textarea = driver.find_element(By.XPATH, "//textarea[last()]")
            textarea.click()
            for _ in [str(problem)[i:i+7] for i in range(0, len(str(problem)), 7)]:
                textarea.send_keys(_)
            sleep(0.5)
            textarea.send_keys("\n")
            sleep(7)
            if not is_page_stable(driver):
                send_log("error", "页面不稳定超时", log_mode)
                driver.refresh()
                continue
            copy_code(driver)
            sleep(0.3)
            code = pyperclip.paste()
            submit_list.append([code, jsessionid_cookie, pid, 'C++', True])
            
    if not is_call:
        driver.quit()
        
    if is_web_call and web_call_mode == 2:
        try:
            requests.get("http://127.0.0.1:1146/api/auto_solver/stopp")
        except:
            pass

def main() -> None:
    global submit_T
    submit_T = Thread(target=submit_code_thread)
    submit_T.start()
    mode = None
    while mode != '4':
        print(Fore.BLUE + '欢迎使用OJ自动刷题爬虫！\n作者：WZ一只蚊子\nGitee仓库: https://gitee.com/wzokee/hoj-tool\n' + Back.RED + Fore.WHITE + '仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.刷训练题目\n2.刷个题\n3.一键刷所有题\n4.退出\n' + Style.RESET_ALL)
        mode = input('请输入序号:')
        system('cls')
        if mode == '1':
            if is_user_data_read:
                try:
                    training_code()
                except Exception as e:
                    print(Fore.RED + f'刷题过程中出现未知错误: {str(e)}' + Style.RESET_ALL)
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')
        elif mode == '2':
            if is_user_data_read:
                try:
                    problem_code()
                except Exception as e:
                    print(Fore.RED + f'刷题过程中出现未知错误: {str(e)}' + Style.RESET_ALL)
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')
        elif mode == '3':
            if is_user_data_read:
                try:
                    all_code()
                except Exception as e:
                    print(Fore.RED + f'刷题过程中出现未知错误: {str(e)}' + Style.RESET_ALL)
                print(f'{Fore.GREEN}刷题结束{Style.RESET_ALL}')
                system('pause')
                system('cls')
            else:
                print(f'{Fore.YELLOW}未导入配置,请先配置信息{Style.RESET_ALL}')
                system('pause')
                system('cls')
        elif mode == '4':
            exit()

if __name__ == '__main__':
    main()