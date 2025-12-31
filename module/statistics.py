import requests
import json
from collections import Counter
import time
import threading
import math
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 缓存
in_memory_cache = {
    "timestamp": 0,
    "submissions": []
}
CACHE_TTL = 600  # 10分钟
cache_lock = threading.Lock()

# 文件缓存路径
CACHE_FILE_PATH = "temp/statistics.json"

# 进度跟踪
statistics_progress = {
    "is_running": False,
    "progress": 0,
    "total_pages": 0,
    "current_page": 0,
    "error": None
}
progress_lock = threading.Lock()

def get_cache_info():
    """获取缓存数据，优先从内存缓存获取，如果没有则从文件缓存获取"""
    with cache_lock:
        # 首先检查内存缓存
        if time.time() - in_memory_cache["timestamp"] < CACHE_TTL:
            return in_memory_cache["submissions"]
        
        # 内存缓存过期，检查文件缓存
        if os.path.exists(CACHE_FILE_PATH):
            try:
                with open(CACHE_FILE_PATH, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                # 检查文件缓存是否过期
                if time.time() - cache_data.get("timestamp", 0) < CACHE_TTL:
                    # 文件缓存有效，加载到内存缓存
                    submissions = cache_data.get("submissions", [])
                    in_memory_cache["timestamp"] = cache_data.get("timestamp", 0)
                    in_memory_cache["submissions"] = submissions
                    return submissions
            except (json.JSONDecodeError, KeyError, IOError) as e:
                print(f"读取文件缓存失败: {e}")
                return None
    return None

def save_to_cache(submissions):
    """保存数据到内存缓存和文件缓存"""
    timestamp = time.time()
    
    with cache_lock:
        in_memory_cache["timestamp"] = timestamp
        in_memory_cache["submissions"] = submissions
    
    # 保存到文件缓存
    try:
        cache_dir = os.path.dirname(CACHE_FILE_PATH)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)
            
        cache_data = {
            "timestamp": timestamp,
            "submissions": submissions
        }
        
        with open(CACHE_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"保存文件缓存失败: {e}")

def clear_cache():
    """清空内存缓存和文件缓存"""
    with cache_lock:
        in_memory_cache["timestamp"] = 0
        in_memory_cache["submissions"] = []
    
    # 删除文件缓存
    try:
        if os.path.exists(CACHE_FILE_PATH):
            os.remove(CACHE_FILE_PATH)
    except IOError as e:
        print(f"删除文件缓存失败: {e}")

def get_oj_api_url():
    try:
        with open("user_data.json", "r") as f:
            data = json.load(f)
            return data.get("OJ").get("APIURL")
    except FileNotFoundError:
        return None

def create_session_with_retries():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_all_submissions(force_refresh=False):
    """获取所有提交数据，支持强制刷新"""
    # 如果不强制刷新，检查缓存
    if not force_refresh:
        cached_submissions = get_cache_info()
        if cached_submissions is not None:
            return cached_submissions

    # 清空进度状态
    with progress_lock:
        statistics_progress["is_running"] = True
        statistics_progress["progress"] = 0
        statistics_progress["total_pages"] = 0
        statistics_progress["current_page"] = 0
        statistics_progress["error"] = None

    # 如果缓存不存在或已过期，或强制刷新，重新请求数据
    oj_api_url = get_oj_api_url()
    if not oj_api_url:
        with progress_lock:
            statistics_progress["is_running"] = False
            statistics_progress["error"] = "OJ API URL not configured."
        return {"error": "OJ API URL not configured."}

    submissions = []
    limit = 500
    session = create_session_with_retries()

    try:
        # 更新进度：开始获取第一页
        with progress_lock:
            statistics_progress["progress"] = 5
            statistics_progress["current_page"] = 1
        
        response = session.get(
            f"{oj_api_url}/api/get-submission-list?onlyMine=false&currentPage=1&limit={limit}&completeProblemID=false"
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        total_count = data.get("total", 0)
        first_page_records = data.get("records", [])
        
        if total_count == 0:
            save_to_cache([])
            with progress_lock:
                statistics_progress["is_running"] = False
                statistics_progress["progress"] = 100
            return []
        
        submissions.extend(first_page_records)
        total_pages = math.ceil(total_count / limit)
        
        with progress_lock:
            statistics_progress["total_pages"] = total_pages
            statistics_progress["progress"] = 10
        
        if total_pages <= 1:
            save_to_cache(submissions)
            with progress_lock:
                statistics_progress["is_running"] = False
                statistics_progress["progress"] = 100
            return submissions
            
    except requests.exceptions.RequestException as e:
        with progress_lock:
            statistics_progress["is_running"] = False
            statistics_progress["error"] = f"Failed to fetch initial data: {e}"
        return {"error": f"Failed to fetch initial data: {e}"}
    except (ValueError, AttributeError):
        with progress_lock:
            statistics_progress["is_running"] = False
            statistics_progress["error"] = "Failed to parse initial data."
        return {"error": "Failed to parse initial data."}

    def fetch_page(page):
        """获取单页数据，带错误处理和重试"""
        url = f"{oj_api_url}/api/get-submission-list?onlyMine=false&currentPage={page}&limit={limit}&completeProblemID=false"
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            
            # 更新进度
            with progress_lock:
                statistics_progress["current_page"] = page
                progress_percentage = 10 + (page / total_pages) * 80
                statistics_progress["progress"] = min(progress_percentage, 90)
            
            return response.json().get("data", {}).get("records", [])
        except Exception as e:
            print(f"获取第{page}页失败: {e}")
            return []

    max_workers = min(16, total_pages - 1)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_page = {executor.submit(fetch_page, page): page for page in range(2, total_pages + 1)}
        
        results = [None] * (total_pages - 1)
        
        for future in as_completed(future_to_page):
            page = future_to_page[future]
            records = future.result()
            if records:
                results[page - 2] = records
        
        for records in results:
            if records:
                submissions.extend(records)
    
    # 保存到缓存
    save_to_cache(submissions)
    
    # 更新完成进度
    with progress_lock:
        statistics_progress["is_running"] = False
        statistics_progress["progress"] = 100
        statistics_progress["current_page"] = total_pages
    
    return submissions

def calculate_statistics(submissions, username=None):
    if not submissions:
        return {}

    total_submissions = len(submissions)
    
    status_map = {
        -3: "Presentation Error",
        -2: "Compile Error",
        -1: "Wrong Answer",
        0: "Accepted",
        1: "Time Limit Exceeded",
        2: "Memory Limit Exceeded",
        3: "Runtime Error",
        4: "System Error",
        5: "Pending",
        6: "Compiling",
        7: "Judging",
        8: "Partial Accepted",
        10: "Submitted Failed",
    }
    all_possible_statuses = sorted(list(status_map.values()))

    user_counts = Counter(sub["username"] for sub in submissions)
    user_ranking_sorted = sorted(user_counts.items(), key=lambda item: item[1], reverse=True)

    status_counts = Counter(status_map.get(sub["status"], "Unknown") for sub in submissions)
    status_ranking = {status: count / total_submissions * 100 for status, count in status_counts.items()}

    language_counts = Counter(sub["language"] for sub in submissions if sub.get("language"))
    language_distribution = {lang: count / total_submissions * 100 for lang, count in language_counts.items()}

    problem_counts = Counter(sub["displayPid"] for sub in submissions if sub.get("displayPid"))
    top_problems = problem_counts.most_common(20)

    hourly_counts = Counter(datetime.fromisoformat(sub["submitTime"].replace("Z", "+00:00")).hour for sub in submissions)
    submission_by_hour = {
        "hours": [f"{h:02d}:00" for h in range(24)],
        "counts": [hourly_counts.get(h, 0) for h in range(24)]
    }

    top_users = user_ranking_sorted[:20]
    user_labels = [user for user, count in top_users]
    
    datasets = {status: [] for status in all_possible_statuses}
    for user, count in top_users:
        user_submissions = [s for s in submissions if s['username'] == user]
        user_status_counts = Counter(status_map.get(s["status"], "Unknown") for s in user_submissions)
        for status in all_possible_statuses:
            datasets[status].append((user_status_counts.get(status, 0) / total_submissions) * 100)
    
    final_datasets = [{"label": status, "data": data} for status, data in datasets.items() if any(d > 0 for d in data)]

    result = {
        "status_ranking": sorted(status_ranking.items(), key=lambda item: item[1], reverse=True),
        "top_users_stacked_data": {
            "users": user_labels,
            "datasets": final_datasets
        },
        "submission_by_hour": submission_by_hour,
        "top_problems": [{"problem": pid, "count": count} for pid, count in top_problems],
        "language_distribution": sorted(language_distribution.items(), key=lambda item: item[1], reverse=True)
    }

    if not language_distribution:
        result["language_distribution"] = []

    if username:
        user_submissions = [sub for sub in submissions if sub["username"] == username]
        if user_submissions:
            user_total_submissions = len(user_submissions)
            user_status_counts = Counter(status_map.get(sub["status"], "Unknown") for sub in user_submissions)
            user_status_percentage = {status: count / user_total_submissions * 100 for status, count in user_status_counts.items()}
            
            user_language_counts = Counter(sub["language"] for sub in user_submissions if sub.get("language"))
            user_language_percentage = {lang: count / user_total_submissions * 100 for lang, count in user_language_counts.items()}
            
            user_hourly_counts = Counter(datetime.fromisoformat(sub["submitTime"].replace("Z", "+00:00")).hour for sub in user_submissions)
            user_submission_by_hour = {
                "hours": [f"{h:02d}:00" for h in range(24)],
                "counts": [user_hourly_counts.get(h, 0) for h in range(24)]
            }

            result["user_specific"] = {
                "username": username,
                "submission_count": user_total_submissions,
                "status_percentage": sorted(user_status_percentage.items(), key=lambda item: item[1], reverse=True),
                "submission_by_hour": user_submission_by_hour,
                "language_percentage": sorted(user_language_percentage.items(), key=lambda item: item[1], reverse=True)
            }

    return result

def get_statistics(username=None):
    submissions = get_all_submissions()
    if isinstance(submissions, dict) and "error" in submissions:
        return submissions
    return calculate_statistics(submissions, username)
