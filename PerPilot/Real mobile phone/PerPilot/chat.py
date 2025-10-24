# coding=utf-8
import base64
import os
import re

from prompt import get_personalization_prompt, create_message_prompt, create_all_message_prompt, verify_per_prompt


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# 初始化对话历史
def personalization_chat(instruction, txt):
    # 初始化对话历史
    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_personalization_prompt(instruction, txt))
    ]
    return chat_history


def verify_chat(id, instruction):
    root_dir = "./shot/"

    folder_path = os.path.join(root_dir, str(id))


    if not os.path.isdir(folder_path):
        print(f"wrong: folder {folder_path} not exist")
        return None, None


    pattern = re.compile(r'^(\d+)\.png$')


    image_numbers = []


    for filename in os.listdir(folder_path):

        match = pattern.match(filename)
        if match:

            number = int(match.group(1))
            image_numbers.append(number)


    if not image_numbers:
        print(f"warning: in folder {folder_path} not found image")
        return None, None


    min_number = min(image_numbers)
    max_number = max(image_numbers)


    image1 = os.path.join(folder_path, f"{min_number}.png")
    image2 = os.path.join(folder_path, f"{max_number}.png")

    base64_image1 = encode_image(image1)
    base64_image2 = encode_image(image2)
    content = [
        {
            "type": "text",
            "text": create_message_prompt(instruction)
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image1}"
            }
        },
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image2}"
            }
        },
    ]

    chat_history = [
        ("system", "You are a Senior Mobile Phone User with rich experience in operating various mobile devices."),
        ("user", content)
    ]
    return chat_history


def verify_all_chat(id, instruction):
    import os
    import re

    root_dir = "./shot/"

    folder_path = os.path.join(root_dir, str(id))


    if not os.path.isdir(folder_path):
        print(f"warning: folder {folder_path} not exist")
        return None, None


    pattern = re.compile(r'^(\d+)\.png$')


    image_numbers = []


    for filename in os.listdir(folder_path):

        match = pattern.match(filename)
        if match:

            number = int(match.group(1))
            image_numbers.append(number)


    if not image_numbers:
        print(f"warning: in folder {folder_path} not found image")
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

