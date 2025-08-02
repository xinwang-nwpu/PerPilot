import os
import time
import shutil
from PIL import Image
from uitars.api import inference_chat
from uitars.controller import get_screenshot
from uitars.prompt import get_action_prompt, get_process_prompt
from uitars.chat import init_action_chat, add_response, init_memory_chat
from uitars.get_action import get_action


class XAgent:
    def __init__(self, config):
        # 初始化配置
        self.height = None
        self.width = None
        self.thought = None
        self.perception_infos = None
        self.screenshot_file = None
        self.adb_path = config.get("adb_path", "")
        self.instruction = config.get("instruction", "")
        self.API_url = config.get("API_url", "")
        self.token = config.get("token", "")
        self.add_info = config.get("add_info", " ")
        self.personalization_switch = config.get("personalization_switch", )
        self.explore_switch = config.get("explore_switch", )
        self.difficulty = config.get("difficulty", "")

        self.temp_file = "temp"
        self.screenshot = "screenshot"
        self._initialize_workspace()

        self.thought_history = []
        self.summary_history = []
        self.action_history = []
        self.summary = ""
        self.action = ""
        self.completed_requirements = ""
        self.memory = ""
        self.insight = ""
        self.error_flag = False
        self.iter = 0
        self.keyboard_height_limit = 0

    def _initialize_workspace(self):
        if not os.path.exists(self.temp_file):
            os.mkdir(self.temp_file)
        else:
            shutil.rmtree(self.temp_file)
            os.mkdir(self.temp_file)

        if not os.path.exists(self.screenshot):
            os.mkdir(self.screenshot)

    @staticmethod
    def get_all_files_in_folder(folder_path):
        file_list = []
        for file_name in os.listdir(folder_path):
            file_list.append(file_name)
        return file_list

    def get_perception_infos(self, screenshot_file):
        get_screenshot(self.adb_path)

        width, height = Image.open(screenshot_file).size
        self.keyboard_height_limit = 0.9 * height

        perception_infos = []

        return perception_infos, width, height

    def run(self, id):
        start_time = time.time()
        all_steps = 0
        while True:
            self.iter += 1
            if self.iter == 1:
                self.screenshot_file = "./screenshot/screenshot.jpg"
                self.perception_infos, self.width, self.height = self.get_perception_infos(self.screenshot_file)
                shutil.rmtree(self.temp_file)
                os.mkdir(self.temp_file)

            prompt_action = get_action_prompt(
                self.instruction, self.perception_infos, self.width, self.height,
                self.summary_history, self.action_history,
                self.summary, self.action, self.add_info, self.error_flag,
                self.completed_requirements, self.memory, self.explore_switch
            )

            chat_action = init_action_chat()
            chat_action = add_response("user", prompt_action, chat_action, self.screenshot_file)
            output_action = inference_chat(chat_action, 'o4-mini', self.API_url, self.token)

            self.thought = output_action.split("### Thought ###")[-1].split("### Action ###")[0].replace("\n",
                                                                                                         " ").replace(
                ":", "").replace("  ", " ").strip()
            self.action = output_action.split("### Action ###")[-1].replace("\n", " ").replace("  ", " ").strip()
            self.summary = self.thought

            chat_action = add_response("assistant", output_action, chat_action)
            time2 = time.time()

            status = "-" * 50 + " decision" + "-" * 50
            print(status)
            print(output_action)
            end_time = time.time()
            all_steps += 1
            should_continue = get_action(self.adb_path, self.action, self.screenshot_file, id)
            if all_steps == 1:
                time.sleep(8)
            else:
                time.sleep(3)
            if not should_continue and self.explore_switch == True:
                print(f"find{self.action.split('|')[-1]}\n")
                return self.action.split('|')[-1]
            if self.explore_switch == True and all_steps > 15:
                return False
            if not self.explore_switch:
                if self.difficulty == 1:
                    if all_steps > 15:
                        return False
                elif self.difficulty == 2:
                    if all_steps > 25:
                        return False
                elif self.difficulty == 3:
                    if all_steps > 35:
                        return False
            if not should_continue:
                return True
            print(f"{all_steps}action，cost time{round(end_time - start_time)}seconds")
            last_screenshot_file = "./screenshot/last_screenshot.jpg"

            if os.path.exists(last_screenshot_file):
                os.remove(last_screenshot_file)
            os.rename(self.screenshot_file, last_screenshot_file)

            self.perception_infos, self.width, self.height = self.get_perception_infos(self.screenshot_file)
            shutil.rmtree(self.temp_file)
            os.mkdir(self.temp_file)

            self.thought_history.append(self.thought)
            self.summary_history.append(self.summary)
            self.action_history.append(self.action)

            prompt_planning = get_process_prompt(
                self.instruction, self.thought_history, self.summary_history,
                self.action_history, self.completed_requirements, self.add_info
            )

            chat_planning = init_memory_chat()
            chat_planning = add_response("user", prompt_planning, chat_planning)
            output_planning = inference_chat(chat_planning, 'o4-mini', self.API_url, self.deep_token)
            chat_planning = add_response("assistant", output_planning, chat_planning)

            status = "-" * 50 + " planning " + "-" * 50
            print(status)
            print(output_planning)

            self.completed_requirements = output_planning.split("### Completed contents ###")[-1].replace("\n",
                                                                                                          " ").strip()

            os.remove(last_screenshot_file)
