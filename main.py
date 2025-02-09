from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from os import system
from json import dump, load, dumps
from datetime import datetime
from time import time, sleep
from sys import exit
import requests, pyperclip, hashlib, re

options = Options()
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(service=Service(r'F:\\编程\\Python\\爬虫\\cd\\chromedriver.exe'),  options = options)

def training_code():
    training_num = input('training:')

    with open('C:\\OJ\\user_data.json',  'r') as file:
        user_data = load(file)

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
    #OJ
    username = user_data['OJ']['username']
    password = user_data['OJ']['password']
    driver.get("http://example.oj/home")
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
    sleep(0.1)
    find_boby = driver.find_element(By.XPATH,  "//button[@class='el-button el-button--primary']")
    find_boby.click()
    sleep(1)
    #获取cokkile
    driver.refresh()
    cookies = driver.get_cookies()
    jsessionid_cookie = next((cookie for cookie in cookies if cookie['name'] == 'JSESSIONID'), None)['value']
    #AI
    add_driver_cookie(driver, 'https://bot.n.cn/', user_data['AI_cookies'])
    
    #获取题目id
    driver.get("http://example.oj/training/" + str(training_num))
    find_boby = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div[3]")
    find_boby.click()
    question_ID = []
    divs = driver.find_elements(By.XPATH, "//div[contains(concat(' ', @class, ' '), ' vxe-cell ') and contains(concat(' ', @class, ' '), ' c--tooltip ') and contains(@style, 'width: 148px;')]")
    #遍历打印
    for div in divs:
        labels = div.find_elements(By.XPATH,  ".//span[contains(concat(' ', @class, ' '), ' vxe-cell--label ')]")
        for label in labels:
            # print(label.text)
            question_ID.append(label.text)

    '''配置AI'''
    driver.get(input('AI对话地址:'))
    find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[1]/div/div[2]/div[1]/div[2]/section/div[1]/div/div/div[1]/span")
    find_boby.click()
    sleep(0.1)
    find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[1]/div[3]/div[4]")
    find_boby.click()
    sleep(0.1)
    find_boby = driver.find_element(By.XPATH,  "/html/body/div[1]/div/div[2]/div/div[2]/div/div[2]/div/div/div[1]/div/div/div/div[2]/div/div/div/div[3]/div[4]")
    find_boby.click()
    sleep(1)

    #开始刷题
    for i in question_ID:
        problem = requests.get(url = 'http://example.oj/api/get-problem-detail?problemId=' + i, headers = {'User-Agent': 'Mozilla/7.0 (Windows NT 13.0; Win256; x256) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/514.0.0.0 Safari/987.36'})
        problem = problem.json()
        problem = problem['data']['problem']
        problem = str('请编写可运行完整程序:' + problem['description'] + '输入:' + problem['input'] + '输出:' + problem['output']).replace("\n",  "").replace("\r", "").replace("<code>", "").replace("</code>", "").replace("<input>", "").replace("</input>", "").replace("<output>", "").replace("</output>", "").replace("\\", "") + str(example_conversion_format(problem['examples']) + '。'  + '帮我编写c++程序，不要有其他赘述，并直接输出程序,代码中不要有注释，可开头直接声明std命名空间。')
        # driver.refresh()
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
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);",  last_target_div)
                last_target_div.click()
            except Exception as e:
                print('复制时出错:' + str(e))
                driver.quit()
                exit()
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
        # print(dumps(headers) + '\n' + dumps(data))
        response = requests.post(url='http://example.oj/api/submit-problem-judge', headers=headers, data=dumps(data))
        if response.status_code != 200:
            print('提交请求异常,status:' + str(response.status_code))
            driver.quit()
            exit()
        now = datetime.now()
        formatted_time = now.strftime("%H:%M:%S")
        print(str(formatted_time) + ',' + str(i))

def get_user_data():
    user_data = {
        'OJ': {'username': None, 'password': None}, 
        'AI_cookies': None
    }
    user_data['OJ']['username'], user_data['OJ']['password'] = input('OJ用户名:'), input('OJ密码:')
    print('请自行操作登录AI，完成后回车', end='')
    driver.get('https://bot.n.cn/')
    input('')
    driver.refresh()
    cookies = driver.get_cookies()
    cookie_list = []
    for cookie in cookies:
        cookie_list.append(cookie)
    user_data['AI_cookies'] = cookie_list
    with open('C:\\OJ\\user_data.json',  'w') as file:
        dump(user_data, file)
if __name__ == '__main__':
    print('请选择模式:\n1.写入配置\n2.刷训练题目\n')
    mode = input('请输入序号:')
    system('cls')
    if mode == '1':
        get_user_data()
        system('cls')
        print('配置成功')
        input('')
    elif mode == '2':
        training_code()
        system('cls')
        print('刷题结束')
        input('')