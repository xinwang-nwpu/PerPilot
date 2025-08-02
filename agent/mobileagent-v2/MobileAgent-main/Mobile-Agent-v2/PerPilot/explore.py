# coding=utf-8
from api import inference_chat
from chat import personalization_chat
from prompt import get_explore_prompt
from personalization import personalization_solve
from Semantic_Analysis import semantic_analysis
from MobileAgent.controller import home
import json
from run2 import run


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
        print(f"warning: No entry found with ID {target_id}, configuration not updated")

    return config


def explore_solve(instruction, api_url, token, model, id):
    txt = []
    while True:
        chat_history = personalization_chat(instruction, txt)

        response = inference_chat(chat_history, model, api_url, token)
        response = response.replace('\n', '')
        print(f"Extracted personalized elements: {response}")
        chat_history.append(("assistant", response))

        f = open("personalization.txt", "r+", encoding="utf-8")
        lines = f.readlines()

        if response.startswith("Yes"):
            response = response.split("|")

            tmp = response[1:]
            a, b = semantic_analysis(tmp, lines)
            if len(b) != 0:
                print(f"Missing personalized information: {b}. Trying to use active exploration feature to get it.\n")
                chat_history.append(("user", get_explore_prompt(b, instruction)))
                response = inference_chat(chat_history, model, api_url, token)
                response = response.split('\n')

                print(response)
                for i in range(min(len(b), len(response))):
                    print(f"Exploring personalized information: {b[i]} with instruction: {response[i]}\n")
                    config["instruction"] = f"{response[i]}"
                    message = run(config["explore_switch"], config["instruction"], id, config["difficulty"])
                    if message != 0:
                        print(
                            f"Is the accurate information of {b[i]} {message}? Enter 1 for correct and 2 for incorrect.\n")
                        key = input()
                        if key == "1":
                            f = open("personalization.txt", "a", encoding="utf-8")
                            f.write(b[i] + "|" + str(message) + "\n")
                            home(config["adb_path"])
                            f.close()
                            if i == min(len(b), len(response)) - 1:
                                exit()
                        else:
                            print(f"can not find the accurate information of {b[i]}\nplease input it manually")
                            message = input()
                            f.write(b[i] + "|" + str(message) + "\n")
                            f.close()
                            home(config["adb_path"])
                            if i == min(len(b), len(response)) - 1:
                                exit()
                    else:

                        print(f"Could not explore the accurate information of {b[i]}. Please input it manually.")
                        home(config["adb_path"])
                        message = input()
                        f.write(b[i] + "|" + str(message) + "\n")
                        f.close()
                        if i == min(len(b), len(response)) - 1:
                            exit()

                f = open("personalization.txt", "r+", encoding="utf-8")
                lines = f.readlines()
                a, b = semantic_analysis(tmp, lines)
                for x in a:
                    instruction = instruction.lower().replace(x["id"], x["ID"])
                config["instruction"] = instruction
                config["explore_switch"] = False
                result = run(config["explore_switch"], config["instruction"], id, config["difficulty"])
                if not result:
                    print("Instruction execution failed.")
                break
            else:
                for i in a:
                    instruction = instruction.lower().replace(i["id"], i["ID"])
                print(f"Information sufficient. Instruction execution stage.")
                config["instruction"] = instruction
                config["explore_switch"] = False
                result = run(config["explore_switch"], config["instruction"], id, config["difficulty"])

                if not result:
                    print("Instruction execution failed.")
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
            result = run(config["explore_switch"], config["instruction"], id, config["difficulty"])
            if not result:
                print("Instruction execution failed.")
            break


config = {
    "adb_path": "",
    "instruction": "",
    "difficulty": 0,
    "API_url": "",
    "token": "",
    "model": "o4-mini",
    "add_info": "you are a helpful agent",
    "personalization_switch": True,
    "explore_switch": True
}
token = "sk-ff1357c8726e40679a4bc9903c766717"
instruction_id = "16"
config = update_config_instruction(config, "instruction.json", instruction_id)
history = personalization_chat(config["instruction"], [])
if config["explore_switch"]:
    explore_solve(config["instruction"], config["API_url"], config["token"], config["model"], instruction_id)
elif config["personalization_switch"]:
    config["instruction"] = personalization_solve(config["instruction"], history, config["deep_api_url"],
                                                  config["deep_token"])
    explore_switch = False
    run(explore_switch, config["instruction"], instruction_id, config["difficulty"])
else:
    explore_switch = False
    run(explore_switch, config["instruction"], instruction_id, config["difficulty"])
