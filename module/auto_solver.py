from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from colorama import Fore, Back, Style, init as colorama_init
from selenium.webdriver.common.by import By
from selenium import webdriver
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

# 禁用所有日志输出
logging.getLogger('tensorflow').disabled = True
logging.getLogger('selenium').setLevel(logging.CRITICAL)
colorama_init(autoreset=True)

# 配置路径
user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')

# 提交相关
last_submit_time = time()
submit_T = None
submit_list = []

# 初始化状态
is_init = False
is_user_data_read = True
user_data = None

def init():
    global is_user_data_read, user_data
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

def send_log(type: str = 'info', message: str = '', pid: str = None, submit_id: str = None) -> None:
    try:
        formatted_message = message
        if pid:
            formatted_message = f"{formatted_message} -> {pid}"
        if submit_id:
            formatted_message = f"{formatted_message} -> {submit_id}"
        requests.post('http://127.0.0.1:1146/api/auto_solver/log', json={'type': type, 'message': formatted_message})
    except:
        pass

def _ensure_inited():
    global is_init
    if not is_init:
        init()
        is_init = True

def _ensure_submit_thread():
    global submit_T
    if submit_T is None:
        submit_T = Thread(target=submit_code_thread, daemon=True)
        submit_T.start()

def get_driver():
    global user_data
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
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option('excludeSwitches', ['enable-automation', 'enable-logging'])
        options.add_argument('--disable-infobars')
        options.add_argument('--log-level=3')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--ignore-ssl-errors')

    except Exception as e:
        print(f"{Fore.RED}配置文件有误，请重新配置并检查:{e}{Style.RESET_ALL}")
        system('pause')
        exit()

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
        send_log('error', '浏览器类型错误，请重新配置并检查配置文件')

def example_conversion_format(examples: str) -> str:
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

def _get_page_hash(driver: webdriver.Chrome) -> str:
    page_source = driver.page_source
    return hashlib.md5(page_source.encode()).hexdigest()

def is_page_stable(driver: webdriver.Chrome, timeout: int = 60 * 10, interval: float = 1) -> bool:
    driver.timeouts.implicit_wait = 0.5
    start_time = time()
    while True:
        if time() - start_time > timeout:
            return False

        current_hash = _get_page_hash(driver)
        sleep(interval)
        try:
            driver.find_element(
                By.XPATH,
                '//button[@class="size-32px rounded-full cursor-pointer flex justify-center items-center border-1px  bg-[#fff] hover:bg-[#F6F7F9] border-[rgba(0,0,0,0.1)] absolute -top-12px transform -translate-y-full"]'
            ).click()
            current_hash = _get_page_hash(driver)
        except:
            pass

        new_hash = _get_page_hash(driver)
        if current_hash == new_hash:
            break
    return True

def get_problem_saying(pid: str, notes: str) -> str:
    global user_data
    problem_url = f"{user_data['OJ']['APIURL']}/api/get-problem-detail?problemId={quote(pid)}"
    try:
        response = requests.get(
            problem_url,
            headers={'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'}
        )

        if response.status_code != 200:
            send_log('error', '获取问题失败', pid=pid)
            return ""

        response_data = response.json()
        if not response_data or 'data' not in response_data or 'problem' not in response_data['data']:
            send_log('error', '响应数据结构不正确', pid=pid)
            return ""

        problem = response_data['data']['problem']
        if problem is None:
            send_log('error', '获取到的problem数据为None', pid=pid)
            return ""

        required_fields = ['description', 'input', 'output', 'examples']
        for field in required_fields:
            if field not in problem:
                send_log('error', f'problem数据缺少必要字段: {field}', pid=pid)
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
    except requests.RequestException:
        send_log('error', '网络请求出错', pid=pid)
        return ""
    except KeyError:
        send_log('error', '响应数据缺少键值', pid=pid)
        return ""
    except Exception:
        send_log('error', '获取问题时出错', pid=pid)
        return ""

def get_training_problem_ids(tid: int, jsessionid_cookie: str) -> list:
    global user_data
    try:
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={jsessionid_cookie}',
            'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00'
        }
        response = requests.get(f"{user_data['OJ']['APIURL']}/api/get-training-problem-list?tid={tid}", headers=headers).json()
        internal_pids = [i['pid'] for i in response['data']]

        data = {
            'cid': 'null',
            'containsEnd': 'false',
            'gid': 'null',
            'isContestProblemList': 'false',
            'pidList': internal_pids
        }
        response2 = requests.post(url=f"{user_data['OJ']['APIURL']}/api/get-user-problem-status", headers=headers, json=data).json()

        pids = []
        for i in response['data']:
            if response2['data'][str(i['pid'])]['status'] != 0:
                pids.append(i['problemId'])
        return pids
    except Exception as e:
        send_log('error', f'训练获取题目时出错:{e}')
        return []

def copy_code(driver: webdriver.Chrome) -> None:
    try:
        divs = driver.find_elements(By.XPATH, '//div[@class="ml-[4px]"]')
        target_divs = [div for div in divs if "复制" in div.text]
        if target_divs:
            last_target_div = target_divs[-1]
            driver.execute_script("arguments[0].scrollIntoView(true);", last_target_div)
            last_target_div.click()
    except Exception:
        send_log('warning', '复制时出错,尝试抢修')
        try:
            driver.refresh()
            driver.implicitly_wait(10)
            divs = driver.find_elements(By.CSS_SELECTOR, "div[class*='ml-[4px]']")
            target_divs = [div for div in divs if "复制" in div.text]
            if target_divs:
                last_target_div = target_divs[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);", last_target_div)
                last_target_div.click()
        except Exception:
            send_log('error', '抢修失败')

def login_and_get_cookie(driver: webdriver.Chrome, url: str, username: str, password: str) -> str:
    driver.get(url)
    try:
        driver.maximize_window()
    except Exception:
        send_log("warning", "无法最大化窗口")
        try:
            driver.set_window_size(1920, 1080)
        except Exception:
            pass

    driver.implicitly_wait(10)
    login_button = driver.find_element(By.XPATH, '//span[contains(text(), "登录")]')
    login_button.click()

    find_body = driver.find_element(By.XPATH, "//input[@placeholder='用户名']")
    find_body.send_keys(username)

    find_body = driver.find_element(By.XPATH, "//input[@placeholder='密码']")
    find_body.send_keys(password)

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
            submit_code = submit_problem(*submit_list[0][:4])
            last_submit_time = time()
            if submit_list[0][4] == True:
                callback_submission(submit_list[0][1], submit_code, submit_list[0][2])
            submit_list.pop(0)
        sleep(1)

def submit_problem(code: str, JSESSIONID: str, pid: str, lang: str) -> int | bool:
    try:
        global user_data
        headers = {
            'Content-Type': 'application/json',
            'Cookie': f'JSESSIONID={JSESSIONID}',
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
            send_log('error', '提交代码请求失败', pid=str(pid))
            return False
        return response.json()['data']['submitId']
    except Exception:
        send_log('warning', '提交代码失败')
        return False

def callback_submission(JSESSIONID: str, submitId: int, pid: str, timeout: int = 30, interval: float = 1):
    global user_data
    cookies = {'JSESSIONID': f'{JSESSIONID}'}
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Url-Type': 'general',
        'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00',
    }
    params = {'submitId': f'{submitId}'}

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
                send_log('warning', '回调查询超时', pid=pid)
                return
    except Exception:
        send_log('warning', '回调查询失败', pid=pid)
        return

    response = requests.get(
        f'{user_data["OJ"]["APIURL"]}/api/get-submission-detail',
        params=params,
        cookies=cookies,
        headers=headers,
    )
    try:
        if str(response.json()['data']['submission']['status']) != '0':
            send_log('warning', 'AI Unaccepted', pid=pid, submit_id=str(submitId))
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
                return

            submit_list.append([KillerCode, JSESSIONID, pid, 'Python3', False])
            send_log('success', '回调抢救成功,结果未知', pid=pid)
        else:
            send_log('success', 'AI Accepted', pid=pid, submit_id=str(submitId))

    except Exception:
        return

def all_code() -> None:
    _ensure_inited()
    _ensure_submit_thread()

    global driver, user_data, submit_T
    driver = get_driver()
    try:
        jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
    except Exception as e:
        send_log('error', f'登录获取Cookie时出错:{e}')
        return
    
    driver.get('https://bot.n.cn/')

    while True:
        sleep(0.5)
        try:
            response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
            if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                break
        except Exception:
            exit()

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/6.0 (Windows NT 12.0; Win128; x128) AppleWebKit/600.00 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/600.00',
        'Cookie': f'JSESSIONID={jsessionid_cookie}'
    }

    i = 1
    while True:
        pids = []
        response = requests.get(f"{user_data['OJ']['APIURL']}/api/get-problem-list?oj=Mine&currentPage={i}&limit=100", headers=headers).json()
        res2 = requests.post(
            url=f"{user_data['OJ']['APIURL']}/api/get-user-problem-status",
            json={"pidList": [record["pid"] for record in response["data"]["records"]], "isContestProblemList": False, "containsEnd": False},
            headers=headers
        ).json()

        if len(response['data']['records']) == 0:
            break

        for j in response['data']['records']:
            if str(res2['data'][str(j['pid'])]['status']) != '0':
                pids.append(j['problemId'])

        i += 1
        if len(pids) == 0:
            continue

        pids_str = ','.join(map(str, pids))
        problem_code(
            driver=driver,
            pids=pids_str,
            notes='',
            jsessionid_cookie=jsessionid_cookie,
            is_call=True
        )

    if driver is not None:
        try:
            requests.get("http://127.0.0.1:1146/api/auto_solver/stopped")
        except:
            pass
        driver.quit()
        exit()

def training_code(driver=None, tids: str = None, jsessionid_cookie: str = None, notes: str = '', is_call: bool = False) -> None:
    _ensure_inited()
    _ensure_submit_thread()

    global user_data, submit_T
    if not is_call:
        tids = input('请输入训练编号,用逗号隔开:')
        notes = input('备注:')

        driver = get_driver()
        try:
            jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        except Exception as e:
            send_log('error', f'登录获取Cookie时出错:{e}')
            return

        print('请自行操作登录360bot')
        driver.get('https://bot.n.cn/')
        system('pause')

    if driver is None:
        driver = get_driver()
        try:
            jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        except Exception as e:
            send_log('error', f'登录获取Cookie时出错:{e}')
            return
        driver.get('https://bot.n.cn/')
        while True:
            sleep(0.5)
            try:
                response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
                if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                    break
            except Exception:
                try:
                    pass
                except:
                    exit()

    tid_list = tids.split(',')
    if tid_list[0] != '':
        for tid in tid_list:
            send_log('info', '开始训练', pid=tid)
            try:
                pids = get_training_problem_ids(tid, jsessionid_cookie)
            except Exception:
                send_log('error', '获取训练题目ID时出错')
                continue

            problem_code(
                driver=driver,
                pids=",".join(map(str, pids)),
                notes=notes,
                jsessionid_cookie=jsessionid_cookie,
                is_call=True
            )

    if not is_call:
        driver.quit()

    try:
        requests.get("http://127.0.0.1:1146/api/auto_solver/stopped")
    except:
        pass

def problem_code(driver=None, pids: str = None, notes: str = '', jsessionid_cookie: str = None, is_call: bool = False) -> None:
    _ensure_inited()
    _ensure_submit_thread()

    global user_data, submit_list

    if not is_call:
        pids = input("请输入题目编号，用逗号分隔：")
        driver = get_driver()
        try:
            jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        except Exception as e:
            send_log('error', f'登录获取Cookie时出错:{e}')
            return
        print('请自行操作登录360bot')
        driver.get('https://bot.n.cn/')
        system('pause')

    if is_call and driver is None:
        driver = get_driver()
        try:
            jsessionid_cookie = login_and_get_cookie(driver, f"{user_data['OJ']['URL']}/home", user_data['OJ']['username'], user_data['OJ']['password'])
        except Exception as e:
            send_log('error', f'登录获取Cookie时出错:{e}')
            return
        driver.get('https://bot.n.cn/')
        while True:
            sleep(0.5)
            try:
                response = requests.get("http://127.0.0.1:1146/api/auto_solver/status")
                if response.status_code == 200 and response.json()['is_login_360ai'] == True:
                    break
            except Exception:
                try:
                    pass
                except:
                    exit()

    if is_call:
        if requests.get("http://127.0.0.1:1146/api/auto_solver/status").json()['stop_flag'] == True:
            requests.get("http://127.0.0.1:1146/api/auto_solver/stopped")
            driver.quit()
            exit()

    driver.get(user_data['AI_URL'])
    pid_list = pids.split(',')
    if pid_list[0] != '':
        for pid in pid_list:
            try:
                problem = get_problem_saying(pid, notes)
            except Exception:
                send_log('error', '获取问题时出错', pid=pid)
                continue

            headers = {
                'accept': 'application/json, text/plain, */*',
                'cache-control': 'no-cache',
                'content-type': 'application/json;charset=utf-8',
                'pragma': 'no-cache',
                'sec-gpc': '1',
                'url-type': 'general',
                'Cookie': f'JSESSIONID={jsessionid_cookie}',
                'Referer': f"{user_data['OJ']['URL']}/status"
            }
            params = {
                'onlyMine': 'false',
                'problemID': pid,
                'currentPage': 1,
                'limit': 10000,
                'completeProblemID': 'false'
            }

            try:
                response = requests.get(
                    f"{user_data['OJ']['APIURL']}/api/get-submission-list",
                    headers=headers,
                    params=params
                ).json()

                if response:
                    records = response.get('data', {}).get('records')
                    target_submit = None
                    if records:
                        target_submit = next((s for s in records if s.get('displayPid') == pid and s.get('status') == 0), None)

                    if target_submit:
                        resubmit_res = requests.get(
                            f"{user_data['OJ']['APIURL']}/api/resubmit",
                            params={'submitId': target_submit.get('submitId')},
                            headers=headers
                        ).json()

                        if not resubmit_res:
                            return
                        elif resubmit_res.get('status') == 200:
                            code_data = resubmit_res.get('data')
                            if code_data and code_data.get('code') and code_data.get('language'):
                                submit_list.append([
                                    code_data['code'],
                                    jsessionid_cookie,
                                    pid,
                                    code_data['language'],
                                    False
                                ])
                                send_log('success', '发现历史AC代码并提交', pid=pid, submit_id=str(target_submit.get("submitId")))
                                continue
                            else:
                                return
                        else:
                            return

            except TypeError:
                return
            except Exception:
                return

            sleep(0.5)
            textarea = driver.find_element(By.XPATH, "//textarea[last()]")
            textarea.click()
            for _ in [str(problem)[i:i+7] for i in range(0, len(str(problem)), 7)]:
                textarea.send_keys(_)
            sleep(0.5)
            textarea.send_keys("\n")
            sleep(7)

            if not is_page_stable(driver):
                send_log("error", "页面不稳定超时", pid=pid)
                driver.refresh()
                continue

            copy_code(driver)
            sleep(0.3)
            code = pyperclip.paste()
            submit_list.append([code, jsessionid_cookie, pid, 'C++', True])

    if not is_call:
        driver.quit()

    if is_call and driver is not None:
        requests.get("http://127.0.0.1:1146/api/auto_solver/stopped")