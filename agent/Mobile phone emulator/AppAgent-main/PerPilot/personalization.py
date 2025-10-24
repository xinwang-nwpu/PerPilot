# coding=utf-8
from api import inference_chat2
from prompt import personalization_solve_prompt, get_personalization_message_prompt


def personalization_solve(instruction, chat_history, api_url, token):

    response,token2 = inference_chat2(chat_history, "o4-mini", api_url, token)
    print("First response:", response)
    chat_history.append(("assistant", response))


    f = open("personalization.txt", "r+", encoding="utf-8")
    knowledge = f.read()


    if response.startswith("Yes"):

        chat_history.append(("user", personalization_solve_prompt(knowledge)))

        response,token2 = inference_chat2(chat_history, "o4-mini", api_url, token)
        print("Second response:", response)
        chat_history.append(("assistant", response))
        if response.startswith("No"):
            response = response.split("|")
            print(f"lack of {response[1:]}'s corresponding exact information, please add it, the format is information1 information2\n")
            message = input().split(" ")
            for i in range(len(message)):
                f.write("\n" + response[i + 1] + "|" + message[i])
            f.close()
            f = open("personalization.txt", "r+", encoding="utf-8")
            temp_message = f.read()
            chat_history.append(("user", get_personalization_message_prompt(temp_message)))
            response,token2 = inference_chat2(chat_history, "o4-mini", api_url, token)
            print("Third response:", response)
        instruction = response
    f.close()
    return instruction
