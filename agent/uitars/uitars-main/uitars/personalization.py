# coding=utf-8
from XAGENT.api import inference_chat
from XAGENT.prompt import personalization_solve_prompt, get_personalization_message_prompt


def personalization_solve(instruction, chat_history, api_url, token):
    response = inference_chat(chat_history, "o4-mini", api_url, token)
    print("onc:", response)
    chat_history.append(("assistant", response))

    f = open("personalization.txt", "r+", encoding="utf-8")
    knowledge = f.read()

    if response.startswith("Yes"):

        chat_history.append(("user", personalization_solve_prompt(knowledge)))

        response = inference_chat(chat_history, "o4-mini", api_url, token)
        print("第二次响应:", response)
        chat_history.append(("assistant", response))
        if response.startswith("No"):
            response = response.split("|")
            print(f"缺少{response[1:]}的相对应的精确信息，请进行添加，输入格式为信息1 信息2\n")
            message = input().split(" ")
            for i in range(len(message)):
                f.write("\n" + response[i + 1] + "|" + message[i])
            f.close()
            f = open("personalization.txt", "r+", encoding="utf-8")
            temp_message = f.read()
            chat_history.append(("user", get_personalization_message_prompt(temp_message)))
            response = inference_chat(chat_history, "o4-mini", api_url, token)
            print("第三次响应:", response)
        instruction = response
    f.close()
    return instruction
