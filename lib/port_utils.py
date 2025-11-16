"""
端口
"""
import socket
import random


def get_available_port(start_port=8000, end_port=65535, exclude_ports=None):
    """
    获取一个随机可用的端口
    """
    if exclude_ports is None:
        exclude_ports = []
    
    common_excluded_ports = [1146, 3306, 5432, 6379, 8080, 3000, 5000, 8000]
    exclude_ports.extend(common_excluded_ports)
    exclude_ports = list(set(exclude_ports))
    
    max_attempts = 100
    attempts = 0
    
    while attempts < max_attempts:
        port = random.randint(start_port, end_port)
        
        if port in exclude_ports:
            attempts += 1
            continue
        
        if is_port_available(port):
            return port
        
        attempts += 1
    
    for port in range(start_port, end_port + 1):
        if port not in exclude_ports and is_port_available(port):
            return port
    
    return None


def is_port_available(port, host='127.0.0.1'):
    """
    检查指定端口是否可用
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            result = sock.bind((host, port))
            return True
    except (OSError, socket.error):
        return False


def get_port():
    """
    获取端口
    """
    if is_port_available(1146):
        return 1146
    else:
        port = get_available_port()
        if port is None:
            return 8080
        return port