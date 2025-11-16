'''HOJ API'''
import requests
import urllib3
import threading
import time

class HOJ:
    def __init__(self, url):
        self.url = url
        self.user = None
        self.headers = {'User-Agent': 'HOJ-Client'}
        self.cookies = {}
        self.authorization = ''
        self.website_name = None
        
    def login(self, username, password):
        '''登录'''
        url = self.url + '/api/login'
        data = {'username': username, 'password': password}
        response = requests.post(url, json=data, headers=self.headers)
        if response.status_code == 200:
            self.cookies = response.cookies
            self.authorization = response.headers['Authorization']
            self.user = response.json()['data']['username']
            return True
        else:
            return False
        
    def get_website_name(self):
        '''获取网站名称'''
        if self.website_name:
            return self.website_name
        url = self.url + '/api/get-website-config'
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200:
            self.website_name = response.json()['data']['name']
            return self.website_name
        else:
            return None
        
    def get_tools(self):
        '''获取工具箱'''
        url = self.url + '/api/tools'
        response = requests.get(url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200:
            return response.json()['data']
        else:
            return None

    def get_rank(self, page: int = 1, limit: int = 10, mode = 'oi', get_all: bool = False):
        '''获取排名'''
        try:
            if not get_all:
                # 获取指定页面的数据
                url = self.url + '/api/get-rank-list?currentPage={}&limit={}&type={}'.format(page, limit, 1 if mode == 'oi' else 0)
                response = requests.get(url, headers=self.headers, cookies=self.cookies)
                if response.status_code == 200:
                    return response.json()['data']
                else:
                    return None
            else:
                # 获取所有数据
                all_records = []
                total_pages = 1
                current_page = 1
                
                # 首先获取第一页数据，获取总页数信息
                url = self.url + '/api/get-rank-list?currentPage=1&limit=200&type={}'.format(1 if mode == 'oi' else 0)
                response = requests.get(url, headers=self.headers, cookies=self.cookies)
                
                if response.status_code == 200:
                    first_page_data = response.json()['data']
                    total_pages = first_page_data.get('pages', 1)
                    all_records.extend(first_page_data.get('records', []))
                    
                    # 线程并发
                    if total_pages > 1:
                        threads = []
                        page_results = {}
                        lock = threading.Lock()
                        errors = []
                        
                        def fetch_page_with_retry(page_num, max_retries=3):
                            '''线程函数：获取指定页面的数据，支持重试机制'''
                            for attempt in range(max_retries):
                                try:
                                    url = self.url + '/api/get-rank-list?currentPage={}&limit=2000&type={}'.format(page_num, 1 if mode == 'oi' else 0)
                                    response = requests.get(url, headers=self.headers, cookies=self.cookies, timeout=30)
                                    
                                    if response.status_code == 200:
                                        page_data = response.json()['data']
                                        with lock:
                                            page_results[page_num] = page_data.get('records', [])
                                        break  # 成功则退出重试循环
                                    else:
                                        with lock:
                                            errors.append(f"第{page_num}页请求失败，状态码: {response.status_code}")
                                        if attempt == max_retries - 1:
                                            print(f"第{page_num}页数据获取失败，已重试{attempt + 1}次")
                                except requests.exceptions.Timeout:
                                    with lock:
                                        errors.append(f"第{page_num}页请求超时，重试 {attempt + 1}/{max_retries}")
                                    if attempt == max_retries - 1:
                                        print(f"第{page_num}页数据获取超时，已重试{attempt + 1}次")
                                except Exception as e:
                                    with lock:
                                        errors.append(f"获取第{page_num}页数据异常: {e}，重试 {attempt + 1}/{max_retries}")
                                time.sleep(1)  # 重试前等待1秒
                        
                        # 分批处理页面，每批10个线程
                        remaining_pages = list(range(2, total_pages + 1))
                        while remaining_pages:
                            # 取下一批页面（最多10个）
                            batch = remaining_pages[:10]
                            remaining_pages = remaining_pages[10:]
                            
                            # 为这批页面创建并启动线程
                            batch_threads = []
                            for page_num in batch:
                                thread = threading.Thread(target=fetch_page_with_retry, args=(page_num,))
                                batch_threads.append(thread)
                                thread.start()
                            
                            # 等待这批线程全部完成
                            for thread in batch_threads:
                                thread.join()
                        
                        # 输出错误信息（如果有）
                        if errors:
                            print(f"并发获取排名数据时出现以下错误:")
                            for error in errors:
                                print(f"  - {error}")
                        
                        # 按页码顺序合并数据
                        for page_num in range(2, total_pages + 1):
                            if page_num in page_results:
                                all_records.extend(page_results[page_num])
                    
                    # 返回合并后的数据
                    return {
                        'records': all_records,
                        'total': len(all_records),
                        'pages': total_pages,
                        'current': 1,
                        'size': len(all_records)
                    }
                else:
                    return None
                    
        except Exception as e:
            print(f"获取排名数据失败: {e}")
            return None
    
hitokoto = ''

def get_hitokoto() -> str:
    '''获取一言'''
    global hitokoto
    return hitokoto

def refresh_hitokoto():
    '''刷新一言'''
    global hitokoto
    urllib3.disable_warnings()
    while True:
        url = 'https://v1.hitokoto.cn/?c=i'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                hitokoto = response.json()['hitokoto']
        except Exception:
            pass
        time.sleep(60)

hitokoto_thread = threading.Thread(target=refresh_hitokoto)
hitokoto_thread.daemon = True
hitokoto_thread.start()