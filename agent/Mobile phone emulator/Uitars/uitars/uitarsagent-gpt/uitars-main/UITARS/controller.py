import os
import string
import subprocess
import time

from PIL import Image


def get_screenshot(adb_path):
    command = adb_path + " -s 127.0.0.1:5557 shell rm /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = adb_path + " -s 127.0.0.1:5557 shell screencap -p /sdcard/screenshot.png"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    time.sleep(0.5)
    command = adb_path + " -s 127.0.0.1:5557 pull /sdcard/screenshot.png ./screenshot"
    subprocess.run(command, capture_output=True, text=True, shell=True)
    image_path = "./screenshot/screenshot.png"
    save_path = "./screenshot/screenshot.jpg"
    image = Image.open(image_path)
    image.convert("RGB").save(save_path, "JPEG")
    os.remove(image_path)



def tap(adb_path, x, y):
    command = adb_path + f" -s 127.0.0.1:5557 shell input tap {x} {y}"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def type(adb_path, text):
    text = text.replace('\n', '_')
    ordinary = set("-.,!?@'°/:;()").union(string.ascii_letters, string.digits)
    buffer = []

    def send(cmd, args=None):
        subprocess.run([adb_path, '-s', '127.0.0.1:5557', 'shell'] + cmd + [args] if args else [adb_path, '-s', '127.0.0.1:5557', 'shell'] + cmd,
                       check=True, capture_output=True)

    for char in text:
        if char == '_':
            if buffer:
                send(['input', 'text', ''.join(buffer).replace(' ', '%s')])
                buffer.clear()
            send(['input', 'keyevent', '代码.txt'])
        elif char == ' ':
            buffer.append('%s')
        elif char in ordinary:
            buffer.append(f"\'{char}\'")
        else:
            if buffer:
                send(['input', 'text', ''.join(buffer).replace(' ', '%s')])
                buffer.clear()
            send(['am', 'broadcast', '-a', 'ADB_INPUT_TEXT', '--es', 'msg', char])

    if buffer:
        send(['input', 'text', ''.join(buffer).replace(' ', '%s')])


def slide(adb_path, x1, y1, x2, y2):
    command = adb_path + f" -s 127.0.0.1:5557 shell input swipe {x1} {y1} {x2} {y2} 500"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def long_press(adb_path, x, y):
    command = adb_path + f" -s 127.0.0.1:5557 shell input swipe {x} {y} {x} {y} 1000"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def back(adb_path):
    command = adb_path + f" -s 127.0.0.1:5557 shell input keyevent 4"
    subprocess.run(command, capture_output=True, text=True, shell=True)



def home(adb_path):
    command = adb_path + f" -s 127.0.0.1:5557 shell am start -a android.intent.action.MAIN -c android.intent.category.HOME"
    subprocess.run(command, capture_output=True, text=True, shell=True)

