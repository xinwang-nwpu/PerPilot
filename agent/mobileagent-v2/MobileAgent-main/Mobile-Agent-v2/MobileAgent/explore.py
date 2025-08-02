# coding=utf-8
from XAGENT.api import inference_chat
from XAGENT.prompt import personalization_solve_prompt, get_personalization_message_prompt, get_explore_prompt


def explore_solve(instruction, chat_history, api_url, token):
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
            tmp = response[1:]
            print(f"缺少{tmp}相应的信息正在尝试使用主动探索功能获取\n")
            chat_history.append(("user", get_explore_prompt(response, instruction)))
            response = inference_chat(chat_history, "qwen-plus", api_url, token)
            response = response.split('\n')
            print(response)
            return tmp, response
    f.close()
    return instruction
