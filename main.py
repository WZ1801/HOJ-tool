from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from pyautogui import scroll
from datetime import datetime
from time import time, sleep
from sys import exit
import requests, pyperclip, win32com.client, hashlib, re

options = Options()
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(service=Service(r'F:\\编程\\Python\\爬虫\\cd\\chromedriver.exe'),  options = options)
shell = win32com.client.Dispatch("WScript.Shell")

#示例转换格式
def example_conversion_format(examples):
    """
    示例转换格式 
 
    :param examples: 原始示例内容 
    :return: 返回转换后的示例格式 
    """
    pattern = r"<input>(.*?)</input><output>(.*?)</output>"
    matches = re.findall(pattern,  examples, re.DOTALL)
    formatted_examples = []
    for match in matches:
        input_part = match[0].strip().replace("\n", " ")
        output_part = match[1].strip().replace("\n", " ")
        formatted_example = f"输入{input_part}，输出{output_part}"
        formatted_examples.append(formatted_example)  
    
    out_example = '示例：'
    for example in formatted_examples:
        out_example += example + '；'
    return out_example 

#等待页面上没有任何元素变化
def is_page_stable(driver, timeout=60, interval=1.5):
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
        print("页面不稳定超时")
        return False
def _get_page_hash(driver):
    """
    捕获页面的DOM快照，并生成一个哈希值
    """
    # 获取页面源代码
    page_source = driver.page_source
    # 使用哈希函数生成页面状态的唯一标识
    return hashlib.md5(page_source.encode()).hexdigest()

#添加cookie
def add_driver_cookie(driver, website, cookies):
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
        print(f"An error occurred: {e}")

#登录
def web_login(driver):
    #OJ
    username = '24CSP118'
    password = '1801a1b2c3'
    driver.get("http://82.156.246.133/home")
    driver.maximize_window()
    driver.implicitly_wait(10)
    find_boby = driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary el-button--medium is-round']")
    find_boby.click()
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='用户名']")
    find_boby.click()
    find_boby.send_keys(username)
    find_boby = driver.find_element(By.XPATH,  "//input[@placeholder='密码']")
    find_boby.click()
    find_boby.send_keys(password)
    find_boby = driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary']")
    find_boby.click()
    #AI
    add_driver_cookie(driver, 'https://bot.n.cn/', [
        {'domain':'.n.cn', 'name':'Q', 'value':'u%3D360H3463311031%26n%3D%26le%3D%26m%3DZGH3WGWOWGWOWGWOWGWOWGWOAwL0%26qid%3D3463311031%26im%3D1_t01923d359dad425928%26src%3Dpcw_aizhushou%26t%3D1'},
        {'domain':'.n.cn', 'name':'T', 'value':'s%3Ded0a4c50ab6004e9a8745dd3a70f3993%26t%3D1736340256%26lm%3D%26lf%3D2%26sk%3D304716dace5cbd6249370810985845ca%26mt%3D1736340256%26rc%3D%26v%3D2.0%26a%3D1'},
        {'domain':'.bot.n.cn', 'name':'sdt', 'value':'deff475b-cb9a-4ef3-af22-2968d7dd7ec5'},
        {'domain':'.n.cn', 'name':'__NS_Q', 'value':'u%3D360H3463311031%26n%3D%26le%3D%26m%3DZGH3WGWOWGWOWGWOWGWOWGWOAwL0%26qid%3D3463311031%26im%3D1_t01923d359dad425928%26src%3Dpcw_aizhushou%26t%3D1'},
        {'domain':'.bot.n.cn', 'name':'Auth-Token', 'value':'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJtaWQiOiIyNTE3MDQ3ODQ1Njc5MDAwMjczMDg0MTY1MDAxNzM0MCIsInFpZCI6IiIsImRldGFpbCI6IjQwMSIsImV4cCI6MTczNjk0NTAyOX0.vUFupG9R9TW_OtotJlbX73XVyHivCiA3ZnZhctiTMEI'},
        {'domain':'.n.cn', 'name':'__NS_T', 'value':'s%3Ded0a4c50ab6004e9a8745dd3a70f3993%26t%3D1736340256%26lm%3D%26lf%3D2%26sk%3D304716dace5cbd6249370810985845ca%26mt%3D1736340256%26rc%3D%26v%3D2.0%26a%3D1'},
        {'domain':'.n.cn', 'name':'__guid', 'value':'25170478.1927469175656186400.1736340203443.209'},
        {'domain':'bot.n.cn', 'name':'__DC_gid', 'value':'25170478.224657746.1734078531409.1736340833327.33'},
        {'domain':'bot.n.cn', 'name':'__DC_monitor_count', 'value':'2'},
        {'domain':'bot.n.cn', 'name':'__DC_sid', 'value':'25170478.2164768734284768500.1736340202708.525'},
        {'domain':'bot.n.cn', 'name':'__quc_silent__', 'value':'1'},
        {'domain':'bot.n.cn', 'name':'test_cookie_enable', 'value':''}
    ])
  
web_login(driver=driver)
#获取题目id
driver.get("http://82.156.246.133/training/" + str(input('training:')))
find_boby = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[3]")
find_boby.click()
question_ID = []
divs = driver.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' vxe-cell ') and contains(concat(' ', @class, ' '), ' c--tooltip ') and contains(@style, 'width: 148px;')]")
#遍历打印
for div in divs:
    labels = div.find_elements(By.XPATH,  ".//span[contains(concat(' ', @class, ' '), ' vxe-cell--label ')]")
    for label in labels:
        print(label.text)
        question_ID.append(label.text)

'''配置AI'''
driver.execute_script("window.open('https://bot.n.cn/chat/6559aaaa5a5e4fa99a62de362d016cea');")   # 在新标签页中打开AI
window_handles = driver.window_handles
driver.switch_to.window(window_handles[1])
find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[2]/section/div[1]/div/div/div[1]/span")
find_boby.click()
sleep(0.1)
find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[3]/div[4]")
find_boby.click()
sleep(0.1)
find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[3]/div[4]")
find_boby.click()
sleep(1)
driver.switch_to.window(window_handles[0])

#开始刷题
for i in question_ID:
    driver.get("http://82.156.246.133/problem/" + i)
    problem = requests.get(url = 'http://82.156.246.133/api/get-problem-detail?problemId=' + i, headers = {'User-Agent': 'Mozilla/7.0 (Windows NT 13.0; Win256; x256) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/514.0.0.0 Safari/987.36'})
    problem = problem.json()
    problem = problem['data']['problem']
    problem = str('请编写可运行完整程序:' + problem['description'] + '输入:' + problem['input'] + '输出:' + problem['output']).replace("\n",  "").replace("\r", "").replace("<code>", "").replace("</code>", "").replace("<input>", "").replace("</input>", "").replace("<output>", "").replace("</output>", "").replace("\\", "") + str(example_conversion_format(problem['examples']) + '。'  + '帮我编写c++程序，不要有其他赘述，并直接输出程序,代码中不要有注释，可开头直接声明std命名空间。')
    driver.switch_to.window(window_handles[1])
    sleep(0.5)
    find_boby = driver.find_element(By.XPATH, "//textarea[@placeholder='输入任何问题，Enter发送，Shift + Enter 换行']")
    find_boby.click()
    find_boby.send_keys(problem)
    sleep(1)
    find_boby.send_keys("\n")
    sleep(7)
    if not is_page_stable(driver):
        driver.quit()
        exit()
    #复制
    sleep(1)
    divs = driver.find_elements(By.CSS_SELECTOR,  "div[class*='ml-[4px]']")
    target_divs = [div for div in divs if "复制" in div.text]
    if target_divs:
        last_target_div = target_divs[-1]
        for _ in range(10):
            try:
                last_target_div.click()
            except Exception:
                driver.execute_script("arguments[0].scrollIntoView(true);",  last_target_div)
            finally:
                break
    sleep(0.2)
    text = pyperclip.paste()
    driver.switch_to.window(window_handles[0])
    file = open("F:\englishfile\problem.cpp",  'w')
    file.write(text)
    file.close()
    find_body = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div[2]/div/span[1]/button')
    find_body.click()
    sleep(1.7)
    shell.Sendkeys(r"F:\englishfile\problem.cpp" + '\n')
    sleep(1)
    find_body = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[1]/div/div[3]/div/div/div[2]/div/div[2]/button")
    find_body.click()
    sleep(0.5)
    now = datetime.now()
    formatted_time = now.strftime("%H:%M:%S")
    print(str(formatted_time) + ', ' + str(i))

sleep(10)
