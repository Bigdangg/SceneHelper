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

expections=["NG", "COOL", "OK"]

host = input("\n请输入Websocket连接地址(默认为localhost)：")
port = int(input("\n请输入Websocket连接端口(默认为4455)："))
password = str(input("\n请输入Websocket连接密码："))
scene = str(input("\n请输入录制场次信息："))
scenes_count = int(input("\n请输入要拍多少场戏："))  
scenes_list = [f"Scene {i+1}" for i in range(scenes_count)] 

def should_show_debug():
    user_input = input("\n是否显示debug? (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\n无效输入，请输入'y'或'n'。")
        return should_show_debug()

if should_show_debug():
    logging.basicConfig(level=logging.DEBUG)

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

def stop_record(status):
    global start_time, start_btn_image
    if start_time:
        ws.call(requests.StopRecord())
        with open(f"{scene} {scene_var.get()} {init_time}.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["场景", "时间", "状态"])
            writer.writerow([scene_var.get(), start_time, status])
        print(f"\n{start_time} 录制已停止，状态为：{status}。场景：{scene_var.get()}\n")
        status_label.config(text=f"录制已停止，状态为：{status}{scene_var.get()}。")
        start_btn.config(image=start_recording_img)
        start_time = None  

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
