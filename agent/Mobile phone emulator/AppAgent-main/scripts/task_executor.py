import argparse
import ast
import datetime
import json
import os
import re
import subprocess
import sys
import time

import prompts
from config import load_config
from and_controller import list_all_devices, AndroidController, traverse_tree
from emulator import shot
from model import parse_explore_rsp, parse_grid_rsp, OpenAIModel, QwenModel
from utils import print_with_color, draw_bbox_multi, draw_grid
from api import append_to_file

adb_path = "C:\platform-tools\\adb.exe"


def home(adb_path):
    command = adb_path + f" -s 127.0.0.1:5557 shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)


arg_desc = "AppAgent Executor"
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=arg_desc)
parser.add_argument("--app")
parser.add_argument("--root_dir", default="./")
args = vars(parser.parse_args())

configs = load_config()

if configs["MODEL"] == "OpenAI":
    mllm = OpenAIModel(base_url=configs["OPENAI_API_BASE"],
                       api_key=configs["OPENAI_API_KEY"],
                       model=configs["OPENAI_API_MODEL"],
                       temperature=configs["TEMPERATURE"],
                       max_tokens=configs["MAX_TOKENS"])
elif configs["MODEL"] == "Qwen":
    mllm = QwenModel(api_key=configs["DASHSCOPE_API_KEY"],
                     model=configs["QWEN_MODEL"])
else:
    print_with_color(f"ERROR: Unsupported model type {configs['MODEL']}!", "red")
    sys.exit()

x1 = 0
y1 = 0


def run(explore_switch, task, id, difficulty):
    global elem_list
    app = "qq"
    root_dir = "D:\\appagent\\appagent\AppAgent-main"
    alltokens = 0

    if not app:
        print_with_color("What is the name of the app you want me to operate?", "blue")
        app = input()
        app = app.replace(" ", "")

    app_dir = os.path.join(os.path.join(root_dir, "apps"), app)
    work_dir = os.path.join(root_dir, "tasks")
    if not os.path.exists(work_dir):
        os.mkdir(work_dir)
    auto_docs_dir = os.path.join(app_dir, "auto_docs")
    demo_docs_dir = os.path.join(app_dir, "demo_docs")
    task_timestamp = int(time.time())
    dir_name = datetime.datetime.fromtimestamp(task_timestamp).strftime(f"task_{app}_%Y-%m-%d_%H-%M-%S")
    task_dir = os.path.join(work_dir, dir_name)
    os.mkdir(task_dir)
    log_path = os.path.join(task_dir, f"log_{app}_{dir_name}.txt")

    no_doc = False
    if not os.path.exists(auto_docs_dir) and not os.path.exists(demo_docs_dir):
        print_with_color(
            f"No documentations found for the app {app}. Do you want to proceed with no docs? Enter y or n",
            "red")
        user_input = ""
        while user_input != "y" and user_input != "n":
            user_input = "y"
        if user_input == "y":
            no_doc = True
        else:
            sys.exit()
    elif os.path.exists(auto_docs_dir) and os.path.exists(demo_docs_dir):
        print_with_color(f"The app {app} has documentations generated from both autonomous exploration and human "
                         f"demonstration. Which one do you want to use? Type 1 or 2.\n1. Autonomous exploration\n2. Human "
                         f"Demonstration",
                         "blue")
        user_input = ""
        while user_input != "1" and user_input != "2":
            user_input = input()
        if user_input == "1":
            docs_dir = auto_docs_dir
        else:
            docs_dir = demo_docs_dir
    elif os.path.exists(auto_docs_dir):
        print_with_color(
            f"Documentations generated from autonomous exploration were found for the app {app}. The doc base "
            f"is selected automatically.", "yellow")
        docs_dir = auto_docs_dir
    else:
        print_with_color(
            f"Documentations generated from human demonstration were found for the app {app}. The doc base is "
            f"selected automatically.", "yellow")
        docs_dir = demo_docs_dir
    """
    device_list = list_all_devices()
    if not device_list:
        print_with_color("ERROR: No device found!", "red")
        sys.exit()
    print_with_color(f"List of devices attached:\n{str(device_list)}", "yellow")
    if len(device_list) == 1:
        device = device_list[0]
        print_with_color(f"Device selected: {device}", "yellow")
    else:
        print_with_color("Please choose the Android device to start demo by entering its ID:", "blue")
        device = input()
    """
    device = "127.0.0.1:5557"
    controller = AndroidController(device)
    width, height = controller.get_device_size()
    if not width and not height:
        print_with_color("ERROR: Invalid device size!", "red")
        sys.exit()
    print_with_color(f"Screen resolution of {device}: {width}x{height}", "yellow")

    print_with_color("Please enter the description of the task you want me to complete in a few sentences:", "blue")
    task_desc = task

    round_count = 0
    last_act = "None"
    task_complete = False
    grid_on = False
    rows, cols = 0, 0

    def area_to_xy(area, subarea):
        area -= 1
        row, col = area // cols, area % cols
        x_0, y_0 = col * (width // cols), row * (height // rows)
        if subarea == "top-left":
            x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 4
        elif subarea == "top":
            x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 4
        elif subarea == "top-right":
            x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 4
        elif subarea == "left":
            x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) // 2
        elif subarea == "right":
            x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) // 2
        elif subarea == "bottom-left":
            x, y = x_0 + (width // cols) // 4, y_0 + (height // rows) * 3 // 4
        elif subarea == "bottom":
            x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) * 3 // 4
        elif subarea == "bottom-right":
            x, y = x_0 + (width // cols) * 3 // 4, y_0 + (height // rows) * 3 // 4
        else:
            x, y = x_0 + (width // cols) // 2, y_0 + (height // rows) // 2
        return x, y

    act_name = ""
    res = ""
    start_time = time.time()
    while round_count < configs["MAX_ROUNDS"]:
        round_count += 1
        allsteps = round_count - 1
        end_time = time.time()
        if allsteps != 0:
            print_with_color(f"{allsteps}steps，cost time{round(end_time - start_time)}秒,token{alltokens}",
                             "yellow")
            append_to_file(id,
                           f"{allsteps}steps,act{res},cost time{round(end_time - start_time)}秒,token{alltokens}")
            if explore_switch == True and allsteps > 15:
                return False
            if not explore_switch:
                if difficulty == 1:
                    if allsteps > 25:
                        append_to_file(id, f"failed")
                        return False
                elif difficulty == 2:
                    if allsteps > 35:
                        append_to_file(id, f"failed")
                        return False
                elif difficulty == 3:
                    if allsteps > 40:
                        append_to_file(id, f"failed")
                        return False

        print_with_color(f"Round {round_count}", "yellow")
        for i in range(3):
            try:
                screenshot_path = controller.get_screenshot(f"{dir_name}_{round_count}", task_dir)
                if not explore_switch:
                    shot(adb_path, id, allsteps)
                xml_path = controller.get_xml(f"{dir_name}_{round_count}", task_dir)
                break
            except Exception as e:
                print(f"xml,wrong{e}")
                time.sleep(2)
                continue

        if screenshot_path == "ERROR" or xml_path == "ERROR":
            append_to_file(id, f"failed,stop,text{screenshot_path}or{xml_path}")
            break
        if grid_on:
            rows, cols = draw_grid(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png"))
            image = os.path.join(task_dir, f"{dir_name}_{round_count}_grid.png")
            prompt = prompts.task_template_grid
        else:
            clickable_list = []
            focusable_list = []
            traverse_tree(xml_path, clickable_list, "clickable", True)
            traverse_tree(xml_path, focusable_list, "focusable", True)
            elem_list = clickable_list.copy()
            for elem in focusable_list:
                bbox = elem.bbox
                center = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                close = False
                for e in clickable_list:
                    bbox = e.bbox
                    center_ = (bbox[0][0] + bbox[1][0]) // 2, (bbox[0][1] + bbox[1][1]) // 2
                    dist = (abs(center[0] - center_[0]) ** 2 + abs(center[1] - center_[1]) ** 2) ** 0.5
                    if dist <= configs["MIN_DIST"]:
                        close = True
                        break
                if not close:
                    elem_list.append(elem)
            draw_bbox_multi(screenshot_path, os.path.join(task_dir, f"{dir_name}_{round_count}_labeled.png"), elem_list,
                            dark_mode=configs["DARK_MODE"])
            image = os.path.join(task_dir, f"{dir_name}_{round_count}_labeled.png")
            if no_doc:
                prompt = re.sub(r"<ui_document>", "", prompts.task_template(explore_switch))
                if explore_switch:
                    prompt += prompts.explore_prompt(task_desc)
            else:
                ui_doc = ""
                for i, elem in enumerate(elem_list):
                    doc_path = os.path.join(docs_dir, f"{elem.uid}.txt")
                    if not os.path.exists(doc_path):
                        continue
                    ui_doc += f"Documentation of UI element labeled with the numeric tag '{i + 1}':\n"
                    doc_content = ast.literal_eval(open(doc_path, "r").read())
                    if doc_content["tap"]:
                        ui_doc += f"This UI element is clickable. {doc_content['tap']}\n\n"
                    if doc_content["text"]:
                        ui_doc += f"This UI element can receive text input. The text input is used for the following " \
                                  f"purposes: {doc_content['text']}\n\n"
                    if doc_content["long_press"]:
                        ui_doc += f"This UI element is long clickable. {doc_content['long_press']}\n\n"
                    if doc_content["v_swipe"]:
                        ui_doc += f"This element can be swiped directly without tapping. You can swipe vertically on " \
                                  f"this UI element. {doc_content['v_swipe']}\n\n"
                    if doc_content["h_swipe"]:
                        ui_doc += f"This element can be swiped directly without tapping. You can swipe horizontally on " \
                                  f"this UI element. {doc_content['h_swipe']}\n\n"
                print_with_color(f"Documentations retrieved for the current interface:\n{ui_doc}", "magenta")
                ui_doc = """
                You also have access to the following documentations that describes the functionalities of UI 
                elements you can interact on the screen. These docs are crucial for you to determine the target of your 
                next action. You should always prioritize these documented elements for interaction:""" + ui_doc
                prompt = re.sub(r"<ui_document>", ui_doc, prompts.task_template(explore_switch))
        prompt = re.sub(r"<task_description>", task_desc, prompt)
        prompt = re.sub(r"<last_act>", last_act, prompt)
        print_with_color("Thinking about what to do in the next step...", "yellow")
        for i in range(3):
            try:
                status, rsp, token_usage = mllm.get_model_response(prompt, [image])
                alltokens += token_usage[2]
                if status:
                    with open(log_path, "a") as logfile:
                        log_item = {"step": round_count, "prompt": prompt,
                                    "image": f"{dir_name}_{round_count}_labeled.png",
                                    "response": rsp}
                        logfile.write(json.dumps(log_item) + "\n")
                    if grid_on:
                        res = parse_grid_rsp(rsp)
                    else:
                        res = parse_explore_rsp(rsp)
                    act_name = res[0]
                    if "FINISH" in act_name:
                        task_complete = True
                        if explore_switch:
                            return res[0].split("|")[-1]
                        else:
                            return True
                    if act_name == "ERROR":
                        append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                        break
                    last_act = res[-1]
                    res = res[:-1]
                    if act_name == "tap":
                        _, area = res
                        tl, br = elem_list[area - 1].bbox
                        x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
                        ret = controller.tap(x, y)
                        if round_count == 1:
                            x1 = x
                            y1 = y
                        if ret == "ERROR":
                            print_with_color("ERROR: tap execution failed", "red")
                            append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                            break
                    elif act_name == "text":
                        _, input_str = res
                        ret = controller.text(input_str)
                        if ret == "ERROR":
                            print_with_color("ERROR: text execution failed", "red")
                            append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                            break
                    elif act_name == "long_press":
                        _, area = res
                        tl, br = elem_list[area - 1].bbox
                        x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
                        ret = controller.long_press(x, y)
                        if ret == "ERROR":
                            print_with_color("ERROR: long press execution failed", "red")
                            append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                            break
                    elif act_name == "swipe":
                        _, area, swipe_dir, dist = res
                        tl, br = elem_list[area - 1].bbox
                        x, y = (tl[0] + br[0]) // 2, (tl[1] + br[1]) // 2
                        ret = controller.swipe(x, y, swipe_dir, dist)
                        if ret == "ERROR":
                            print_with_color("ERROR: swipe execution failed", "red")
                            append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                            break
                    elif act_name == "grid":
                        grid_on = True
                    elif act_name == "tap_grid" or act_name == "long_press_grid":
                        _, area, subarea = res
                        x, y = area_to_xy(area, subarea)
                        if act_name == "tap_grid":
                            ret = controller.tap(x, y)
                            if ret == "ERROR":
                                print_with_color("ERROR: tap execution failed", "red")
                                append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                                break
                        else:
                            ret = controller.long_press(x, y)
                            if ret == "ERROR":
                                print_with_color("ERROR: tap execution failed", "red")
                                append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                                break
                    elif act_name == "swipe_grid":
                        _, start_area, start_subarea, end_area, end_subarea = res
                        start_x, start_y = area_to_xy(start_area, start_subarea)
                        end_x, end_y = area_to_xy(end_area, end_subarea)
                        ret = controller.swipe_precise((start_x, start_y), (end_x, end_y))
                        if ret == "ERROR":
                            print_with_color("ERROR: tap execution failed", "red")
                            append_to_file(id, f"failed,stop,text{res[0].split('|')[-1]}")
                            break
                    if act_name != "grid":
                        grid_on = False
                    time.sleep(configs["REQUEST_INTERVAL"])
                    if round_count == 1:
                        time.sleep(5)
                        #controller.tap(x1, y1)
                        #time.sleep(5)
                else:
                    print_with_color(rsp, "red")
                    append_to_file(id, f"failed,stop,text{rsp}")
                    break
                break
            except Exception as e:
                print_with_color(f"Task finished unexpectedly due to error: {e}", "red")
                continue

    if task_complete:
        print_with_color("Task completed successfully", "yellow")
    elif round_count == configs["MAX_ROUNDS"]:
        print_with_color("Task finished due to reaching max rounds", "yellow")
    else:
        print_with_color("Task finished unexpectedly", "red")
