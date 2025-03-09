#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
智能聊天预测程序 - 主程序入口

本程序通过深度整合微信客户端数据与DeepSeek大模型，
实现高效、精准的聊天预测与回复辅助功能。
"""

import sys
import os
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication

# 导入自定义模块
from src.ui.main_window import MainWindow
from src.utils.config import Config

# 加载环境变量
load_dotenv()

def main():
    print("运行程序前，请确保已经配置好DeepSeek的API_KEY")
    """程序主入口"""
    # 初始化配置
    config = Config()
    
    # 创建QT应用
    app = QApplication(sys.argv)
    app.setApplicationName("智能聊天预测程序")
    
    # 创建并显示主窗口
    window = MainWindow(config)
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()