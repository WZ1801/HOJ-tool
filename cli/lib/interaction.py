import msvcrt
import os
from colorama import init, Fore, Back, Style

def get_key():
    """获取键盘输入"""
    if os.name == 'nt':  # Windows系统
        key = msvcrt.getch()
        if key == b'\xe0':  # 扩展键
            key = msvcrt.getch()
            return key
        elif key == b'\r':  # 回车键
            return 'enter'
        elif key == b'\x1b':  # ESC键
            return 'esc'
        else:
            return key

def get_case(cases: list[any], title = None) -> any:
    """获取用户选择"""
    if title:
        print(f'{Fore.YELLOW}{title}{Style.RESET_ALL}')
    index = 1
    case_map = {}
    for case in cases:
        if case == 'exit':
            print(f'{Fore.RED}{0}{Fore.CYAN}. {Style.RESET_ALL}{'退出'}')
            case_map.update({0: 'exit'})
            continue
        print(f'{Fore.CYAN}{index}{Fore.YELLOW}. {Style.RESET_ALL}{case}')
        case_map.update({index: case})
        index += 1
    while True:
        key = get_key()
        
        try:
            key = int(key)
        except Exception:
            continue
        
        if key in case_map:
            return case_map[key]
        
def show_message(message: str, mode = 'info'):
    """显示消息"""
    if mode == 'info':
        print(f'{Fore.GREEN}{message}{Style.RESET_ALL}')
    elif mode == 'error':
        print(f'{Fore.RED}{message}{Style.RESET_ALL}')
    elif mode == 'warning':
        print(f'{Fore.YELLOW}{message}{Style.RESET_ALL}')

def show_hello(oj_name: str, username: str, hitokoto: str):
    print(f'{Fore.CYAN}欢迎使用 {oj_name} {username}!{Style.RESET_ALL}\n{Fore.YELLOW}{hitokoto}{Style.RESET_ALL}')
    
def show_table(items: dict, mode: str = 'table', line_count: int = 10):
    '''显示表格'''
    os.system('cls')
    
    # 获取数据
    header = items.get('header', '')
    columns = items.get('column', [])
    data = items.get('data', [])
    current_page = items.get('current_page', 1)
    total_pages = items.get('total_pages', 1)
    
    # 显示表头
    if header:
        print(f'{Fore.CYAN}{header}{Style.RESET_ALL}')
        print('-' * 50)
    
    # 计算列宽
    col_widths = []
    if columns:
        for i, col in enumerate(columns):
            max_width = len(col)
            for row in data:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max(max_width + 2, 20))
    else:
        if data:
            num_cols = len(data[0]) if data else 3
            col_widths = [15] * num_cols
    
    # 显示列名
    if columns:
        header_str = ''.join(f'{col:<{width}}' for col, width in zip(columns, col_widths))
        if mode == 'rank':
            print(f'{Fore.YELLOW}{header_str}{Style.RESET_ALL}')
        else:
            print(f'{Fore.GREEN}{header_str}{Style.RESET_ALL}')
    
    # 计算当前页数据
    start_idx = (current_page - 1) * line_count
    end_idx = min(start_idx + line_count, len(data))
    current_data = data[start_idx:end_idx]
    
    # 更新总页数
    total_pages = max(1, (len(data) + line_count - 1) // line_count)
    
    # 显示数据行
    for i, row in enumerate(current_data):
        if mode == 'rank':  # rank
            # 前三名
            if start_idx + i == 0:
                row_str = ''.join(f'{Fore.RED}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
            elif start_idx + i == 1:
                row_str = ''.join(f'{Fore.YELLOW}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
            elif start_idx + i == 2:
                row_str = ''.join(f'{Fore.GREEN}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
            else:
                # 交替颜色
                if i % 2 == 0:
                    row_str = ''.join(f'{Style.DIM}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
                else:
                    row_str = ''.join(f'{str(item):<{width}}' for item, width in zip(row, col_widths))
        else:  # table
            if i == 0:  # 第一行特殊颜色
                row_str = ''.join(f'{Fore.YELLOW}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
            else:
                # 交替颜色
                if i % 2 == 0:
                    row_str = ''.join(f'{Style.DIM}{str(item):<{width}}{Style.RESET_ALL}' for item, width in zip(row, col_widths))
                else:
                    row_str = ''.join(f'{str(item):<{width}}' for item, width in zip(row, col_widths))
        
        print(row_str)
    
    # 分页信息
    print('\n' + '-' * 50)
    _show_pagination(current_page, total_pages)
    
    # 等待用户输入控制分页
    while True:
        key = get_key()
        if key == b'K':  # 左箭头
            if current_page > 1:
                items['current_page'] = current_page - 1
                show_table(items, mode, line_count)
                return
        elif key == b'M':  # 右箭头
            if current_page < total_pages:
                items['current_page'] = current_page + 1
                show_table(items, mode, line_count)
                return
        elif key == 'esc':  # ESC键退出
            return

def _show_pagination(current_page: int, total_pages: int):
    '''显示分页导航'''
    page_str = ''
    
    # 显示页码导航
    if total_pages <= 7:
        # 如果总页数较少，显示所有页码
        for i in range(1, total_pages + 1):
            if i == current_page:
                page_str += f'{Fore.YELLOW}{i}{Style.RESET_ALL} '
            else:
                page_str += f'{i} '
    else:
        # 显示导航
        if current_page <= 4:
            # 当前页在前几页
            for i in range(1, min(6, total_pages) + 1):
                if i == current_page:
                    page_str += f'{Fore.YELLOW}{i}{Style.RESET_ALL} '
                else:
                    page_str += f'{i} '
            if total_pages > 6:
                page_str += f'... {total_pages}'
        elif current_page >= total_pages - 3:
            # 当前页在后几页
            page_str += f'1 ... '
            for i in range(max(1, total_pages - 4), total_pages + 1):
                if i == current_page:
                    page_str += f'{Fore.YELLOW}{i}{Style.RESET_ALL} '
                else:
                    page_str += f'{i} '
        else:
            # 当前页在中间
            page_str += f'1 ... '
            for i in range(current_page - 1, current_page + 2):
                if i == current_page:
                    page_str += f'{Fore.YELLOW}{i}{Style.RESET_ALL} '
                else:
                    page_str += f'{i} '
            page_str += f'... {total_pages}'
    
    print(f'页码: {page_str}')
    print('使用 ← → 键翻页，ESC 键退出')
    

def show_rank(rank: dict, mode: str = 'oi'):
    '''显示排名'''
    if not rank or 'records' not in rank:
        show_message('没有排名数据', 'error')
        return
    
    # 提取排名数据
    records = rank['records']
    total_pages = rank.get('pages', 1)
    current_page = rank.get('current', 1)
    
    # 准备表格
    table_data = []
    for i, record in enumerate(records):
        username = record.get('username', '')
        score = record.get('score', 0)
        ac = record.get('ac', 0)
        total = record.get('total', 0)
        
        if mode == 'oi':
            # OI榜：显示用户、分数、AC/总数
            table_data.append([
                f'{i + 1}. {username}',
                f'{score}',
                f'{ac}/{total}'
            ])
        elif mode == 'acm':
            # ACM榜：显示用户、AC/总数、通过率
            if total > 0:
                pass_rate = round((ac / total) * 100, 2)
            else:
                pass_rate = 0.00
            pass_rate_str = f'{pass_rate}%'
            table_data.append([
                f'{i + 1}. {username}',
                f'{ac}/{total}',
                pass_rate_str
            ])
        else:
            # 默认模式（兼容旧代码）
            table_data.append([
                f'{i + 1}. {username}',
                f'{score}',
                f'{ac}/{total}'
            ])
    
    # 创建表格项
    if mode == 'oi':
        columns = ['用户', '分数', 'AC/总数']
    elif mode == 'acm':
        columns = ['用户', 'AC/总数', '通过率']
    else:
        columns = ['用户', '分数', 'AC/总数']
    
    table_items = {
        'header': f'排名 ({mode.upper()}模式)',
        'column': columns,
        'data': table_data,
        'current_page': current_page,
        'total_pages': total_pages
    }
    
    # 调用show_table显示
    show_table(table_items, mode='rank', line_count=10)

init()