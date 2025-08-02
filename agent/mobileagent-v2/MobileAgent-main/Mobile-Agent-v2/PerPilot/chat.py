# coding=utf-8
import copy
from prompt import get_personalization_prompt


# 初始化对话历史
def personalization_chat(instruction, txt):
    # 初始化对话历史
    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_personalization_prompt(instruction, txt))
    ]
    return chat_history



