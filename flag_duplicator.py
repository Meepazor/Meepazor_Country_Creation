# -*- coding: utf-8 -*-
"""
Created on Sun Jun 22

@author: meepazor
"""

import os
from tkinter import filedialog
import shutil

common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the gfx/flags folder from your mod")
#print(common_folder_location)
ideologies_full = ['democratic', 'communism', 'fascism', 'neutrality']
folders_full = ['', '/medium', '/small']
flag_array = []

for folder in folders_full:
    #print(folder)
    flag_location = common_folder_location + folder
    #print(flag_location)
    for file in os.listdir(flag_location):
        if len(file) > 7:
            #print(file + ' stored')
            flag_array.append(file)
    
    for file in os.listdir(flag_location):
        #print(file, len(file))
        if len(file) == 7:
            for ideology in ideologies_full:
                #print(ideology)
                if not file.split('.')[0] + '_' + ideology + '.tga' in flag_array:
                    shutil.copyfile(flag_location + '/' + file, flag_location + '/' + file.split('.')[0] + '_' + ideology + '.tga')