#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
微信数据捕获模块

负责实时捕获微信桌面端当前激活窗口的聊天内容，
并提供对话上下文管理功能。
"""

import time
import win32gui
import win32con
import win32clipboard
import pyperclip
from PIL import ImageGrab
from collections import deque

class WeChatCapture:
    """微信聊天内容捕获类"""
    
    def __init__(self, config):
        """初始化微信捕获器"""
        self.config = config
        # 使用双端队列存储聊天历史
        self.chat_history = deque(maxlen=config.max_history_length)
        # 上次捕获的内容，用于去重
        self.last_captured = ""
        # 微信窗口句柄
        self.wechat_hwnd = None
    
    def find_wechat_window(self):
        """查找微信窗口"""
        def callback(hwnd, extra):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                window_text = win32gui.GetWindowText(hwnd)
                if "微信" in window_text:
                    extra.append(hwnd)
            return True
        
        hwnd_list = []
        win32gui.EnumWindows(callback, hwnd_list)
        
        if hwnd_list:
            # 找到微信主窗口
            self.wechat_hwnd = hwnd_list[0]
            return True
        return False
    
    def capture_chat_content(self):
        """捕获当前聊天内容"""
        if not self.wechat_hwnd:
            if not self.find_wechat_window():
                # 如果找不到微信窗口但有历史记录，返回现有历史
                if self.chat_history:
                    return list(self.chat_history)
                return None
        
        # 保存当前活动窗口句柄，以便操作后恢复
        current_hwnd = win32gui.GetForegroundWindow()
        
        try:
            # 激活微信窗口
            win32gui.SetForegroundWindow(self.wechat_hwnd)
            time.sleep(0.1)  # 等待窗口激活
            
            # 模拟Ctrl+A全选
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYDOWN, ord('A'), 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYUP, ord('A'), 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
            
            # 模拟Ctrl+C复制
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYDOWN, ord('C'), 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYUP, ord('C'), 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
            
            time.sleep(0.1)  # 等待复制完成
            
            # 获取剪贴板内容
            win32clipboard.OpenClipboard()
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32con.CF_TEXT):
                    chat_content = win32clipboard.GetClipboardData(win32con.CF_TEXT)
                    chat_content = chat_content.decode('gbk')
                else:
                    chat_content = pyperclip.paste()
            finally:
                win32clipboard.CloseClipboard()
            
            # 按ESC取消选择
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYDOWN, win32con.VK_ESCAPE, 0)
            win32gui.SendMessage(self.wechat_hwnd, win32con.WM_KEYUP, win32con.VK_ESCAPE, 0)
            
            # 将焦点返回给原来的窗口
            try:
                if current_hwnd and current_hwnd != self.wechat_hwnd:
                    win32gui.SetForegroundWindow(current_hwnd)
            except Exception:
                pass  # 忽略恢复焦点时的错误
            
            # 检查内容是否有变化
            if chat_content == self.last_captured:
                # 即使内容没有变化，也返回当前的聊天历史
                if self.chat_history:
                    return list(self.chat_history)
                return None
            
            self.last_captured = chat_content
            processed_content = self.process_chat_content(chat_content)
            
            # 如果处理后没有内容但有历史记录，返回现有历史
            if not processed_content and self.chat_history:
                return list(self.chat_history)
                
            return processed_content
            
        except Exception as e:
            if self.config.debug_mode:
                print(f"捕获聊天内容失败: {e}")
            # 发生异常时，如果有历史记录，返回现有历史
            if self.chat_history:
                return list(self.chat_history)
            return None
    
    def process_chat_content(self, content):
        """处理捕获的聊天内容"""
        if not content or len(content.strip()) == 0:
            return None
        print("捕获到的聊天内容："+content)
        
        # 直接将完整内容添加到聊天历史中
        if content not in self.chat_history:
            self.chat_history.append(content)
        
        return list(self.chat_history)
    
    def get_chat_history(self):
        """获取当前聊天历史"""
        return list(self.chat_history)
    
    def clear_history(self):
        """清空聊天历史"""
        self.chat_history.clear()
        self.last_captured = ""