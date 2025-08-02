# coding=utf-8
import subprocess

from prompt import get_personalization_prompt


def home(adb_path):
    command = adb_path + f" shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)


# 初始化对话历史
def personalization_chat(instruction, txt):
    # 初始化对话历史
    chat_history = [
        ("system", "You are a highly capable large language model skilled at understanding instructions."),
        ("user", get_personalization_prompt(instruction, txt))
    ]
    return chat_history
