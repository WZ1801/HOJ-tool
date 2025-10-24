"""
端口工具模块
提供获取随机可用端口的功能
"""
import socket
import random


def get_available_port(start_port=8000, end_port=65535, exclude_ports=None):
    """
    获取一个随机可用的端口
    
    Args:
        start_port: 起始端口范围（默认8000）
        end_port: 结束端口范围（默认65535）
        exclude_ports: 需要排除的端口列表
    
    Returns:
        int: 可用的端口号，如果找不到可用端口则返回None
    """
    if exclude_ports is None:
        exclude_ports = []
    
    # 常见的需要排除的端口
    common_excluded_ports = [1146, 3306, 5432, 6379, 8080, 3000, 5000, 8000]
    exclude_ports.extend(common_excluded_ports)
    exclude_ports = list(set(exclude_ports))  # 去重
    
    # 尝试随机端口
    max_attempts = 100  # 最大尝试次数
    attempts = 0
    
    while attempts < max_attempts:
        port = random.randint(start_port, end_port)
        
        # 检查是否在排除列表中
        if port in exclude_ports:
            attempts += 1
            continue
        
        # 检查端口是否可用
        if is_port_available(port):
            return port
        
        attempts += 1
    
    # 如果随机尝试失败，尝试顺序查找
    for port in range(start_port, end_port + 1):
        if port not in exclude_ports and is_port_available(port):
            return port
    
    return None


def is_port_available(port, host='127.0.0.1'):
    """
    检查指定端口是否可用
    
    Args:
        port: 要检查的端口号
        host: 要检查的主机地址（默认127.0.0.1）
    
    Returns:
        bool: 如果端口可用返回True，否则返回False
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            # 设置socket选项，允许地址重用
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # 尝试绑定到指定端口
            result = sock.bind((host, port))
            return True
    except (OSError, socket.error):
        # 端口被占用或其他错误
        return False


def get_default_port():
    """
    获取默认端口（1146），如果不可用则返回一个随机可用端口
    
    Returns:
        int: 可用的端口号
    """
    if is_port_available(1146):
        return 1146
    else:
        port = get_available_port()
        if port is None:
            return 8080
        return port


if __name__ == "__main__":
    # 测试函数
    print("测试端口工具函数...")
    
    # 测试获取可用端口
    available_port = get_available_port()
    print(f"获取到的随机可用端口: {available_port}")
    
    # 测试默认端口
    default_port = get_default_port()
    print(f"默认端口: {default_port}")
    
    # 测试端口可用性检查
    test_port = 8080
    is_available = is_port_available(test_port)
    print(f"端口 {test_port} 是否可用: {is_available}")