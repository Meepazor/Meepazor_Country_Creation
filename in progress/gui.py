# -*- coding: utf-8 -*-
"""
Created on Sat Jan  4 17:08:29 2025

@author: rhysb
"""

import tkinter as tk

available_modes = ['1','2','3','4','0']
available_mode_names = ['Country Creation','Flag Resizing','Focus Tree Supplementor','Character Creator','Exit']

main_window = tk.Tk()
main_window.geometry("250x170")
main_window.title("Python Tools by Meep\n")

title_text = tk.Label(main_window, text="Pick a Mode:",font='Helvetica 18 bold')
title_text.pack()

for modes in available_mode_names:
    mode_button = tk.Button(main_window,text=modes,width="20")
    mode_button.pack()

main_window.mainloop()