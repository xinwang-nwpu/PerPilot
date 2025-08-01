# coding=utf-8
from api import inference_chat2, append_to_file
from chat import personalization_chat
from prompt import get_explore_prompt
from personalization import personalization_solve
from Semantic_Analysis import semantic_analysis
from run import XAgent
from XAGENT.controller import home
import json
import tkinter as tk
from tkinter import messagebox


def tixin():
    # 创建隐藏的主窗口
    root = tk.Tk()
    root.withdraw()
    # 显示更醒目的弹窗
    root.tk.call('wm', 'attributes', '.', '-topmost', '1')
    messagebox.showwarning("system",
                           "⚠️ import ⚠️\n\n"
                           "system:Please handle the corresponding tasks in a timely manner.",
                           icon='warning')


def update_config_instruction(config, json_file_path, target_id):
    # 读取JSON数据
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"fail to find {json_file_path}")
        return config
    except json.JSONDecodeError:
        print(f"fail to parse {json_file_path}")
        return config

    # 查找对应的instruction
    instruction = None
    difficult = None
    for item in json_data:
        if str(item.get('id')) == str(target_id):
            instruction = item.get('instruction')
            difficult = item.get('difficulty')
            break

    # 更新配置
    if instruction:
        config['instruction'] = instruction
        config['difficulty'] = difficult
    else:
        print(f"warning: fail to find {target_id}")

    return config


def explore_solve(instruction, api_url, token, model, id):
    txt = []
    while True:
        chat_history = personalization_chat(instruction, txt)

        append_to_file(id, f"instruction:{instruction}")
        append_to_file(id, f"Personalized processing phase")
        response = inference_chat2(chat_history, model, api_url, token)
        response = response.replace('\n', '')
        print(f"Extract personalization elements:{response}")
        chat_history.append(("assistant", response))

        f = open("personalization.txt", "r+", encoding="utf-8")
        lines = f.readlines()

        if response.startswith("Yes"):
            response = response.split("|")
            append_to_file(id, f"Extracted personalization elements:{response[1:]}")
            tmp = response[1:]
            a, b = semantic_analysis(tmp, lines)
            if len(b) != 0:
                print(f"Lack of information:{b}try using active discovery to get it\n")
                append_to_file(id, f"Exploration phase")
                append_to_file(id, f"Lack of personalization information:{b}")
                chat_history.append(("user", get_explore_prompt(b, instruction)))
                response = inference_chat2(chat_history, model, api_url, token)
                response = response.split('\n')
                append_to_file(id, f"Generated exploration instructions:{response}")
                for i in range(min(len(b), len(response))):
                    print(f"Is trying to get accurate information:{response[i]}\n")
                    append_to_file(id, f"Exploration personalized information:{b[i]} Instruction:{response[i]}")
                    config["instruction"] = f"{response[i]}"
                    agent = XAgent(config)
                    message = agent.run(instruction_id)
                    tixin()
                    if message != 0:
                        print(
                            f"Is the accurate information about {b[i]}:{message}? If correct, input 1; if incorrect, input 2\n")
                        key = input()
                        if key == "1":
                            f = open("personalization.txt", "a", encoding="utf-8")
                            f.write(b[i] + "|" + str(message) + "\n")
                            append_to_file(id, f"Explored accurate information:{message}Exploration correct\n\n")
                            home(config["adb_path"])
                            f.close()
                            if i == min(len(b), len(response)) - 1:
                                exit()
                        else:
                            append_to_file(id, f"Explored accurate information:{message}Exploration failed\n\n")
                            print(
                                f"Is the accurate information about {b[i]}:{message}? If incorrect, please input the accurate information\n")
                            message = input()
                            f.write(b[i] + "|" + str(message) + "\n")
                            f.close()
                            home(config["adb_path"])
                            if i == min(len(b), len(response)) - 1:
                                exit()
                    else:
                        print(
                            f"Is the accurate information about {b[i]}:{message}? If incorrect, please input the accurate information\n")
                        append_to_file(id, f"Exploration failed\n\n")
                        home(config["adb_path"])
                        message = input()
                        f.write(b[i] + "|" + str(message) + "\n")
                        f.close()

                f = open("personalization.txt", "r+", encoding="utf-8")
                lines = f.readlines()
                a, b = semantic_analysis(tmp, lines)
                for x in a:
                    instruction = instruction.lower().replace(x["id"], x["ID"])
                append_to_file(id, f"Replace instruction:{instruction}")
                config["instruction"] = instruction
                config["explore_switch"] = False
                append_to_file(id, f"Accurate instruction execution phase")
                agent = XAgent(config)
                result = agent.run(instruction_id)
                tixin()
                if not result:
                    print("Instruction execution failed")
                break
            else:
                for i in a:
                    instruction = instruction.lower().replace(i["id"], i["ID"])
                print(f"Replace instruction:{instruction}")
                append_to_file(id, f"Replace instruction:{instruction}")
                config["instruction"] = instruction
                config["explore_switch"] = False
                append_to_file(id, f"Accurate instruction execution phase")
                agent = XAgent(config)
                result = agent.run(instruction_id)
                tixin()
                if not result:
                    print("Instruction execution failed")
                break
        else:
            f.close()
            if len(txt) != 0:
                config["instruction"] = personalization_solve(instruction,
                                                              personalization_chat(config["instruction"], txt),
                                                              config["deep_api_url"], config["deep_token"])
            else:
                config["instruction"] = instruction
            config["explore_switch"] = False
            append_to_file(id, f"Accurate instruction execution phase")
            agent = XAgent(config)
            result = agent.run(instruction_id)
            if not result:
                print("Instruction execution failed")
            break


config = {
    "adb_path": "",
    "instruction": "",
    "difficulty": "",
    "API_url": "",
    "token": "",
    "model": "",
    "add_info": "you are a helpful agent",
    "personalization_switch": True,  # Does enabling the exploration switch
    "explore_switch": True  #Is passive acquisition activated
}

instruction_id = "73"
config = update_config_instruction(config, "instruction.json", instruction_id)
history = personalization_chat(config["instruction"], [])
if config["explore_switch"]:
    explore_solve(config["instruction"], config["API_url"], config["token"], config["model"], instruction_id)
elif config["personalization_switch"]:
    config["instruction"] = personalization_solve(config["instruction"], history, config["deep_api_url"],
                                                  config["deep_token"])
    agent = XAgent(config)
    agent.run(instruction_id)
else:
    agent = XAgent(config)
    agent.run(instruction_id)


