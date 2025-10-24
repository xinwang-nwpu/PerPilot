# coding=utf-8
import json
import os
import shutil
import subprocess
import time
import traceback
from Semantic_Analysis import semantic_analysis
from api import inference_chat2, append_to_file
from chat import personalization_chat, verify_all_chat, verify_per_chat
from emulator import start_emulator, restart_emulator, adb_connect,stop_emulator, adb_keyboard
from personalization import personalization_solve
from prompt import get_explore_prompt
from run2 import run #Encapsulate the agent's execution code as run

def home(adb_path):
    command = adb_path + f" -s 127.0.0.1:5557 shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def update_config_instruction(config, json_file_path, target_id):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: File not found {json_file_path}")
        return config
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON file {json_file_path}")
        return config


    instruction = None
    difficult = None
    for item in json_data:
        if str(item.get('id')) == str(target_id):
            instruction = item.get('instruction')
            difficult = item.get('difficulty')
            if difficult == "easy":
                difficult = 1
            elif difficult == "normal":
                difficult = 2
            elif difficult == "difficult":
                difficult = 3


    if instruction:
        config['instruction'] = instruction
        config['difficulty'] = difficult
    else:
        print(f"Warning: No item found with ID {target_id}, configuration not updated")

    return config


def explore_solve(instruction, api_url, TOKEN, model, ID):
    txt = []
    all_token = 0
    while True:
        errorflag = False
        start_emulator()
        time.sleep(50)
        adb_connect()
        time.sleep(5)
        adb_keyboard(config["adb_path"])
        chat_history = personalization_chat(instruction, txt)

        append_to_file(ID, f"instruction:{instruction}")
        append_to_file(ID, f"Personalization phase")
        response, token1 = inference_chat2(chat_history, model, api_url, TOKEN)
        all_token += token1[2]
        response = response.replace('\n', '')
        print(f"Extracting personalized elements:{response}")
        chat_history.append(("assistant", response))

        f = open("personalization.txt", "r+", encoding="utf-8")
        lines = f.readlines()

        if response.startswith("Yes"):
            response = response.split("|")
            append_to_file(ID, f"Extracting personalized elements:{response[1:]}")
            tmp = response[1:]
            a, b = semantic_analysis(tmp, lines)
            if len(b) != 0:
                print(f"Missing personalized information:{b} Trying to use active exploration feature to get it\n")
                append_to_file(ID, f"Information exploration phase")
                append_to_file(ID, f"Missing personalized information:{b}")
                chat_history.append(("user", get_explore_prompt(b, instruction)))
                response, token2 = inference_chat2(chat_history, model, api_url, TOKEN)
                all_token += token2[2]
                response = response.split('\n')
                append_to_file(ID, f"Generated exploration instructions:{response}")
                temp_response = response
                print(response)
                for i in range(min(len(b), len(temp_response))):
                    print(f"try {temp_response[i]}\n")
                    append_to_file(ID, f"Exploring personalized information:{b[i]} Instruction:{temp_response[i]}")
                    config["instruction"] = f"{temp_response[i]}"
                    message = run(config["explore_switch"], config["instruction"], ID, config["difficulty"])
                    if message != 0:
                        txt = b[i] + "|" + message
                        chat = verify_per_chat(txt)
                        response, token3 = inference_chat2(chat, model, api_url, TOKEN)
                        print(f"Verify whether the search information is successful, the verification result is{response}")
                        all_token += token3[2]
                        if response.startswith("yes"):
                            f = open("personalization.txt", "a", encoding="utf-8")
                            f.write(b[i] + "|" + str(message) + "\n")
                            f.close()
                            append_to_file(ID, f"Exploring personalized information:{b[i]} Successful:{message}\n\n")
                        else:
                            append_to_file(ID, f"Exploring personalized information:{b[i]} Failed:{message}\n\n")
                            errorflag = True
                        home(config["adb_path"])
                        if i == min(len(b), len(response)) - 1:
                            restart_emulator()
                            start_emulator()
                            time.sleep(50)
                            adb_keyboard(config["adb_path"])
                            break
                    else:

                        print(f"Failed to explore personalized information:{b[i]}\n")
                        append_to_file(ID, f"Exploring personalized information:{b[i]} Failed:Failed to explore\n\n")
                        home(config["adb_path"])
                        errorflag = True
                        break
                if errorflag:
                    stop_emulator()
                    break

                f = open("personalization.txt", "r+", encoding="utf-8")
                lines = f.readlines()
                a, b = semantic_analysis(tmp, lines)
                sorted_a = sorted(a, key=lambda x: len(x["id"]), reverse=True)
                for x in sorted_a:
                    instruction = instruction.lower().replace(x["id"], x["ID"])
                append_to_file(ID, f"Replace personalized elements:{x['id']} with {x['ID']}")
                config["instruction"] = instruction
                config["explore_switch"] = False
                append_to_file(ID, f"Precise Command Execution Phase")
                result = run(config["explore_switch"], config["instruction"], ID, config["difficulty"])
                if result:
                    chat_history = verify_all_chat(ID, instruction)
                    response, token3 = inference_chat2(chat_history, model, api_url, TOKEN)
                    print(response)
                    if "Success" in response:
                        append_to_file(ID,
                                       f"Verify personalized elements execution success\nReason:{response},Verification token consumption:{token3[2]},Personalized elements:{tmp}\n")
                        append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                        print("Verify personalized elements execution success")
                    else:
                        append_to_file(ID, f"Verify personalized elements execution failed\nReason:{response},Verification token consumption:{token3[2]}\n")
                        append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                        print("Verify personalized elements execution failed")
                else:
                    print("Precise Command Execution Phase Failed")
                restart_emulator()
                config["explore_switch"] = True
                break
            else:
                sorted_a = sorted(a, key=lambda x: len(x["id"]), reverse=True)
                for i in sorted_a:
                    instruction = instruction.lower().replace(i["id"], i["ID"])
                print(f"Information sufficient to execute:{instruction}")
                append_to_file(ID, f"Replace personalized elements:{i['id']} with {i['ID']}")
                config["instruction"] = instruction
                config["explore_switch"] = False
                append_to_file(ID, f"Precise Command Execution Phase")
                result = run(config["explore_switch"], config["instruction"], ID, config["difficulty"])
                if result:
                    chat_history = verify_all_chat(ID, instruction)
                    response, token3 = inference_chat2(chat_history, model, api_url, TOKEN)
                    print(response)
                    if "Success" in response:
                        append_to_file(ID,
                                       f"Verify personalized elements execution success\nReason:{response},Verification token consumption:{token3[2]},Personalized elements:{tmp}\n")
                        append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                        print("Verify personalized elements execution success")
                    else:
                        append_to_file(ID, f"Verify personalized elements execution failed\nReason:{response},Verification token consumption:{token3[2]}\n")
                        append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                        print("Verify personalized elements execution failed")
                else:
                    print("Precise Command Execution Phase Failed")
                restart_emulator()
                config["explore_switch"] = True
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
            append_to_file(ID, f"Precise Command Execution Phase")
            result = run(config["explore_switch"], config["instruction"], ID, config["difficulty"])
            if result:
                chat_history = verify_all_chat(ID, instruction)
                response, token3 = inference_chat2(chat_history, model, api_url, TOKEN)
                print(response)
                if "Success" in response:
                    append_to_file(ID, f"Verify personalized elements execution success\nReason:{response},Verification token consumption:{token3[2]}\n")
                    append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                    print("Verify personalized elements execution success")
                else:
                    append_to_file(ID, f"Verify personalized elements execution failed\nReason:{response},Verification token consumption:{token3[2]}\n")
                    append_to_file(ID, f"Personalized information extraction and instruction generation token consumption:{all_token}\n")
                    print("Verify personalized elements execution failed")
            else:
                print("Precise Command Execution Phase Failed")
            restart_emulator()
            config["explore_switch"] = True
            break


config = {
    "adb_path": "",
    "instruction": "",
    "difficulty": 0,
    "API_url": "",  # gpt baseurl
    "token": "",  # gpt token
    "add_info": "When you cannot open the app using open app, please try clicking the app's icon to open it.",#Add some extra information you want to provide to the large model
    "personalization_switch": True,  # Enable personalized features if tasks require personalized instructions, opening will slow down the speed
    "explore_switch": True  # Enable active exploration information feature, which is the active acquisition of personalized information
}

instruction_id = "1"
history = personalization_chat(config["instruction"], [])
while int(instruction_id) <= 75:
    try:
        config = update_config_instruction(config, "pre-instruction.json", instruction_id)
        if config["explore_switch"]:
            explore_solve(config["instruction"], config["API_url"], config["token"], "qwen-max", instruction_id)
        elif config["personalization_switch"]:
            history = personalization_chat(config["instruction"], [])
            config["instruction"] = personalization_solve(config["instruction"], history, config["deep_api_url"],
                                                          config["deep_token"])
            explore_switch = False
            run(explore_switch, config["instruction"], instruction_id, config["difficulty"])
        else:
            explore_switch = False
            start_emulator()
            time.sleep(40)
            adb_connect()
            time.sleep(5)
            adb_keyboard(config["adb_path"])
            run(explore_switch, config["instruction"], instruction_id, config["difficulty"])
            restart_emulator()
        instruction_id = str(int(instruction_id) + 1)
    except Exception as e:

        traceback.print_exc()
        print(e)
        try:
            with open(f"error-log.txt", "a", encoding="utf-8") as f:

                error_msg = traceback.format_exc()
                f.write(f"instruction_id:{instruction_id}\nerror occurred during execution:\n{error_msg}\n")

            instruction_id = str(int(instruction_id) + 1)
            config = update_config_instruction(config, "pre-instruction.json", instruction_id)
            stop_emulator()
            time.sleep(3)

        except Exception as e:

            print(e)
            traceback.print_exc()
