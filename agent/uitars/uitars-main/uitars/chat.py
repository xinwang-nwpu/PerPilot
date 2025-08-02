# coding=utf-8
import copy
from uitars.api import encode_image
from uitars.prompt import get_personalization_prompt


def init_action_chat():
    operation_history = []
    system_prompt = "You are an intelligent AI-powered smartphone operation assistant. Your task is to help operate the user's smartphone to fulfill their instructions."
    operation_history.append(["system", [{"type": "text", "text": system_prompt}]])
    return operation_history


def personalization_chat(instruction, txt):
    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_personalization_prompt(instruction, txt))
    ]
    return chat_history


def init_memory_chat():
    operation_history = []
    system_prompt = "you are a helpful agent"
    operation_history.append(["system", [{"type": "text", "text": system_prompt}]])
    return operation_history


def add_response(role, prompt, chat_history, image=None):
    new_chat_history = copy.deepcopy(chat_history)
    if image:
        base64_image = encode_image(image)
        content = [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            },
        ]
    else:
        content = [
            {
                "type": "text",
                "text": prompt
            },
        ]
    new_chat_history.append([role, content])
    return new_chat_history


