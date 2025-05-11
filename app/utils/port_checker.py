#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
端口检查工具
检查指定端口是否可用，如果被占用则检查是否为当前应用程序占用
"""

import socket
import os
import sys
import psutil
import logging
from pathlib import Path

logger = logging.getLogger("FastAgentApp")

def is_port_in_use(port):
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def is_port_used_by_python():
    """检查主Python进程是否已经在运行"""
    current_pid = os.getpid()
    current_process = psutil.Process(current_pid)
    current_python_path = current_process.exe()
    
    # 获取当前脚本的完整路径
    current_script_path = Path(sys.argv[0]).resolve()
    
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
        try:
            # 跳过当前进程
            if proc.pid == current_pid:
                continue
                
            # 检查是否是Python进程
            proc_info = proc.info
            if "python" in proc_info['name'].lower():
                # 检查命令行参数中是否包含main.py
                cmd = proc_info.get('cmdline', [])
                if cmd and any('main.py' in arg for arg in cmd if arg):
                    logger.info(f"发现已运行的FastAgent实例 (PID: {proc.pid})")
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return False

def check_port_availability(port, exit_on_conflict=True):
    """
    检查端口是否可用，如果不可用则根据情况退出或返回结果
    
    Args:
        port: 要检查的端口号
        exit_on_conflict: 如果端口被其他应用占用则退出程序
        
    Returns:
        bool: 如果不退出程序，返回端口是否可用
    """
    logger.info(f"检查端口 {port} 是否可用...")
    
    if is_port_in_use(port):
        # 检查是否是我们自己的应用占用了端口
        if is_port_used_by_python():
            logger.warning(f"FastAgent已经在端口 {port} 上运行")
            if exit_on_conflict:
                print(f"FastAgent已经在端口 {port} 上运行。如需运行多个实例，请指定不同的端口。")
                sys.exit(1)
            return False
        else:
            logger.error(f"端口 {port} 被其他应用程序占用")
            if exit_on_conflict:
                print(f"错误: 端口 {port} 被其他应用程序占用。请关闭占用该端口的应用或使用其他端口。")
                sys.exit(1)
            return False
    
    logger.info(f"端口 {port} 可用")
    return True 