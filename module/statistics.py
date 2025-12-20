import requests
import json
from collections import Counter
import time
import threading
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# 缓存
in_memory_cache = {
    "timestamp": 0,
    "submissions": []
}
CACHE_TTL = 600  # 10分钟
cache_lock = threading.Lock()

def get_cache_info():
    with cache_lock:
        if time.time() - in_memory_cache["timestamp"] < CACHE_TTL:
            return in_memory_cache["submissions"]
    return None

def save_to_cache(submissions):
    with cache_lock:
        in_memory_cache["timestamp"] = time.time()
        in_memory_cache["submissions"] = submissions

def clear_cache():
    with cache_lock:
        in_memory_cache["timestamp"] = 0
        in_memory_cache["submissions"] = []

def get_oj_api_url():
    try:
        with open("user_data.json", "r") as f:
            data = json.load(f)
            return data.get("OJ").get("APIURL")
    except FileNotFoundError:
        return None

def get_all_submissions():
    # 检查缓存
    cached_submissions = get_cache_info()
    if cached_submissions is not None:
        return cached_submissions

    # 如果缓存不存在或已过期，重新请求数据
    oj_api_url = get_oj_api_url()
    if not oj_api_url:
        return {"error": "OJ API URL not configured."}

    submissions = []
    limit = 1000

    try:
        response = requests.get(
            f"{oj_api_url}/api/get-submission-list?onlyMine=false&currentPage=1&limit=1&completeProblemID=false"
        )
        response.raise_for_status()
        data = response.json().get("data", {})
        total_count = data.get("total", 0)
        if total_count == 0:
            save_to_cache([])
            return []
        
        total_pages = math.ceil(total_count / limit)
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch initial data: {e}"}
    except (ValueError, AttributeError):
        return {"error": "Failed to parse initial data."}

    def fetch_page(page):
        url = f"{oj_api_url}/api/get-submission-list?onlyMine=false&currentPage={page}&limit={limit}&completeProblemID=false"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json().get("data", {}).get("records", [])
        except (requests.exceptions.RequestException, ValueError):
            return []

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_page = {executor.submit(fetch_page, page): page for page in range(1, total_pages + 1)}
        for future in as_completed(future_to_page):
            records = future.result()
            if records:
                submissions.extend(records)
    
    # 保存到缓存
    save_to_cache(submissions)
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