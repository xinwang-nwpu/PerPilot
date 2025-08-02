# coding=utf-8
from MobileAgent.api import inference_chat
from MobileAgent.prompt import personalization_solve_prompt, get_personalization_message_prompt


def personalization_solve(instruction, chat_history, api_url, token):
    # 第一次请求
    response = inference_chat(chat_history, "qwen-plus", api_url, token)
    print("第一次响应:", response)
    chat_history.append(("assistant", response))

    # 读取知识库
    f = open("personalization.txt", "r+", encoding="utf-8")
    knowledge = f.read()

    # 条件判断后继续对话
    if response.startswith("是"):
        # 追加用户的新问题到历史
        chat_history.append(("user", personalization_solve_prompt(knowledge)))
        # 第二次请求（携带完整历史）
        response = inference_chat(chat_history, "qwen-plus", api_url, token)
        print("第二次响应:", response)
        chat_history.append(("assistant", response))  # 再次记录响应
        if response.startswith("否"):
            response = response.split("|")
            print(f"缺少{response[1:]}的相对应的精确信息，请进行添加，输入格式为信息1 信息2\n")
            message = input().split(" ")
            for i in range(len(message)):
                f.write("\n" + response[i + 1] + "|" + message[i])
            f.close()
            f = open("personalization.txt", "r+", encoding="utf-8")
            temp_message = f.read()
            chat_history.append(("user", get_personalization_message_prompt(temp_message)))
            response = inference_chat(chat_history, "qwen-plus", api_url, token)
            print("第三次响应:", response)
        instruction = response
    f.close()
    return instruction
