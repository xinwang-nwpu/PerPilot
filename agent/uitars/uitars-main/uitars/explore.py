# coding=utf-8
from uitars.api import inference_chat
from uitars.chat import personalization_chat
from uitars.prompt import get_explore_prompt
from uitars.personalization import personalization_solve
from uitars.Semantic_Analysis import semantic_analysis
from run import XAgent
from uitars.controller import home
import json


def update_config_instruction(config, json_file_path, target_id):

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found {json_file_path}")
        return config
    except json.JSONDecodeError:
        print(f"Error: Unable to parse JSON file {json_file_path}")
        return config

    instruction = None
    difficult = None
    for item in json_data:
        if str(item.get('id')) == str(target_id):
            instruction = item.get('instruction')
            difficult = item.get('difficulty')
            break

    if instruction:
        config['instruction'] = instruction
        config['difficulty'] = difficult
    else:
        print(f"警告：未找到ID为{target_id}的条目，配置未更新")

    return config


def explore_solve(instruction, api_url, token, model, id):
    txt = []
    while True:
        chat_history = personalization_chat(instruction, txt)

        response = inference_chat(chat_history, model, api_url, token)
        response = response.replace('\n', '')
        print(f"Extract personalization elements:{response}")
        chat_history.append(("assistant", response))

        f = open("personalization.txt", "r+", encoding="utf-8")
        lines = f.readlines()

        if response.startswith("Yes"):
            response = response.split("|")

            tmp = response[1:]
            a, b = semantic_analysis(tmp, lines)
            if len(b) != 0:
                print(f"Lack of information:{b}try using active discovery to get it\n")

                chat_history.append(("user", get_explore_prompt(b, instruction)))
                response = inference_chat(chat_history, model, api_url, token)
                response = response.split('\n')

                for i in range(min(len(b), len(response))):
                    print(f"Is trying to get accurate information:{response[i]}\n")
                    config["instruction"] = f"{response[i]}"
                    agent = XAgent(config)
                    message = agent.run(instruction_id)
                    if message != 0:
                        print(
                            f"Is the accurate information about {b[i]}:{message}? If correct, input 1; if incorrect, input 2\n")
                        key = input()
                        if key == "1":
                            f = open("personalization.txt", "a", encoding="utf-8")
                            f.write(b[i] + "|" + str(message) + "\n")
                            home(config["adb_path"])
                            f.close()
                            if i == min(len(b), len(response)) - 1:
                                exit()
                        else:
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
                            f"Is the accurate information about {b[i]}:{message}? If incorrect, please input the "
                            f"accurate information\n")
                        home(config["adb_path"])
                        message = input()
                        f.write(b[i] + "|" + str(message) + "\n")
                        f.close()

                f = open("personalization.txt", "r+", encoding="utf-8")
                lines = f.readlines()
                a, b = semantic_analysis(tmp, lines)
                for x in a:
                    instruction = instruction.lower().replace(x["id"], x["ID"])

                config["instruction"] = instruction
                config["explore_switch"] = False

                agent = XAgent(config)
                result = agent.run(instruction_id)
                if not result:
                    print("Instruction execution failed")
                break
            else:
                for i in a:
                    instruction = instruction.lower().replace(i["id"], i["ID"])
                print(f"Replace instruction:{instruction}")

                config["instruction"] = instruction
                config["explore_switch"] = False

                agent = XAgent(config)
                result = agent.run(instruction_id)
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

            agent = XAgent(config)
            result = agent.run(instruction_id)
            if not result:
                print("Instruction execution failed")
            break


config = {
    "adb_path": "C:\\platform-tools\\adb.exe",
    "instruction": "",
    "difficulty": 0,
    "API_url": "http://35.220.164.252:3888/v1",
    "token": "sk-wtQwjJwJFHsHFL1iH2P0Y6eqKXNvkab1w4ucpFwYWkIKJ5Tq",
    "model": "o4-mini",
    "add_info": "you are a helpful agent",
    "personalization_switch": True,
    "explore_switch": True
}

instruction_id = "22"
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
