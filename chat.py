# coding=utf-8
import copy
from prompt import get_personalization_prompt, get_explore_prompt



def personalization_chat(instruction, txt):
    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_personalization_prompt(instruction, txt))
    ]
    return chat_history



