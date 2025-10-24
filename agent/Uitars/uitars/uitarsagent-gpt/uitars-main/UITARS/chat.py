# coding=utf-8
import copy
from UITARS.api import encode_image
from UITARS.prompt import get_personalization_prompt, get_explore_prompt, create_all_message_prompt, verify_per_prompt


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


def explore_chat(instruction, txt):

    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_explore_prompt(instruction, txt))
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


def verify_all_chat(id, instruction):
    import os
    import re

    root_dir = "./shot/"

    folder_path = os.path.join(root_dir, str(id))


    if not os.path.isdir(folder_path):
        print(f"错误: 文件夹 {folder_path} 不存在")
        return None, None


    pattern = re.compile(r'^(\d+)\.png$')


    image_numbers = []


    for filename in os.listdir(folder_path):

        match = pattern.match(filename)
        if match:

            number = int(match.group(1))
            image_numbers.append(number)


    if not image_numbers:
        print(f"警告: 在文件夹 {folder_path} 中未找到符合要求的图片")
        return None, None


    image_numbers.sort()


    content = [
        {
            "type": "text",
            "text": create_all_message_prompt(instruction)
        }
    ]


    for number in image_numbers:
        image_path = os.path.join(folder_path, f"{number}.png")

        base64_image = encode_image(image_path)

        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })


    chat_history = [
        ("system", "You are a Senior Mobile Phone User with rich experience in operating various mobile devices."),
        ("user", content)
    ]
    return chat_history


def verify_per_chat(txt):
    chat_history = [
        ("system", "You are an experienced linguist"),
        ("user", verify_per_prompt(txt))
    ]
    return chat_history
