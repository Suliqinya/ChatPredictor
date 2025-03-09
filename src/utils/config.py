#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块

负责加载和管理程序的配置信息，包括API密钥、应用设置等。
"""

import os
import json
from pathlib import Path

class Config:
    """配置类，负责管理程序配置"""
    
    def __init__(self):
        """初始化配置"""
        # 基础配置
        self.app_name = os.getenv("APP_NAME", "智能聊天预测程序")
        self.debug_mode = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # API配置
        self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-b92cee1642e34f0a84b08227410d01b5")
        self.api_base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        
        # 聊天历史配置
        self.max_history_length = int(os.getenv("MAX_HISTORY_LENGTH", "5"))
        
        # 用户配置
        self.user_config_path = Path.home() / ".chat_predictor" / "user_config.json"
        self.user_config = self.load_user_config()
    
    def load_user_config(self):
        """加载用户配置"""
        if not self.user_config_path.exists():
            # 创建默认配置
            default_config = {
                "nickname": "",
                "default_relation": "朋友",
                "additional_info": ""
            }
            # 确保目录存在
            self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存默认配置
            with open(self.user_config_path, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            return default_config
        
        # 加载现有配置
        try:
            with open(self.user_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载用户配置失败: {e}")
            return {"nickname": "", "default_relation": "朋友", "additional_info": ""}
    
    def save_user_config(self, nickname=None, relation=None, additional_info=None):
        """保存用户配置"""
        if nickname is not None:
            self.user_config["nickname"] = nickname
        if relation is not None:
            self.user_config["default_relation"] = relation
        if additional_info is not None:
            self.user_config["additional_info"] = additional_info
        
        # 确保目录存在
        self.user_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存配置
        try:
            with open(self.user_config_path, "w", encoding="utf-8") as f:
                json.dump(self.user_config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存用户配置失败: {e}")
            return False