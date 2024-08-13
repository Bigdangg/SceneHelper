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

host = input("\nPlease enter the websocket connection address (default is localhost):")
port = int(input("\nPlease enter the Websocket connection port (default is 4455):"))
password = str(input("\nPlease enter the Websocket connection password:"))
scene = str(input("\nPlease enter the recording session information:"))
scenes_count = int(input("\nPlease enter how many scenes you want to shoot:"))  
scenes_list = [f"Scene {i+1}" for i in range(scenes_count)] 

def should_show_debug():
    user_input = input("\nShow debug?  (y/n): ").strip().lower()
    if user_input == 'y':
        return True
    elif user_input == 'n':
        return False
    else:
        print("\nInvalid input, please enter 'y' or 'n'.")
        return should_show_debug()

if should_show_debug():
    logging.basicConfig(level=logging.DEBUG)

def GetStatus(ws):
    print("\nStart the self-test.\n")
    s = str(ws.call(requests.GetRecordStatus()))
    match = re.search(r"'outputActive':\s*([^,}]+)", s)
    if match:
        value = match.group(1).strip().lower() == 'true'
        print("\nSelf-test result: 'outputActive' is" + str(value))
        return value
    else:
        print("'outputActive' not found, please check if the version of OBS Websocket is correct \nThe program will exit automatically after 10 seconds ...\n")
        time.sleep(10)
        exit()

ws = obsws(host, port, password)
ws.connect()

status = GetStatus(ws)
if not status:
    input("Not currently recording. \nIf your recording is currently paused, we will stop the recording for you. \nPress enter to continue ......\n")
else:
    input("Uh-oh, there's been a small error. \nWe have detected that OBS is currently in a recording state. \nPlease check the recording status of OBS and press enter to stop the current recording ...\n")
ws.call(requests.StopRecord())
print("\nSelf-test completed. \n The current OBS is on standby.\n")

start_time = None
init_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

def start_record():
    global start_time, start_btn_image
    if start_time is None:
        ws.call(requests.StartRecord())
        start_time = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        print(f"\nRecording has begun and the time has been recorded.\n")
        status_label.config(text="Recording has begun.")
        start_btn.config(image=stop_recording_img)
    else:
        status_label.config(text="Recording has started.")

def stop_record(status):
    global start_time, start_btn_image
    if start_time:
        ws.call(requests.StopRecord())
        with open(f"{scene} {scene_var.get()} {init_time}.csv", mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Scene", "Time", "Status"])
            writer.writerow([scene_var.get(), start_time, status])
        print(f"\n{start_time} Recording has stopped.:{status}。{scene_var.get()}\n")
        status_label.config(text=f"Recording has stopped:{status}{scene_var.get()}")
        start_btn.config(image=start_recording_img)
        start_time = None  

root = tk.Tk()
root.title("DIGITAL CLAPPING BOARD")
root.iconbitmap("assets/ico.ico")

scene_var = tk.StringVar(root)  
scene_var.set(scenes_list[0])
  
scene_combobox = ttk.Combobox(root, textvariable=scene_var, values=scenes_list)
scene_combobox.pack(pady=10)

start_recording_img = PhotoImage(file="assets/start.png")
stop_recording_img = PhotoImage(file="assets/stop.png")
stop_buttons_imgs = [PhotoImage(file=f"assets/{s}.png") for s in expections]

status_label = tk.Label(root, text="Recording has stopped.", width=27, height=1, wraplength=0, font=('Arial', 30))
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
