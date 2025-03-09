#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
模型交互模块

负责与DeepSeek API通信，发送聊天历史并获取预测结果。
"""

import time
from openai import OpenAI

class DeepSeekAPI:
    """DeepSeek API交互类"""
    
    def __init__(self, config):
        """初始化API客户端"""
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base_url
        )
        # 上次请求时间，用于控制请求频率
        self.last_request_time = 0
        # 请求间隔时间（秒）
        self.request_interval = 2
    
    def _wait_for_rate_limit(self):
        """等待请求间隔，避免频率限制"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.request_interval:
            # 需要等待的时间
            wait_time = self.request_interval - elapsed
            time.sleep(wait_time)
        
        # 更新上次请求时间
        self.last_request_time = time.time()
    
    def predict_replies(self, chat_history, nickname="", relation="朋友", additional_info="", gender=""):
        """预测对方可能的回复"""
        self._wait_for_rate_limit()
        
        # 构建系统提示
        system_prompt = "你是一个专业的对话预测助手。根据提供的聊天历史，预测对方接下来最可能说的5句话。"
        
        # 构建用户提示
        if nickname:
            user_prompt =  f"\n我的昵称是：{nickname}\n"
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt += f"以下是{nickname}与一位{relation_text}的聊天记录：\n\n"
        else:
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt = f"\n以下是我与一位{relation_text}的聊天记录：\n\n"
        
        # 添加聊天历史
        for message in chat_history:
            user_prompt += f"{message}\n"
        
        if additional_info:
            user_prompt += f"\n补充信息：{additional_info}\n"
        
        user_prompt += "\n请预测对方接下来最可能回复的5句话，使用自然的口语表达，避免重复句式，可以使用Emoji表情。"
        print(user_prompt)
        try:
            # 调用API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            # 解析结果
            result = response.choices[0].message.content
            return self._parse_predictions(result)
            
        except Exception as e:
            if self.config.debug_mode:
                print(f"API请求失败: {e}")
            return [f"预测失败: {str(e)}"] if self.config.debug_mode else ["预测失败，请稍后再试"]
    
    def suggest_replies(self, chat_history, nickname="", relation="朋友", additional_info="", gender=""):
        """生成建议回复"""
        self._wait_for_rate_limit()
        
        # 构建系统提示
        system_prompt = "你是一个专业的对话助手。根据提供的聊天历史，生成5条合适的回复内容。"
        
        # 构建用户提示
        if nickname:
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt = f"以下是{nickname}与一位{relation_text}的聊天记录：\n\n"
        else:
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt = f"以下是我与一位{relation_text}的聊天记录：\n\n"
        # 添加聊天历史
        for message in chat_history:
            user_prompt += f"{message}\n"
        
        
        if additional_info:
            user_prompt += f"\n补充信息：{additional_info}\n"
        
        user_prompt += "\n请为我生成5条合适的回复内容，使用自然的口语表达，避免重复句式，可以使用Emoji表情。"
        print(user_prompt)
        try:
            # 调用API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            # 解析结果
            result = response.choices[0].message.content
            return self._parse_predictions(result)
            
        except Exception as e:
            if self.config.debug_mode:
                print(f"API请求失败: {e}")
            return [f"生成建议失败: {str(e)}"] if self.config.debug_mode else ["生成建议失败，请稍后再试"]
    
    def analyze_conversation(self, chat_history, nickname="", relation="朋友", additional_info="", gender=""):
        """分析对话内容"""
        self._wait_for_rate_limit()
        
        # 构建系统提示
        system_prompt = "你是一个专业的对话分析师。根据提供的聊天历史，根据对话内容分析双方的情绪，以及潜台词，并提供洞察。"
        
        # 构建用户提示
        if nickname:
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt = f"以下是{nickname}与一位{relation_text}的聊天记录：\n\n"
        else:
            gender_text = f"{'男' if gender == '男' else '女'}性" if gender else ""
            relation_text = f"{gender_text}{relation}" if gender else relation
            user_prompt = f"以下是我与一位{relation_text}的聊天记录：\n\n"
        # 添加聊天历史
        for message in chat_history:
            user_prompt += f"{message}\n"
        
        
        if additional_info:
            user_prompt += f"\n补充信息：{additional_info}\n"
        
        user_prompt += "\n请分析这段对话，提供有价值的洞察，包括但不限于：\n1. 对话的主要话题和情感基调\n2. 对方可能的想法和意图\n3. 对话中的潜在问题或机会\n4. 改善沟通的建议"
        print(user_prompt)
        try:
            # 调用API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                stream=False
            )
            
            # 获取结果
            result = response.choices[0].message.content
            return result
            
        except Exception as e:
            if self.config.debug_mode:
                print(f"API请求失败: {e}")
            return f"分析失败: {str(e)}" if self.config.debug_mode else "分析失败，请稍后再试"
    
    def _parse_predictions(self, content):
        """解析预测结果，提取出预测的回复列表"""
        if not content:
            return []
        
        # 尝试解析格式化的回复（如：1. xxx\n2. xxx）
        lines = content.split('\n')
        predictions = []
        
        for line in lines:
            line = line.strip()
            # 匹配格式为"数字. 内容"的行
            if line and (line[0].isdigit() and line[1:].startswith('. ')):
                # 提取预测内容（去掉序号）
                prediction = line[line.find('.')+1:].strip()
                if prediction:
                    predictions.append(prediction)
        
        # 如果没有找到格式化的回复，则直接按行分割
        if not predictions:
            predictions = [line.strip() for line in lines if line.strip()]
            # 限制最多5条预测
            predictions = predictions[:5]
        
        return predictions