from tkinter import filedialog
import os

map_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the map/strategic regions folder from your mod")

for files in os.listdir(map_folder_location):
    lines_array = []
    indicator = 0
    with open(map_folder_location+'/'+files, "r") as map_file:
        zero_start = -1
        zero_end = -1
        four_start = -1
        four_end = -1
        lines = map_file.readlines()
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