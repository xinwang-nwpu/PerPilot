import subprocess
import time

import easyocr
from PIL import Image
import os


def adb_connect():
    command = "adb connect 127.0.0.1:5557"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def start_emulator():
    command = "MuMuManager.exe control -v 1 launch"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def stop_emulator():
    command = "MuMuManager.exe control -v 1 shutdown"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def delete_emulator():
    command = "MuMuManager.exe delete -v 1"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def backup_emulator():
    command = "MuMuManager.exe export -v 0 -d E:\\backup -n test"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def restore_emulator():
    command = "MuMuManager.exe import -p E:\\backup\\test.mumudata"
    subprocess.run(command, capture_output=True, text=True, shell=True)


def adb_start():
    command = "MuMuManager.exe control -v 1 app launch -pkg com.android.settings"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(10)
    command = "adb -s 127.0.0.1:5557 shell input swipe 100 1500 100 0"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input swipe 100 1500 100 0"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input tap 600 1500"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input tap 500 500"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input tap 500 900"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(5)
    command = "adb -s 127.0.0.1:5557 shell input tap 600 900"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input tap 600 800"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)
    command = "adb -s 127.0.0.1:5557 shell input tap 150 200"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(2)


def shot(adb_path, id, step):

    folder_path = f"./newshot/{id}"
    os.makedirs(folder_path, exist_ok=True)

    final_image_path = f"{folder_path}/{step}.png"

    try:

        adb_commands = (
            f'"{adb_path}" -s 127.0.0.1:5557 shell '
            f'rm /sdcard/screenshot.png; ' 
            f'screencap -p /sdcard/screenshot.png'
        )


        subprocess.run(adb_commands, capture_output=True, text=True, shell=True, check=True)


        pull_command = f'"{adb_path}" -s 127.0.0.1:5557 pull /sdcard/screenshot.png "{final_image_path}"'
        subprocess.run(pull_command, capture_output=True, text=True, shell=True, check=True)


        with Image.open(final_image_path) as img:
            img.verify()

        return final_image_path

    except subprocess.CalledProcessError as e:
        print(f"ADB命令执行错误: {e.stderr}")
        return None
    except Exception as e:
        print(f"截图处理错误: {str(e)}")
        return None


def restart_emulator():
    stop_emulator()
    time.sleep(3)
    delete_emulator()
    time.sleep(10)
    restore_emulator()
    time.sleep(40)


def adb_keyboard(adb_path, local_save_path="./temp_screenshot.png"):
    for i in range(3):
        adb_start()
        result = pull_screenshot_and_ocr(adb_path, local_save_path)
        command = "MuMuManager.exe control -v 1 app close -pkg com.android.settings"
        subprocess.run(command, capture_output=True, text=True, shell=True)
        time.sleep(2)
        if '英语(美国)' in result or 'SogoulME-chuizi' in result:
            print(f"open keyboard failed {i+1} times")
            continue
        elif 'ADB Keyboard' not in result:
            print(f"open keyboard failed {i+1} times")
            continue
        else:
            os.remove(local_save_path)
            print("open keyboard success")
            break


def pull_screenshot_and_ocr(adb_path, local_save_path=None):
    try:

        if local_save_path is None:
            local_save_path = "./temp_screenshot.png"


        os.makedirs(os.path.dirname(os.path.abspath(local_save_path)), exist_ok=True)


        device_screenshot_path = "/sdcard/screenshot_temp.png"
        screencap_command = f'"{adb_path}" -s 127.0.0.1:5557 shell screencap -p {device_screenshot_path}'
        result = subprocess.run(screencap_command, capture_output=True, text=True, shell=True, check=True)


        pull_command = f'"{adb_path}" -s 127.0.0.1:5557 pull {device_screenshot_path} "{local_save_path}"'
        subprocess.run(pull_command, capture_output=True, text=True, shell=True, check=True)


        if not os.path.exists(local_save_path):
            print("pull screenshot failed")
            return False, None

        reader = easyocr.Reader(['ch_sim', 'en'])
        result = reader.readtext(local_save_path, detail=0)


        rm_device_command = f'"{adb_path}" -s 127.0.0.1:5557 shell rm {device_screenshot_path}'
        subprocess.run(rm_device_command, capture_output=True, text=True, shell=True, check=True)



        return result

    except subprocess.CalledProcessError as e:
        print(f"ADB falied: {e.stderr}")
        return False, None
    except Exception as e:
        print(f"handle screenshot error: {str(e)}")
        return False, None


