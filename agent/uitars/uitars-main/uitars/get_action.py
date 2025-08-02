import re
from uitars.controller import long_press, tap, slide, type, back, home
from openai import OpenAI
from uitars.prompt import solve_action_prompt
from uitars.api import encode_image
from PIL import Image


def extract_coordinates(action, image_width=1084, image_high=2412):
    coordinates = re.findall(r'\((\d+),\s*(\d+)\)', action)
    result = []
    if coordinates:
        for x_str, y_str in coordinates:
            x = int(x_str)

            x = x * image_width / 1000
            y = int(y_str)
            y = y * image_high / 1000
            result.append((x, y))
    return result


def get_response(instruction, screenshot_path):
    encoded_string = encode_image(screenshot_path)
    client = OpenAI(
        base_url="",
        api_key="empty",
    )

    response = client.chat.completions.create(
        model="ui_tars",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": solve_action_prompt() + instruction},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encoded_string}"}},
                ],
            },
        ],
        frequency_penalty=1,
        max_tokens=2048,
    )
    return response


def get_action(adb_path, instruction, screenshot_path, id):
    response = get_response(instruction, screenshot_path)
    index = response.choices[0].message.content.rfind("Action: ")
    if index != -1:
        action = response.choices[0].message.content[index + 8:]
    else:
        action = response.choices[0].message
    print(f"\naction:{action}")

    width, height = Image.open(screenshot_path).size
    if "Stop" in instruction:
        return 0
    elif "home" == instruction:
        home(adb_path)
        return 1
    elif "back" == instruction:
        back(adb_path)
        return 1
    elif "type" in instruction:
        try:
            pattern = r"content=['\"](.*?)['\"]"
            matches = re.findall(pattern, instruction)
            type(adb_path, matches[0])
        except:
            pattern = r"\"(.*?)\""
            matches = re.findall(pattern, instruction)
            type(adb_path, matches[0])
        return 1
    elif "long_press" in action:
        coordinate = extract_coordinates(action, width, height)
        x, y = coordinate[0]
        long_press(adb_path, x, y)
    elif "scroll" in action:
        coordinate = extract_coordinates(action, width, height)
        x1, y1 = coordinate[0]
        x2, y2 = coordinate[1]
        slide(adb_path, x1, y1, x2, y2)
    elif "click" in action:
        coordinate = extract_coordinates(action, width, height)
        x, y = coordinate[0]
        tap(adb_path, x, y)
    return 1
