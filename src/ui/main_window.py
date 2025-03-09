#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
主窗口模块

实现程序的主要界面，包括预测结果展示、按钮控件等UI元素。
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, 
                             QComboBox, QLabel, QHBoxLayout, QTextEdit, QListWidget, 
                             QListWidgetItem, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
                             QTextBrowser)
from PyQt5.QtCore import Qt, QPoint, QMetaObject, Q_ARG, Q_RETURN_ARG
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QColor, QFont, QPalette, QIcon
import threading

# 导入自定义模块
from src.data.wechat_capture import WeChatCapture
from src.api.deepseek_api import DeepSeekAPI

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self, config):
        super().__init__(None, Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.config = config
        
        # 初始化微信捕获器和API客户端
        self.wechat_capture = WeChatCapture(config)
        self.api_client = DeepSeekAPI(config)
        
        # 窗口拖动相关变量
        self.draggable = True
        self.dragging = False
        self.drag_position = QPoint()
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        # 设置窗口基本属性
        self.setWindowTitle("智能聊天预测程序")
        self.setGeometry(100, 100, 300, 400)  # 减小窗口尺寸
        
        # 设置窗口透明
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建一个带圆角和阴影的容器
        container = QFrame()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: rgba(255, 255, 255, 220);
                border-radius: 15px;
                border: 1px solid rgba(200, 200, 200, 150);
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        container.setGraphicsEffect(shadow)
        
        # 容器的布局
        container_layout = QVBoxLayout(container)
        
        # 标题栏（用于拖动窗口）
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setStyleSheet("""
            #titleBar {
                background-color: rgba(70, 130, 180, 220);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                padding: 5px;
            }
        """)
        title_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        title_bar.setFixedHeight(30)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 10, 0)
        
        # 标题
        title_label = QLabel("智能聊天助手")
        title_label.setStyleSheet("color: white; font-weight: bold;")
        title_layout.addWidget(title_label)
        
        # 最小化和关闭按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        min_btn = QPushButton("_")
        min_btn.setFixedSize(16, 16)
        min_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 150);
                border-radius: 8px;
                color: #333;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 200);
            }
        """)
        min_btn.clicked.connect(self.showMinimized)
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(16, 16)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 100, 100, 150);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(255, 100, 100, 200);
            }
        """)
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(min_btn)
        btn_layout.addWidget(close_btn)
        title_layout.addLayout(btn_layout)
        
        container_layout.addWidget(title_bar)
        
        # 创建控件
        self.create_controls(container_layout)
        
        # 将容器添加到主布局
        main_layout.addWidget(container)
        
        # 设置布局
        central_widget.setLayout(main_layout)
    
    def create_controls(self, layout):
        """创建控件"""
        # 用户信息区域
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(240, 240, 240, 150);
                border-radius: 10px;
                padding: 5px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(10, 10, 10, 10)
        info_layout.setSpacing(8)
        
        # 昵称输入框
        nickname_layout = QHBoxLayout()
        nickname_label = QLabel("昵称:")
        nickname_label.setStyleSheet("font-weight: bold; color: #444;")
        self.nickname_input = QLineEdit()
        self.nickname_input.setPlaceholderText("请输入您的昵称")
        self.nickname_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 180);
            }
            QLineEdit:focus {
                border: 1px solid #66afe9;
                background-color: white;
            }
        """)
        nickname_layout.addWidget(nickname_label)
        nickname_layout.addWidget(self.nickname_input)
        info_layout.addLayout(nickname_layout)
        
        # 关系选择下拉框
        relation_layout = QHBoxLayout()
        relation_label = QLabel("关系:")
        relation_label.setStyleSheet("font-weight: bold; color: #444;")
        self.relation_combo = QComboBox()
        self.relation_combo.addItems(["", "朋友", "同事", "家人","上司", "恋人", "同学","暗恋对象","其他"])
        self.relation_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 180);
            }
            QComboBox:focus {
                border: 1px solid #66afe9;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        relation_layout.addWidget(relation_label)
        relation_layout.addWidget(self.relation_combo)
        info_layout.addLayout(relation_layout)
        
        # 性别选择下拉框
        gender_layout = QHBoxLayout()
        gender_label = QLabel("对方性别:")
        gender_label.setStyleSheet("font-weight: bold; color: #444;")
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "男", "女"])
        self.gender_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 180);
            }
            QComboBox:focus {
                border: 1px solid #66afe9;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
        """)
        gender_layout.addWidget(gender_label)
        gender_layout.addWidget(self.gender_combo)
        info_layout.addLayout(gender_layout)
        
        # 自定义关系输入框（初始隐藏）
        self.custom_relation_input = QLineEdit()
        self.custom_relation_input.setPlaceholderText("请输入自定义关系")
        self.custom_relation_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 180);
            }
            QLineEdit:focus {
                border: 1px solid #66afe9;
                background-color: white;
            }
        """)
        self.custom_relation_input.hide()
        info_layout.addWidget(self.custom_relation_input)
        
        # 补充信息输入框
        additional_info_layout = QHBoxLayout()
        additional_info_label = QLabel("补充信息:")
        additional_info_label.setStyleSheet("font-weight: bold; color: #444;")
        self.additional_info_input = QLineEdit()
        self.additional_info_input.setPlaceholderText("请输入补充信息（可选）")
        self.additional_info_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                background-color: rgba(255, 255, 255, 180);
            }
            QLineEdit:focus {
                border: 1px solid #66afe9;
                background-color: white;
            }
        """)
        additional_info_layout.addWidget(additional_info_label)
        additional_info_layout.addWidget(self.additional_info_input)
        info_layout.addLayout(additional_info_layout)
        
        layout.addWidget(info_frame)
        
        # 结果显示区域 - 使用QTextBrowser代替QListWidget以更好地显示Markdown格式
        self.result_list = QTextBrowser()
        self.result_list.setStyleSheet("""
            QTextBrowser {
                border: 1px solid #ccc;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 180);
                padding: 5px;
            }
        """)
        self.result_list.setMinimumHeight(150)
        self.result_list.setFixedWidth(280)  # 设置固定宽度
        self.result_list.setOpenExternalLinks(True)  # 允许打开外部链接
        self.result_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用垂直滚动条
        self.result_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        self.result_list.setLineWrapMode(QTextBrowser.WidgetWidth)  # 设置文本自动换行
        layout.addWidget(self.result_list)
        
        # 功能按钮区域
        buttons_layout = QHBoxLayout()
        
        # 样式化按钮
        button_style = """
            QPushButton {
                background-color: rgba(70, 130, 180, 200);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(70, 130, 180, 230);
            }
            QPushButton:pressed {
                background-color: rgba(60, 110, 150, 230);
            }
            QPushButton:disabled {
                background-color: rgba(150, 150, 150, 200);
            }
        """
        
        self.predict_btn = QPushButton("预测回复")
        self.predict_btn.setStyleSheet(button_style)
        
        self.suggest_btn = QPushButton("建议回复")
        self.suggest_btn.setStyleSheet(button_style)
        
        self.analyze_btn = QPushButton("对话分析")
        self.analyze_btn.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.predict_btn)
        buttons_layout.addWidget(self.suggest_btn)
        buttons_layout.addWidget(self.analyze_btn)
        
        layout.addLayout(buttons_layout)
        
        # 状态显示
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 绑定按钮事件
        self.predict_btn.clicked.connect(self.on_predict)
        self.suggest_btn.clicked.connect(self.on_suggest)
        self.analyze_btn.clicked.connect(self.on_analyze)
        
        # 绑定关系下拉框变化事件
        self.relation_combo.currentTextChanged.connect(self.on_relation_changed)
        
        # 加载用户配置
        if self.config.user_config:
            self.nickname_input.setText(self.config.user_config.get("nickname", ""))
            relation = self.config.user_config.get("default_relation", "朋友")
            index = self.relation_combo.findText(relation)
            if index >= 0:
                self.relation_combo.setCurrentIndex(index)
    
    # 窗口拖动相关方法
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.draggable:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def _(self, callback):
        """辅助方法，用于在主线程中安全执行回调函数"""
        if callable(callback):
            try:
                callback()
                return True
            except Exception as e:
                if self.config.debug_mode:
                    print(f"主线程回调执行失败: {str(e)}")
                return False
        return False
    
    def on_relation_changed(self, text):
        """关系下拉框变化事件处理"""
        if text == "其他":
            self.custom_relation_input.show()
        else:
            self.custom_relation_input.hide()
    
    def get_user_input(self):
        """安全地获取用户输入，在主线程中执行"""
        relation = self.relation_combo.currentText()
        if relation == "其他":
            relation = self.custom_relation_input.text() or "其他"
        gender = self.gender_combo.currentText()
        return self.nickname_input.text(), relation, self.additional_info_input.text(), gender
    
    # 添加一个专门用于线程间通信的槽函数
    @pyqtSlot(object)
    def get_input_from_main_thread(self, callback):
        """在主线程中执行回调函数获取用户输入"""
        if callback:
            callback()
    
    def _get_user_input_thread_safe(self):
        """线程安全地获取用户输入"""
        result = [None, None, None, None]
        
        def _get_values():
            nickname, relation, additional_info, gender = self.get_user_input()
            result[0] = nickname
            result[1] = relation
            result[2] = additional_info
            result[3] = gender
        
        try:
            # 使用专门的槽函数在主线程中执行获取输入操作
            QMetaObject.invokeMethod(self, "get_input_from_main_thread", 
                Qt.BlockingQueuedConnection,
                Q_ARG(object, _get_values))
        except Exception as e:
            # 如果上述方法失败，记录错误并尝试直接获取
            if self.config.debug_mode:
                print(f"线程安全获取用户输入失败: {e}")
            nickname, relation, additional_info, gender = self.get_user_input()
            result[0] = nickname
            result[1] = relation
            result[2] = additional_info
            result[3] = gender
        
        return result[0], result[1], result[2], result[3]
    
    def on_predict(self):
        """预测按钮点击事件"""
        self.status_label.setText("正在捕获聊天内容...")
        self.predict_btn.setEnabled(False)
        
        # 在新线程中执行，避免UI卡顿
        threading.Thread(target=self._do_predict, daemon=True).start()
    
    def _do_predict(self):
        """执行预测操作"""
        try:
            # 捕获聊天内容
            chat_history = self.wechat_capture.capture_chat_content()
            
            if not chat_history:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, "未能捕获聊天内容，请确保微信窗口处于活动状态"))
                QMetaObject.invokeMethod(self.predict_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "clear",
                Qt.QueuedConnection)
            
            content = "### 捕获的聊天内容\n\n"
            for message in chat_history:
                content += f"{message}\n"
            content += "\n### 预测结果\n\n"
            
            # 获取用户输入（需要在主线程中执行）
            try:
                # 使用线程安全的方法获取用户输入
                nickname, relation, additional_info, gender = self._get_user_input_thread_safe()
                
                # 保存用户配置
                self.config.save_user_config(nickname=nickname, relation=relation)
            except Exception as e:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"获取用户输入失败: {str(e)}"))
                QMetaObject.invokeMethod(self.predict_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "正在预测回复..."))
            
            # 调用API预测回复
            predictions = self.api_client.predict_replies(
                chat_history, nickname, relation, additional_info, gender
            )
            
            # 显示结果
            for prediction in predictions:
                content += f"- {prediction}\n"
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "setMarkdown",
                Qt.QueuedConnection,
                Q_ARG(str, content))
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "预测完成"))
            
        except Exception as e:
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, f"预测失败: {str(e)}"))
        finally:
            QMetaObject.invokeMethod(self.predict_btn, "setEnabled",
                Qt.QueuedConnection,
                Q_ARG(bool, True))
    
    def on_suggest(self):
        """建议回复按钮点击事件"""
        self.status_label.setText("正在捕获聊天内容...")
        self.suggest_btn.setEnabled(False)
        
        # 在新线程中执行，避免UI卡顿
        threading.Thread(target=self._do_suggest, daemon=True).start()
    
    def _do_suggest(self):
        """执行建议回复操作"""
        try:
            # 捕获聊天内容
            chat_history = self.wechat_capture.capture_chat_content()
            
            if not chat_history:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, "未能捕获聊天内容，请确保微信窗口处于活动状态"))
                QMetaObject.invokeMethod(self.suggest_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "clear",
                Qt.QueuedConnection)
            
            content = "### 捕获的聊天内容\n\n"
            for message in chat_history:
                content += f"{message}\n"
            content += "\n### 建议回复\n\n"
            
            # 获取用户输入（需要在主线程中执行）
            try:
                # 使用线程安全的方法获取用户输入
                nickname, relation, additional_info, gender = self._get_user_input_thread_safe()
                
                # 保存用户配置
                self.config.save_user_config(nickname=nickname, relation=relation)
            except Exception as e:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"获取用户输入失败: {str(e)}"))
                QMetaObject.invokeMethod(self.suggest_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "正在生成建议回复..."))
            
            # 调用API生成建议回复
            try:
                suggestions = self.api_client.suggest_replies(
                    chat_history, nickname, relation, additional_info, gender
                )
                
                # 显示结果
                if suggestions and isinstance(suggestions, list):
                    for suggestion in suggestions:
                        content += f"- {suggestion}\n"
                else:
                    content += "- 暂无建议回复\n"
            except Exception as e:
                content += f"- 生成建议失败: {str(e)}\n"
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "setMarkdown",
                Qt.QueuedConnection,
                Q_ARG(str, content))
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "建议生成完成"))
            
        except Exception as e:
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, f"生成建议失败: {str(e)}"))
        finally:
            QMetaObject.invokeMethod(self.suggest_btn, "setEnabled",
                Qt.QueuedConnection,
                Q_ARG(bool, True))
    
    def on_analyze(self):
        """对话分析按钮点击事件"""
        self.status_label.setText("正在捕获聊天内容...")
        self.analyze_btn.setEnabled(False)
        
        # 在新线程中执行，避免UI卡顿
        threading.Thread(target=self._do_analyze, daemon=True).start()
    
    def _do_analyze(self):
        """执行对话分析操作"""
        try:
            # 捕获聊天内容
            chat_history = self.wechat_capture.capture_chat_content()
            
            if not chat_history:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, "未能捕获聊天内容，请确保微信窗口处于活动状态"))
                QMetaObject.invokeMethod(self.analyze_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "clear",
                Qt.QueuedConnection)
            
            content = "### 捕获的聊天内容\n\n"
            for message in chat_history:
                content += f"{message}\n"
            content += "\n### 对话分析结果\n\n"
            
            # 获取用户输入（需要在主线程中执行）
            try:
                # 使用线程安全的方法获取用户输入
                nickname, relation, additional_info, gender = self._get_user_input_thread_safe()
                
                # 保存用户配置
                self.config.save_user_config(nickname=nickname, relation=relation)
            except Exception as e:
                QMetaObject.invokeMethod(self.status_label, "setText",
                    Qt.QueuedConnection,
                    Q_ARG(str, f"获取用户输入失败: {str(e)}"))
                QMetaObject.invokeMethod(self.analyze_btn, "setEnabled",
                    Qt.QueuedConnection,
                    Q_ARG(bool, True))
                return
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "正在分析对话..."))
            
            # 调用API分析对话
            analysis = self.api_client.analyze_conversation(
                chat_history, nickname, relation, additional_info, gender
            )
            
            # 在主线程中更新UI
            QMetaObject.invokeMethod(self.result_list, "setMarkdown",
                Qt.QueuedConnection,
                Q_ARG(str, content + analysis))
            
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, "分析完成"))
            
        except Exception as e:
            QMetaObject.invokeMethod(self.status_label, "setText",
                Qt.QueuedConnection,
                Q_ARG(str, f"分析失败: {str(e)}"))
        finally:
            QMetaObject.invokeMethod(self.analyze_btn, "setEnabled",
                Qt.QueuedConnection,
                Q_ARG(bool, True))