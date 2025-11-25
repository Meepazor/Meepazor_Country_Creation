import pathlib
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import shutil
            
def folder_up(folder, num=1, new_path=''):
    for i in range(1, num):
        folder = os.path.dirname(folder)
    return folder + '/' + new_path

def set_mode(mode):
    global mode_num
    mode_num = available_modes.index(mode)

def major_function(mode_val):
    #stuff needed later on
    global base_path, ideologies, ideologies_sub, ideologies_full, mod_folder_location, history_folder_location
    
    base_path = pathlib.Path(__file__).parent.resolve()
    character_input = ''
    create_flag_ind = ''
    create_mult_flag_ind = ''
    create_extras_ind = ''
    create_focus_ind = ''
    create_colour_ind = ''
    create_states_ind = ''
    tag_input = 'taggerihardlyknowher' #lmao
    name_input = ''
    ideology_input = ''
    invalid_ind = 1
    warning_ind = ''
    history_folder_location = base_path
    common_folder_location = base_path
    flag_directory = '/'
    
    if 1==1:
        additional_flag_ind = 'y'
        os.makedirs("gfx/flags/medium",exist_ok=True)
        os.makedirs("gfx/flags/small",exist_ok=True)
        while additional_flag_ind == 'y':
            try:
                flag_input = filedialog.askopenfilename(initialdir = flag_directory,title = "Select a Flag",filetypes = (("PNG files","*.png*"),("JPG files","*.jpg*"),("TGA files","*.tga*")))
                flag_orig = Image.open(flag_input)
                flag_name = (os.path.basename(flag_input))[:-4]
                
                flag_large = flag_orig.resize((82, 52))
                flag_large.save(str(base_path)+'/gfx/flags/'+flag_name+'.tga')
                flag_medium = flag_orig.resize((41, 26))
                flag_medium.save(str(base_path)+'/gfx/flags/medium/'+flag_name+'.tga')
                flag_small = flag_orig.resize((10, 7))
                flag_small.save(str(base_path)+'/gfx/flags/small/'+flag_name+'.tga')
                
                flag_directory = os.path.dirname(flag_input)
            except ValueError:
                print("Ended early")
            additional_flag_ind = input("Convert another flag (y/N)? ").lower()

mode_val = '99'
available_modes = ['0','2']

#option to create folders, keeps going until you actually answer y or n
while not mode_val in available_modes:
    mode_val = str(input("2 - Flag Resizing\n0 - Exit \nWhich mode would you like? "))
    major_function(mode_val)













