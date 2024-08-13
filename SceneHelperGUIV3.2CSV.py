import sys
import logging
import time
import re
import csv
import tkinter as tk
from tkinter import messagebox
from tkinter import PhotoImage
from tkinter import ttk  
from datetime import datetime
from obswebsocket import obsws, requests

print("欢迎使用数字场记板制片版！\n作者：@巧克力蛋包饭\n您现在所使用的版本是V3.2。\n鸣谢列表：\n@Not Cat（提议：CSV格式）\n@猫ちゃん丶（提议：自动重录功能）\n@你亲爱的酒保_K（VRChat拍摄道具）\n@可可脂 与@SKP彭彭 等VRCD创作者系列活动运营组成员（产品宣发）\n\n欢迎加入SceneHelper公测群（882127120）或VRCD玩家社区QQ群（750258838）参与话题讨论。\n\n请打开OBS-工具中的Websocket功能")

expections=["NG", "COOL", "OK"]

host = input("\n请输入Websocket连接地址(默认为localhost)：")
port = int(input("\n请输入Websocket连接端口(默认为4455)："))
password = str(input("\n请输入Websocket连接密码(终端内右键粘贴)："))
scene = str(input("\n请输入录制场次信息："))
scenes_count = int(input("\n请输入要拍多少场戏："))  
scenes_list = [f"Scene {i+1}" for i in range(scenes_count)] 

NG_auto_record = False
COOL_auto_record = False 
OK_auto_record = False

def should_show_advanced():
    user_input = input("\n是否显示高级功能? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_show_advanced()
    
def should_show_debug():
    user_input = input("\n是否显示debug? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_show_debug()
    
def should_ng_auto_record():
    user_input = input("\n是否要在NG后自动重录? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_ng_auto_record()
    
def should_cool_auto_record():
    user_input = input("\n是否要在COOL后自动重录? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_cool_auto_record()
    
def should_ok_auto_record():
    user_input = input("\n是否要在OK后自动重录? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_ok_auto_record()

if should_show_advanced():
    if should_show_debug():
        logging.basicConfig(level=logging.DEBUG)
    if should_ng_auto_record():
        NG_auto_record = True
    if should_cool_auto_record():
        COOL_auto_record = True
    if should_ok_auto_record():
        OK_auto_record = True
    if NG_auto_record and COOL_auto_record and OK_auto_record:
        print("\n三个选项全选？你无敌了朋友，你会停不下来的……\n")
    if NG_auto_record or COOL_auto_record or OK_auto_record:
        auto_record_delay=input("\n自动重录功能受限于电脑情况可能不完全可用，请你测试确保完全可用后再到生产场景中投入使用。\n如果你的电脑不能使用此功能，则你需要更改间隔时间，并在生产场景中注意时间间隔（默认且推荐大多数用户设置为3秒）\n请输入自动重录间隔时间：")
        if not auto_record_delay:
            auto_record_delay=3
            print("\n没有输入值。已设置自动重录时间为默认值3秒。\n")
        else:
            auto_record_delay=int(auto_record_delay)
            print(f"\n已设置自动重录时间为{auto_record_delay}秒。\n")


def GetStatus(ws):
    print("\n开始自检。\n")
    s = str(ws.call(requests.GetRecordStatus()))
    match = re.search(r"'outputActive':\s*([^,}]+)", s)
    if match:
        value = match.group(1).strip().lower() == 'true'
        print("\n自检结果:'outputActive'为" + str(value))
        return value
    else:
        print("未找到'outputActive'，请检查OBS Websocket的版本是否正确\n程序将于10秒后自动退出……\n")
        time.sleep(10)
        exit()

ws = obsws(host, port, password)
ws.connect()

status = GetStatus(ws)
if not status:
    input("目前没有在录制。\n若您的录制目前为暂停状态，则我们会为您停止录制。\n按回车键继续……\n")
else:
    input("啊哦，出现了一个小错误。\n我们检测到OBS目前正在录制状态。\n请您检查OBS的录制情况，按回车键停止当前录制……\n")
ws.call(requests.StopRecord())
print("\n自检完毕。\n当前OBS为待命状态。\n")


start_time = None
init_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def start_record():
    global start_time, start_btn_image
    if start_time is None:
        ws.call(requests.StartRecord())
        start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        print(f"\n录制已开始，时间已记录。\n")
        status_label.config(text="录制已开始，时间已记录。")
        start_btn.config(image=stop_recording_img)
    else:
        status_label.config(text="录制已经开始，无法再次开始。")

def start_auto_record():
    start_record()
    print(f"\n重录已开始！因为状态是{status}。场景：{scene_var.get()}\n")
    
def stop_record(status):
    auto_record=False
    if status == "NG":
        if NG_auto_record:
            auto_record=True
    elif status == "COOL":
        if COOL_auto_record:
            auto_record=True
    else:
        if OK_auto_record:
            auto_record=True
    global start_time, auto_record_delay, start_btn_image
    if start_time:
        ws.call(requests.StopRecord())
        with open(f"{scene} {scene_var.get()} {init_time}.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["场景", "时间", "状态"])
            writer.writerow([scene_var.get(), start_time, status])
        print(f"\n{start_time} 录制已停止，状态为：{status}。场景：{scene_var.get()}\n")
        start_btn.config(image=start_recording_img)
        start_time = None
        if auto_record:
            status_label.config(text=f"将在{auto_record_delay}秒后重录...")
            print(f"\n将要在{auto_record_delay}秒后重录，因为状态是{status}。场景：{scene_var.get()}\n")
            root.after(auto_record_delay * 1000, start_auto_record)
        else:
            status_label.config(text=f"录制已停止，状态为：{status} 场景：{scene_var.get()}。")

root = tk.Tk()
root.title("电子场记板")
root.iconbitmap("assets/ico.ico")

scene_var = tk.StringVar(root)  
scene_var.set(scenes_list[0])
  
scene_combobox = ttk.Combobox(root, textvariable=scene_var, values=scenes_list)
scene_combobox.pack(pady=10)

start_recording_img = PhotoImage(file="assets/start.png")
stop_recording_img = PhotoImage(file="assets/stop.png")
stop_buttons_imgs = [PhotoImage(file=f"assets/{s}.png") for s in expections]

status_label = tk.Label(root, text="录制已停止。", width=27, height=1, wraplength=0, font=('Arial', 30))
status_label.pack(pady=20)

start_btn = tk.Button(root, image=start_recording_img, command=start_record)  
start_btn.image = start_recording_img
start_btn.pack(pady=10)

for status, img in zip(expections, stop_buttons_imgs):
    btn = tk.Button(root, image=img, command=lambda s=status: stop_record(s))
    btn.image = img
    btn.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()

ws.disconnect()  
