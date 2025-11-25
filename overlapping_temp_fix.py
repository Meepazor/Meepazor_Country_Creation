import pathlib
import os
#import system
#import codecs
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import shutil
import re
import subprocess

def set_mode(mode):
    global mode_num
    mode_num = available_modes.index(mode)

def major_function(mode_val):
    if mode_val == '6':
        
        map_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the map/strategic regions folder from your mod")
        
        for files in os.listdir(map_folder_location):
            lines_array = []
            indicator = 0
            with open(map_folder_location+'/'+files, "r") as map_file:
                lines = map_file.readlines()
                zero_start = -1
                zero_end = -1
                four_start = -1
                four_end = -1
                for num, line in enumerate(lines,1):
                    if '0.0 0.0' in line:
                        zero_start = num - 1
                        zero_end = num + 11
                    if '4.11 21.11' in line:
                        four_start = num - 1
                        four_end = num + 11
                for num, line in enumerate(lines,1):
                    if not (zero_start <= num <= zero_end or four_start <= num <= four_end):
                        lines_array.append(line)
            with open(map_folder_location+'/'+files, "w") as map_file:
                for line in lines_array:
                    map_file.write(line)
    

# =============================================================================
# available_modes = ['1','2','3','4','0']
# available_mode_names = ['Country Creation','Flag Resizing','Focus Tree Supplementor','Character Creator','Exit']
# 
# main_window = tk.Tk()
# main_window.geometry("250x170")
# main_window.title("Python Tools by Meep\n")
# 
# title_text = tk.Label(main_window, text="Pick a Mode:",font='Helvetica 18 bold').pack()
# 
# for mode in available_mode_names:
#     mode_button = tk.Button(main_window,text=mode,width="20",command=lambda:major_function(mode)).pack()
# 
# main_window.mainloop()
# =============================================================================

mode_val = '99'
available_modes = ['0','6']

#option to create folders, keeps going until you actually answer y or n
while not mode_val in available_modes:
    mode_val = str(input("6 - Overlapping Temperature Fix\n0 - Exit \nWhich mode would you like? "))
    major_function(mode_val)













