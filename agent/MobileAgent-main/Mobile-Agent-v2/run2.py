import os
import time
import copy
import re

import torch
import shutil
from PIL import Image, ImageDraw

from MobileAgent.api import inference_chat, append_to_file
from MobileAgent.text_localization import ocr
from MobileAgent.icon_localization import det
from MobileAgent.controller import get_screenshot, tap, slide, type, back, home
from MobileAgent.prompt import get_action_prompt, get_reflect_prompt, get_memory_prompt, get_process_prompt
from MobileAgent.chat import init_action_chat, init_reflect_chat, init_memory_chat, add_response, add_response_two_image

from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope import snapshot_download, AutoModelForCausalLM, AutoTokenizer, GenerationConfig

from dashscope import MultiModalConversation
import dashscope
import concurrent

from PerPilot.emulator import shot

####################################### Edit your Setting #########################################
# adb
adb_path = ""

# openai url
API_url = ""

# openai token
token = ""

# qwen  qwen-vl-plus" or "qwen-vl-max"
caption_model = "qwen-vl-plus"

# qwen token
qwen_api = ""

# You can add operational knowledge to help Agent operate more accurately.
add_info = "When you want to open an app, you should use the action Open app (app name).But the app name should be in Chinese .When you want to open another app, use the home operation to return to the home page first"

# Reflection Setting: If you want to improve the operating speed, you can disable the reflection agent. This may reduce the success rate.
reflection_switch = False
# Memory Setting: If you want to improve the operating speed, you can disable the memory unit. This may reduce the success rate.
memory_switch = True
###################################################################################################
caption_call_method = "api"

cache = "D:\modelscope"


def get_all_files_in_folder(folder_path):
    file_list = []
    for file_name in os.listdir(folder_path):
        file_list.append(file_name)
    return file_list


def draw_coordinates_on_image(image_path, coordinates):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    point_size = 10
    for coord in coordinates:
        draw.ellipse((coord[0] - point_size, coord[1] - point_size, coord[0] + point_size, coord[1] + point_size),
                     fill='red')
    output_image_path = './screenshot/output_image.png'
    image.save(output_image_path)
    return output_image_path


def crop(image, box, i):
    image = Image.open(image)
    x1, y1, x2, y2 = int(box[0]), int(box[1]), int(box[2]), int(box[3])
    if x1 >= x2 - 10 or y1 >= y2 - 10:
        return
    cropped_image = image.crop((x1, y1, x2, y2))
    cropped_image.save(f"./temp/{i}.jpg")


def generate_local(tokenizer, model, image_file, query):
    query = tokenizer.from_list_format([
        {'image': image_file},
        {'text': query},
    ])
    response, _ = model.chat(tokenizer, query=query, history=None)
    return response


def process_image(image, query):
    dashscope.api_key = qwen_api
    image = "file://" + image
    messages = [{
        'role': 'user',
        'content': [
            {
                'image': image
            },
            {
                'text': query
            },
        ]
    }]
    response = MultiModalConversation.call(model=caption_model, messages=messages)

    try:
        response = response['output']['choices'][0]['message']['content'][0]["text"]
    except:
        response = "This is an icon."

    return response


def generate_api(images, query):
    icon_map = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(process_image, image, query): i for i, image in enumerate(images)}

        for future in concurrent.futures.as_completed(futures):
            i = futures[future]
            response = future.result()
            icon_map[i + 1] = response

    return icon_map


def merge_text_blocks(text_list, coordinates_list):
    merged_text_blocks = []
    merged_coordinates = []

    sorted_indices = sorted(range(len(coordinates_list)),
                            key=lambda k: (coordinates_list[k][1], coordinates_list[k][0]))
    sorted_text_list = [text_list[i] for i in sorted_indices]
    sorted_coordinates_list = [coordinates_list[i] for i in sorted_indices]

    num_blocks = len(sorted_text_list)
    merge = [False] * num_blocks

    for i in range(num_blocks):
        if merge[i]:
            continue

        anchor = i

        group_text = [sorted_text_list[anchor]]
        group_coordinates = [sorted_coordinates_list[anchor]]

        for j in range(i + 1, num_blocks):
            if merge[j]:
                continue

            if abs(sorted_coordinates_list[anchor][0] - sorted_coordinates_list[j][0]) < 10 and \
                    sorted_coordinates_list[j][1] - sorted_coordinates_list[anchor][3] >= -10 and \
                    sorted_coordinates_list[j][1] - sorted_coordinates_list[anchor][3] < 30 and \
                    abs(sorted_coordinates_list[anchor][3] - sorted_coordinates_list[anchor][1] - (
                            sorted_coordinates_list[j][3] - sorted_coordinates_list[j][1])) < 10:
                group_text.append(sorted_text_list[j])
                group_coordinates.append(sorted_coordinates_list[j])
                merge[anchor] = True
                anchor = j
                merge[anchor] = True

        merged_text = "\n".join(group_text)
        min_x1 = min(group_coordinates, key=lambda x: x[0])[0]
        min_y1 = min(group_coordinates, key=lambda x: x[1])[1]
        max_x2 = max(group_coordinates, key=lambda x: x[2])[2]
        max_y2 = max(group_coordinates, key=lambda x: x[3])[3]

        merged_text_blocks.append(merged_text)
        merged_coordinates.append([min_x1, min_y1, max_x2, max_y2])

    return merged_text_blocks, merged_coordinates


def get_perception_infos(adb_path, screenshot_file):
    get_screenshot(adb_path)

    width, height = Image.open(screenshot_file).size

    text, coordinates = ocr(screenshot_file, ocr_detection, ocr_recognition)
    text, coordinates = merge_text_blocks(text, coordinates)

    perception_infos = []
    for i in range(len(coordinates)):
        perception_info = {"text": "text: " + text[i], "coordinates": coordinates[i]}
        perception_infos.append(perception_info)

    coordinates = det(screenshot_file, "icon", groundingdino_model)

    for i in range(len(coordinates)):
        perception_info = {"text": "icon", "coordinates": coordinates[i]}
        perception_infos.append(perception_info)

    return perception_infos, width, height


### Load caption model ###
device = "cuda"
torch.manual_seed(1234)

### Load ocr and icon detection model ###
groundingdino_dir = snapshot_download('AI-ModelScope/GroundingDINO', revision='v1.0.0', cache_dir=cache)
groundingdino_model = pipeline('grounding-dino-task', model=groundingdino_dir)

ocr_det_dir = snapshot_download('damo/cv_resnet18_ocr-detection-line-level_damo', cache_dir=cache)
ocr_re_cog_dir = snapshot_download('damo/cv_convnextTiny_ocr-recognition-document_damo', cache_dir=cache)

ocr_detection = pipeline(Tasks.ocr_detection, model=ocr_det_dir)
ocr_recognition = pipeline(Tasks.ocr_recognition, model=ocr_re_cog_dir)
temp_file = "./temp"
screenshot = "./screenshot"


def run(explore_switch, instruction, id, difficulty):
    alltoken = 0
    thought_history = []
    summary_history = []
    action_history = []
    summary = ""
    action = ""
    completed_requirements = ""
    memory = ""
    insight = ""
    if not os.path.exists(temp_file):
        os.mkdir(temp_file)
    else:
        shutil.rmtree(temp_file)
        os.mkdir(temp_file)
    if not os.path.exists(screenshot):
        os.mkdir(screenshot)
    error_flag = False

    iter = 0
    # 定义开始时间和步骤数
    start_time = time.time()
    allsteps = 0
    while True:
        iter += 1
        if not explore_switch:
            shot(adb_path, id, allsteps)
        if iter == 1:
            screenshot_file = "./screenshot/screenshot.jpg"
            perception_infos, width, height = get_perception_infos(adb_path, screenshot_file)
            shutil.rmtree(temp_file)
            os.mkdir(temp_file)

            keyboard = False
            keyboard_height_limit = 0.9 * height
            for perception_info in perception_infos:
                if perception_info['coordinates'][1] < keyboard_height_limit:
                    continue
                if 'ADB Keyboard' in perception_info['text']:
                    keyboard = True
                    break
        prompt_action = get_action_prompt(instruction, perception_infos, width, height, keyboard, summary_history,
                                          action_history, summary, action, add_info, error_flag, completed_requirements,
                                          memory, explore_switch)
        chat_action = init_action_chat()
        chat_action = add_response("user", prompt_action, chat_action, screenshot_file)

        output_action, token1 = inference_chat(chat_action, 'o4-mini', API_url, token)
        alltoken += token1[2]
        thought = output_action.split("### Thought ###")[-1].split("### Action ###")[0].replace("\n", " ").replace(":",
                                                                                                                   "").replace(
            "  ", " ").strip()
        summary = output_action.split("### Operation ###")[-1].replace("\n", " ").replace("  ", " ").strip()
        action = output_action.split("### Action ###")[-1].split("### Operation ###")[0].replace("\n", " ").replace(
            "  ",
            " ").strip()
        chat_action = add_response("assistant", output_action, chat_action)
        status = "#" * 50 + " Decision " + "#" * 50
        print(status)
        print(output_action)
        print('#' * len(status))

        if memory_switch:
            prompt_memory = get_memory_prompt(insight)
            chat_action = add_response("user", prompt_memory, chat_action)
            output_memory, token2 = inference_chat(chat_action, 'o4-mini', API_url, token)
            alltoken += token2[2]
            chat_action = add_response("assistant", output_memory, chat_action)
            status = "#" * 50 + " Memory " + "#" * 50
            print(status)
            print(output_memory)
            print('#' * len(status))
            output_memory = output_memory.split("### Important content ###")[-1].split("\n\n")[0].strip() + "\n"
            if "None" not in output_memory and output_memory not in memory:
                memory += output_memory
        if "Type" in action:
            print("")
        else:
            action = action.replace(" ", "")
        if "Tap" in action:
            coordinate = action.split("(")[-1].split(")")[0].split(",")
            x, y = int(coordinate[0]), int(coordinate[1])
            tap(adb_path, x, y)

        elif "Openapp" in action:
            app_name = action.split("(")[-1].split(")")[0]
            text, coordinate = ocr(screenshot_file, ocr_detection, ocr_recognition)
            tap_coordinate = [0, 0]
            for ti in range(len(text)):
                if app_name == text[ti]:
                    name_coordinate = [int((coordinate[ti][0] + coordinate[ti][2]) / 2),
                                       int((coordinate[ti][1] + coordinate[ti][3]) / 2)]
                    tap(adb_path, name_coordinate[0],
                        name_coordinate[1] - int(coordinate[ti][3] - coordinate[ti][1]))  #
                    break

        elif "Swipe" in action:
            print(action)
            pattern = r'Swipe\((\d+),(\d+)\),\((\d+),(\d+)\)'
            match = re.fullmatch(pattern, action)
            x1, y1, x2, y2 = map(int, match.groups())
            slide(adb_path, x1, y1, x2, y2)

        elif "Type" in action:
            start = action.find('(')
            end = action.rfind(')')


            if start != -1 and end != -1 and start < end:
                text = action[start + 1:end]
            if "(text)" not in action:
                text = text
            else:
                text = action.split("\"")[-1].split("\"")[0]
            type(adb_path, text)

        elif "Back" in action:
            back(adb_path)

        elif "Home" in action:
            home(adb_path)

        elif "Stop" in action:
            if explore_switch:
                print(f"find{action.split('|')[-1]}\n")
                return action.split('|')[-1]
            else:
                return 1
        if not explore_switch:
            if difficulty == 1:
                if allsteps > 25:
                    append_to_file(id, f"instruction failed")
                    return False
            elif difficulty == 2:
                if allsteps > 35:
                    append_to_file(id, f"instruction failed")
                    return False
            elif difficulty == 3:
                if allsteps > 40:
                    append_to_file(id, f"instruction failed")
                    return False
        if explore_switch == True and allsteps > 15:
            print("无法找到对应信息\n")
            return 0
        time.sleep(10)
        allsteps += 1
        end_time = time.time()
        print(f"{allsteps}step,spent time{round(end_time - start_time)}seconds")
        append_to_file(id, f"{allsteps}step,output action is{summary},spent time{round(end_time - start_time)}seconds,total token consumption{alltoken}")
        last_perception_infos = copy.deepcopy(perception_infos)
        last_screenshot_file = "./screenshot/last_screenshot.jpg"
        last_keyboard = keyboard
        if os.path.exists(last_screenshot_file):
            os.remove(last_screenshot_file)
        os.rename(screenshot_file, last_screenshot_file)

        perception_infos, width, height = get_perception_infos(adb_path, screenshot_file)
        shutil.rmtree(temp_file)
        os.mkdir(temp_file)

        keyboard = False
        for perception_info in perception_infos:
            if perception_info['coordinates'][1] < keyboard_height_limit:
                continue
            if 'ADB Keyboard' in perception_info['text']:
                keyboard = True
                break

        if reflection_switch:
            prompt_reflect = get_reflect_prompt(instruction, last_perception_infos, perception_infos, width, height,
                                                last_keyboard, keyboard, summary, action, add_info)
            chat_reflect = init_reflect_chat()
            chat_reflect = add_response_two_image("user", prompt_reflect, chat_reflect,
                                                  [last_screenshot_file, screenshot_file])

            output_reflect, token3 = inference_chat(chat_reflect, 'o4-mini', API_url, token)
            alltoken += token3[2]
            reflect = output_reflect.split("### Answer ###")[-1].replace("\n", " ").strip()
            chat_reflect = add_response("assistant", output_reflect, chat_reflect)
            status = "#" * 50 + " Reflcetion " + "#" * 50
            print(status)
            print(output_reflect)
            print('#' * len(status))

            if 'A' in reflect:
                thought_history.append(thought)
                summary_history.append(summary)
                action_history.append(action)

                prompt_planning = get_process_prompt(instruction, thought_history, summary_history, action_history,
                                                     completed_requirements, add_info)
                chat_planning = init_memory_chat()
                chat_planning = add_response("user", prompt_planning, chat_planning)
                output_planning, token4 = inference_chat(chat_planning, 'o4-mini', API_url, token)
                alltoken += token4[2]
                chat_planning = add_response("assistant", output_planning, chat_planning)
                status = "#" * 50 + " Planning " + "#" * 50
                print(status)
                print(output_planning)
                print('#' * len(status))
                completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n",
                                                                                                         " ").strip()

                error_flag = False

            elif 'B' in reflect:
                error_flag = True
                back(adb_path)

            elif 'C' in reflect:
                error_flag = True

        else:
            thought_history.append(thought)
            summary_history.append(summary)
            action_history.append(action)

            prompt_planning = get_process_prompt(instruction, thought_history, summary_history, action_history,
                                                 completed_requirements, add_info)
            chat_planning = init_memory_chat()
            chat_planning = add_response("user", prompt_planning, chat_planning)
            output_planning, token5 = inference_chat(chat_planning, 'o4-mini', API_url, token)
            alltoken += token5[2]
            chat_planning = add_response("assistant", output_planning, chat_planning)
            status = "#" * 50 + " Planning " + "#" * 50
            print(status)
            print(output_planning)
            print('#' * len(status))
            completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n", " ").strip()

        os.remove(last_screenshot_file)
