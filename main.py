from time import time, sleep

Start_time = time()

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from os import path as pt
import subprocess
from colorama import init, Fore, Back, Style
from os import system
from json import dump, load, dumps
from datetime import datetime
import requests, pyperclip, hashlib, re, logging, sys

# 禁用所有日志输出 
logging.getLogger('tensorflow').disabled  = True 
logging.getLogger('selenium').setLevel(logging.CRITICAL)
options = Options()
options.add_argument("--log-level=3")

user_data_path = pt.join(pt.dirname(pt.normpath(sys.argv[0])), 'user_data.json')
init(autoreset=True)
#导入配置
is_user_data_read = True
try:
    with open(user_data_path, 'r', encoding='utf-8') as file:
        user_data = load(file)
except FileNotFoundError:
    is_user_data_read = False
    user_data = None

#示例转换格式
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

#等待页面上没有任何元素变化
def is_page_stable(driver: webdriver.Chrome, timeout: int = 60 * 3, interval: float = 1.5) -> bool:
    """
    等待页面上没有任何元素变化

    :param driver: Selenium WebDriver实例
    :param timeout: 超时时间（秒）
    :param interval: 检查间隔（秒）
    :return: 如果页面在指定时间内稳定，则返回True，否则返回False
    """
    start_time = time()
    while time()  - start_time < timeout:
        # 捕获页面当前状态
        current_hash = _get_page_hash(driver)
        # 等待指定间隔
        sleep(interval)
        # 捕获页面状态
        new_hash = _get_page_hash(driver)
        if current_hash == new_hash:
            break
    final_hash = _get_page_hash(driver)
    if current_hash == final_hash:
        return True
    else:
        return False
def _get_page_hash(driver: webdriver.Chrome) -> str:
    """
    捕获页面的DOM快照，并生成一个哈希值
    """
    # 获取页面源代码
    page_source = driver.page_source
    # 使用哈希函数生成页面状态的唯一标识
    return hashlib.md5(page_source.encode()).hexdigest()

#添加cookie
def add_driver_cookie(driver: webdriver.Chrome, website: str, cookies: list) -> None:
    """
    添加指定域名下的所有cookie
    """
    try:
        driver.get(website)
        driver.delete_all_cookies()
        for cookie in cookies:
            if 'name' in cookie and 'value' in cookie and 'domain' in cookie:
                cookie['path'] = '/'
                # print(cookie)
                driver.add_cookie(cookie)
    except Exception as e:
        print(Fore.RED + f"添加cookie时错误:{str(e)}" + Style.RESET_ALL)

#获取题目+AI话术
def get_problem_saying(pid: str, notes: str) -> str:
    global user_data
    '''
    #获取题目+AI话术
    '''
    problem_url = f"{user_data['OJ']['URL']}/api/get-problem-detail?problemId=" + pid
    # print(problem_url)
    problem = requests.get(url = problem_url, headers = {'User-Agent': 'Mozilla/7.0 (Windows NT 13.0; Win256; x256) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/514.0.0.0 Safari/987.36'})
    problem = problem.json()
    # print(problem)
    problem = problem['data']['problem']
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
    problem_str = (
        f"{problem_str}。{example_str}。帮我编写c++程序，不要有其他赘述，并直接输出程序,代码中不要有注释，可开头直接声明std命名空间。{notes}"
        .replace('\n', '')
    )
    return problem_str

#复制代码
def copy_code(driver: webdriver.Chrome, AI_URL: str) -> None:
    try:
        divs = driver.find_elements(By.CSS_SELECTOR,  "div[class*='ml-[4px]']")
        target_divs = [div for div in divs if "复制" in div.text]
        if target_divs:
            last_target_div = target_divs[-1]
        driver.execute_script("arguments[0].scrollIntoView(true);",  last_target_div)
        last_target_div.click()
    except Exception as e:
        print(Fore.YELLOW + '复制时出错,尝试抢修' + Style.RESET_ALL)
        try:
            for i in range(100):
                driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/button/span/div").click()
        except Exception as e:
            try:
                divs = driver.find_elements(By.CSS_SELECTOR,  "div[class*='ml-[4px]']")
                target_divs = [div for div in divs if "复制" in div.text]
                if target_divs:
                    last_target_div = target_divs[-1]
                driver.execute_script("arguments[0].scrollIntoView(true);",  last_target_div)
                last_target_div.click()
            except Exception as e:
                print(Fore.RED + '抢修失败' + str(e) + Style.RESET_ALL)
                try:
                    driver.refresh()
                    driver.implicitly_wait(10)
                except Exception as e:
                    print(Fore.RED + '配置AI时出错:' + str(e) + Style.RESET_ALL)

def training_code() -> None:
    global driver, user_data, options
    driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']),  options = options)
    tids = input('请输入训练编号,用逗号隔开:')
    AI_URL = user_data['AI_URL']
    notes = input('备注:')  #代码后添加的东西

    #登录
    #OJ
    username = user_data['OJ']['username']
    password = user_data['OJ']['password']
    driver.get(f"{user_data['OJ']['URL']}/home")
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary el-button--medium is-round']").click()  #登录按钮
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='用户名']")
    find_boby.click()
    find_boby.send_keys(username)
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='密码']")
    find_boby.click()
    find_boby.send_keys(password)
    sleep(0.1)
    driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary']").click()
    sleep(1)
    #获取cookile
    driver.refresh()
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)['value'] # type: ignore
    #AI
    add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])
    for tid in tids.split(','):
        print('start,tid:', str(tid))
        #获取题目id
        driver.get(f"{user_data['OJ']['URL']}/training/" + str(tid))
        find_boby = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[3]").click()
        question_ID = []
        divs = driver.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' vxe-cell ') and contains(concat(' ', @class, ' '), ' c--tooltip ') and contains(@style, 'width: 148px;')]")
        #遍历
        for div in divs:
            labels = div.find_elements(By.XPATH,  ".//span[contains(concat(' ', @class, ' '), ' vxe-cell--label ')]")
            for label in labels:
                question_ID.append(label.text)

        driver.get(AI_URL)

        #开始刷题
        for i in question_ID:
            try:
                problem = get_problem_saying(i, notes)
            except Exception as e:
                print(Fore.RED + '获取问题时出错:' + str(e) + Style.RESET_ALL)
                continue
            sleep(0.5)
            find_boby = driver.find_element(By.XPATH, "//textarea[@placeholder='输入任何问题，Enter发送，Shift + Enter 换行']")
            find_boby.click()
            find_boby.send_keys(problem)
            sleep(1)
            find_boby.send_keys("\n")
            sleep(10)
            if not is_page_stable(driver):
                print(Fore.RED + "页面不稳定超时" + Style.RESET_ALL)
                driver.refresh
                continue
            #复制
            copy_code(driver = driver, AI_URL = AI_URL)
            sleep(0.5)
            code = pyperclip.paste()

            #提交代码
            headers = {
                'Content-Type': 'application/json', 
                'Cookie': 'JSESSIONID=' + jsessionid_cookie, 
                'User-Agent': 'Mozilla/6.0 (Windows NT 13.0; Win128; x128) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'
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
            response = requests.post(url = f"{user_data['OJ']['URL']}/api/submit-problem-judge", headers=headers, data=dumps(data))
            if response.status_code != 200:
                print(Fore.RED + '提交请求异常,status:' + str(response.status_code) + Style.RESET_ALL)
            now = datetime.now()
            formatted_time = now.strftime("%H:%M:%S")
            print(str(formatted_time) + ',pid:' + str(i))
    driver.quit()

def problem_code() -> None:
    global options, user_data
    driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']),  options = options)

    pids = input('请输入题目ID,用逗号隔开:')
    AI_URL = user_data['AI_URL']
    notes = input('备注:')  #代码后添加的东西

    #登录
    #OJ
    username = user_data['OJ']['username']
    password = user_data['OJ']['password']
    driver.get(f"{user_data['OJ']['URL']}/home")
    driver.maximize_window()
    driver.implicitly_wait(10)
    driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary el-button--medium is-round']").click()  #登录按钮
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='用户名']")
    find_boby.click()
    find_boby.send_keys(username)
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='密码']")
    find_boby.click()
    find_boby.send_keys(password)
    sleep(0.1)
    driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary']").click()
    sleep(1)

    #获取cookile
    driver.refresh()
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'))['value'] # type: ignore
    #AI
    add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])

    driver.get(AI_URL)

    for pid in pids.split(','):
        try:
            problem = get_problem_saying(pid, notes)
        except Exception as e:
            print(Fore.RED + '获取问题时出错:' + str(e) + Style.RESET_ALL)
            continue
        sleep(0.5)
        find_boby = driver.find_element(By.XPATH, "//textarea[@placeholder='输入任何问题，Enter发送，Shift + Enter 换行']")
        find_boby.click()
        find_boby.send_keys(problem)
        sleep(1)
        find_boby.send_keys("\n")
        sleep(10)
        if not is_page_stable(driver):
            print(Fore.RED + "页面不稳定超时" + Style.RESET_ALL)
            driver.refresh()
            continue
        #复制
        copy_code(driver = driver, AI_URL = AI_URL)
        sleep(0.5)
        code = pyperclip.paste()

        #提交代码
        headers = {
            'Content-Type': 'application/json', 
            'Cookie': 'JSESSIONID=' + jsessionid_cookie, 
            'User-Agent': 'Mozilla/6.0 (Windows NT 13.0; Win128; x128) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'
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
            print('提交请求异常,status:' + str(response.status_code))
            driver.quit()
            return
        now = datetime.now()
        formatted_time = now.strftime("%H:%M:%S")
        print(str(formatted_time) + ',pid:' + str(pid))
    driver.quit()

def get_user_data() -> None:
    global user_data_path, options, user_data
    user_data = {
        'OJ': {'URL': None, 'username': None, 'password': None}, 
        'AI_cookies': None, 
        'AI_URL': None, 
        'ChromeDriver_path': None
    }
    user_data['OJ']['URL'], user_data['OJ']['username'], user_data['OJ']['password'], user_data['AI_URL'], user_data['ChromeDriver_path'] = input('OJ网址:').rstrip('/'), input('OJ用户名:'), input('OJ密码:'), input('AI对话地址:'), input('ChromeDriver路径:')
    driver = webdriver.Chrome(service=Service(user_data['ChromeDriver_path']),  options = options)
    print('请自行操作登录AI，完成后回车', end='')
    driver.get('https://bot.n.cn/')
    input('')
    driver.refresh()
    cookies = driver.get_cookies()
    cookie_list = []
    for cookie in cookies:
        cookie_list.append(cookie)
    user_data['AI_cookies'] = cookie_list
    subprocess.run("type nul > " + user_data_path, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    with open(user_data_path,  'w') as file:
        dump(user_data, file)
    driver.quit()

if __name__ == '__main__':
    mode = None
    print(Fore.GREEN + '启动时间:' + str(int((time() - Start_time) * 100) / 100))
    while(mode != '4'):
        print(Fore.BLUE + '由一只蚊子WZ制作\nGitee仓库:https://gitee.com/wzokee/oj-auto-problem-solver-bot' + Back.RED + Fore.WHITE + '\n仅供参考学习!' + Style.RESET_ALL + Fore.GREEN + '\n\n请选择模式:' + Fore.CYAN + '\n1.配置信息\n2.刷训练题目\n3.刷个题\n4.退出\n' + Style.RESET_ALL)
        mode = input('请输入序号:')
        system('cls')
        if mode == '1':
            get_user_data()
            system('cls')
            print('配置成功')
            input('')
            is_user_data_read = True
        elif mode == '2':
            if is_user_data_read:
                training_code()
                print('刷题结束')
                input('')
                system('cls')
            else:
                print(Fore.YELLOW + '未导入配置,请先配置信息')
                input('')
                system('cls')
        elif mode == '3':
            if is_user_data_read:
                problem_code()
                print('做题结束')
                input('')
                system('cls')
            else:
                print(Fore.YELLOW + '未导入配置,请先配置信息')
                input('')
                system('cls')
