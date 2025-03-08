import pathlib
import os
#import system
#import codecs
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import shutil
import re

#makes sure the sort is in state number order
def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )

def remove_last_line(file):
    with open(file, "r") as edit_file:
        lines = edit_file.readlines()
    with open(file, "w") as edit_file:   
        for line in lines[:-1]:
            edit_file.writelines(line)

def substring_after(string, delimiter):
    return (string.partition(delimiter)[-1]).replace(' ','').replace('\n','')

def find_mod_folder():
    global mod_folder_location, base_path
    if not os.path.exists(str(base_path)+"/common"):
        tk.Tk().withdraw()
        mod_folder_location = os.path.dirname(filedialog.askdirectory(initialdir = "/",title = "Select the common folder from your mod"))
    else:
        mod_folder_location = base_path

def find_mod_file(file_path, initial_text, delete_last_num=False):
    
    os.makedirs(os.path.dirname(str(mod_folder_location)+file_path),exist_ok=True)
    if os.path.exists(str(mod_folder_location)+file_path):
        with open(str(mod_folder_location)+file_path, "r") as file:
            first = file.read(1)
        
        with open(str(mod_folder_location)+file_path, "a") as file:
            if not first:
                file.write(initial_text)
            else:
                file.write("\n")
                if not delete_last_num == False:
                    for x in range(0,delete_last_num):
                        remove_last_line(str(mod_folder_location)+file_path)

def read_without_comments(file, comments=0):
    with open(file,'r') as file_read:
        array = file_read.readlines()
    array = array[comments:]
    print(array)
    return array
            
def folder_up(folder, num=1, new_path=''):
    for i in range(1, num):
        folder = os.path.dirname(folder)
    return folder + '/' + new_path

def remove_duplicates(x):
  return list(dict.fromkeys(x))

def create_character(tag_input, character_input, ideology_input):
    global ideologies, ideologies_sub, ideologies_full, mod_folder_location, history_folder_location
    
    find_mod_file('/common/characters/'+tag_input+'_characters.txt','characters = {\n',1)
    find_mod_file('/localisation/english/'+tag_input+'_l_english.yml','l_english \n ')
    
    character_input_tag = tag_input+'_'+(character_input.replace(' ', '_').lower())
    
    if ideology_input in ideologies:
        ideology_tag = ideologies_sub[ideologies.index(ideology_input)]
    elif ideology_input in ideologies_full:
        ideology_tag = ideologies_sub[ideologies_full.index(ideology_input)]
    else:
        ideology_tag = ideology_input
        
    with open(str(mod_folder_location)+'/common/characters/'+tag_input+'_characters.txt', "a") as character_file:
        character_file.write('\t'+character_input_tag+' = { \n\t\tname = '+character_input_tag+'\n\t\tportraits = {\n\t\t\tcivilian = {\n\t\t\t\tlarge = GFX_portrait_'+character_input_tag+'\n\t\t\t}\n\t\t}\n\t\tcountry_leader = {\n\t\t\tideology = '+ideology_tag+'\n\t\t\texpire = "1960.1.1.1"\n\t\t\tid = -1\n\t\t}\n\t}\n}')
    
    for files in os.listdir(str(mod_folder_location)+'/history/countries'):
        if (os.path.basename(files))[:3] == tag_input:
            history_folder_location = str(mod_folder_location)+'/history/countries/'+files
    
    with open(history_folder_location, "r") as history_file:
        history_file_data = history_file.read()
        history_file_data = history_file_data.replace('set_politics', 'recruit_character = '+character_input_tag+'\nset_politics')
    with open(history_folder_location, "w") as history_file:
        history_file.write(history_file_data)
    
    with open(str(mod_folder_location)+'/localisation/english/'+tag_input+'_l_english.yml', "a") as loc_file:
        loc_file.write('\n '+character_input_tag+': "'+character_input+'"\n '+character_input_tag+'_desc: "'+character_input+' Description"')

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

    #ideology set up
    ideologies = ['d','c','f','n']
    ideologies_full = ['democratic', 'communism', 'fascism', 'neutrality']
    ideologies_sub = ['conservatism', 'marxism', 'gen_nazism', 'despotism']
    
    #various paths to folders needed
    path_array = ["common/country_tags","common/countries","common/characters","history/countries","history/units","localisation/english","gfx/flags/medium","gfx/flags/small","history/states"]
    
    #creates all the folders if they don't exist
    if mode_val == '1':
        for folder in path_array:
            os.makedirs(folder,exist_ok=True)
    
        #choose a tag, keeps going until you input a three character tag where the first is a letter
        while not len(tag_input)==3 or not tag_input[0:1].isalpha():
            tag_input = str(input("Choose a tag: ")).upper()
        
        #choose a country name, keeps going until you actually enter something
        while not len(name_input)>0:
            name_input = str(input("Choose a country name: "))
            
        #choose an ideology, keeps going until you enter something within the ideologies array
        while not ideology_input in ideologies:
            ideology_input = str(input("Which ideology is your country: Democratic (d); Communism (c); Fascism (f); Neutrality (n)? "))
            
        #sets the number of the ideology to be used for full and sub conversion
        ideology_num = ideologies.index(ideology_input)
        
        #opens 02_countries.txt (or creates if it no exist), then adds the country on a new line
        with open(path_array[0]+'/02_countries.txt', "a") as tag_file:
            tag_file.seek(0,0)
            tag_file.write(tag_input+' = "countries/'+name_input+'.txt"\n')
        
        #creates a basic countries file called by 02_countries.txt, eastern europe is arbitrary
        with open(path_array[1]+'/'+name_input+'.txt', "w") as country_file:
            country_file.write('graphical_culture = eastern_european_gfx \ngraphical_culture_2d = eastern_european_2d\n\ncolor = { 0 0 0 }')
        
        #creates a basic characters file with a characters block, may later be amended
        with open(path_array[2]+'/'+tag_input+'_characters.txt', "w") as character_file:
            character_file.write('characters={\n}')
        
        #creates a basic history/countries file with capital = 1, 3 research slots, no research and of the ideology chosen
        #the indexing ensures the ideology you chose has 70% and the others 10%
        #will be incompatible with more than 4 ideologies
        with open(path_array[3]+'/'+tag_input+' - '+name_input+'.txt', "w") as history_file:
            history_file.write('capital = 1\n\noob = "'+tag_input+'_1936"\n\nset_research_slots = 3\n\n#set_technology = {\n#}\n\n#recruit_character = \n\nset_politics = {\n\truling_party = '+ideologies_full[ideology_num]+'\n\tlast_election = "1936.1.1"\n\telection_frequency = 48\n\telections_allowed = yes\n}\n\nset_popularities = {\n\t'+ideologies_full[ideology_num]+' = 70\n\t'+ideologies_full[(ideology_num+1)%4]+' = 10\n\t'+ideologies_full[(ideology_num+2)%4]+' = 10\n\t'+ideologies_full[(ideology_num+3)%4]+' = 10\n}')
        
        #creates an essentially empty oob
        with open(path_array[4]+'/'+tag_input+'_1936.txt', "w") as oob_file:
            oob_file.write('division_template={\n}\nunits = {\n}')
        
        #creates a localisation file and adds country name, DEF and AJG
        with open(path_array[5]+'/'+tag_input+'_l_english.yml', "w", encoding='utf-8-sig') as loc_file:
            loc_file.write('l_english:\n '+tag_input+': "'+name_input+'"\n '+tag_input+'_DEF: "'+name_input+'"\n '+tag_input+'_ADJ: "'+name_input+'"')
        
        #choose a character name, keeps going until you enter one
        #character orig is proper case, character input is with _'s and character input tag is full name lowercased with tag at front
        while len(character_input) == 0:
            character_input_orig = input("Create a leader?\nEnter 'n' for No, or enter their name: ")
            character_input = character_input_orig.replace(' ', '_')
            character_input_tag = tag_input+'_'+(character_input.lower())
        
        #if not n (you can't have a leader with n as the name) 
        #replaces the close bracket in characters file with the basic stuff for a leader, with the right sub ideology
        #replaces commented out recruit character with recruiting this one
        #adds leader to loc file
        if not character_input.lower() == 'n':
            with open(path_array[2]+'/'+tag_input+'_characters.txt', "r") as character_file:
                character_file_data = character_file.read()
                character_file_data = character_file_data.replace('}', '\t'+character_input_tag+' = { \n\t\tname = '+character_input_tag+'\n\t\tportraits = {\n\t\t\tcivilian = {\n\t\t\t\tlarge = GFX_portrait_'+character_input_tag+'\n\t\t\t}\n\t\t}\n\t\tcountry_leader = {\n\t\t\tideology = '+ideologies_sub[ideology_num]+'\n\t\t\texpire = "1960.1.1.1"\n\t\t\tid = -1\n\t\t}\n\t}\n}')
            with open(path_array[2]+'/'+tag_input+'_characters.txt', "w") as character_file:
                character_file.write(character_file_data)
            
            with open(path_array[3]+'/'+tag_input+' - '+name_input+'.txt', "r") as history_file:
                history_file_data = history_file.read()
            history_file_data = history_file_data.replace('#recruit_character =', 'recruit_character = '+character_input_tag)
            with open(path_array[3]+'/'+tag_input+' - '+name_input+'.txt', "w") as history_file:
                history_file.write(history_file_data)
        
            with open(path_array[5]+'/'+tag_input+'_l_english.yml', "a") as loc_file:
                loc_file.write('\n '+character_input_tag+': "'+character_input_orig+'"\n '+character_input_tag+'_desc: "'+character_input_orig+' Description"')
        
        #choose whether you want a flag, keeps going until you enter y or n
        while not (create_flag_ind =='y' or create_flag_ind == 'n'):
            create_flag_ind = input("Use existing .png, .jpg or .tga file to create flags (y/n)? ")
        
        #opens file explorer to pick flag
        #resizes flag to large medium and small and puts them in the right place
        #tag files are valid (more luck than intentional)
        if create_flag_ind == 'y':
            tk.Tk().withdraw()
            flag_input = filedialog.askopenfilename(initialdir = "/",title = "Select a Flag",filetypes = (("PNG files","*.png*"),("JPG files","*.jpg*"),("TGA files","*.tga*")))
            flag_orig = Image.open(flag_input)
            flag_name = (os.path.basename(flag_input))[:-4]
            
            flag_large = flag_orig.resize((82, 52))
            flag_large.save(str(base_path)+'/gfx/flags/'+flag_name+'.tga')
            flag_medium = flag_orig.resize((41, 26))
            flag_medium.save(str(base_path)+'/gfx/flags/medium/'+flag_name+'.tga')
            flag_small = flag_orig.resize((10, 7))
            flag_small.save(str(base_path)+'/gfx/flags/small/'+flag_name+'.tga')
        
            flag_directory = os.path.dirname(flag_input)
            while not (create_mult_flag_ind =='y' or create_mult_flag_ind == 'n'):
                create_mult_flag_ind = input("Create up to three more flags for each other ideology (y/n)? ")
            
            if create_mult_flag_ind == 'y':
                for x in range(1,4):
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
                    except ValueError:
                        print("Ended early")
        
        #choose whether you want the extra files, keeps going until you enter y or n
        while not (create_extras_ind =='y' or create_extras_ind == 'n'):
            create_extras_ind = input("Create extra files your country may need, including states (y/n)? ")
        
        if create_extras_ind == 'y':
            #only start these if needed
            extra_path_array = ["common/national_focus","common/ideas","common/decisions","common/decisions/categories","common/scripted_localisation","common/scripted_effects","common/scripted_triggers","common/dynamic_modifiers","common/on_actions","common/country_leader","events","common/names"]
            extra_file_names = [tag_input+"_focus.txt",tag_input+"_ideas.txt",tag_input+"_decisions.txt",tag_input+"_decision_categories.txt",tag_input+"_scripted_loc.txt",tag_input+"_scripted_effects.txt",tag_input+"_scripted_triggers.txt",tag_input+"_dynamic_modifiers.txt",tag_input+"_on_actions.txt",tag_input+"_traits.txt",tag_input+"_events.txt",tag_input+"_names.txt"]
            extra_file_inputs = ['focus_tree={\n\n\tid = '+tag_input+'_focus\n\n\tcountry = {\n\t\tfactor = 0\n\t\tmodifier = {\n\t\t\tadd = 10\n\t\t\ttag = '+tag_input+'\n\t\t}\n\t}\n\n\tdefault = no\n\treset_on_civilwar = no\n\n\tcontinuous_focus_position = { x = 1000 y = 1000 }\n\n\t#focus = {}\n}','ideas = {\n\tcountry = {\n\t}\n}','','','','','','','on_actions = {\n}','leader_traits = {\n}','#add_namespace = example\n\n#country_event = {}\n\n#news_event = {}',tag_input+' = {\n\tmale = {\n\t\tnames = { John Steve Greg }\n\t}\n\tfemale = {\n\t\tnames = { Jane Stevie Grace }\n\t}\n\tsurnames = { Jonhson Stevensen Gregson }\n\tcallsigns = { }\n}']
            
            for folder in extra_path_array:
                os.makedirs(folder,exist_ok=True)
                
                folder_num = extra_path_array.index(folder)
                #file_name = extra_file_names[folder_num]
                
                with open(extra_path_array[folder_num]+'/'+extra_file_names[folder_num], "w") as new_extra_file:
                    new_extra_file.write(extra_file_inputs[folder_num])
                
            #choose whether you want a basic focus tree, keeps going until you enter y or n
            while not (create_focus_ind =='y' or create_focus_ind == 'n'):
                create_focus_ind = input("Import a generic focus tree for your country (y/n)? ")       
                
            if create_focus_ind == 'y':
                
                #because I don't have a better way to do this yet
                extra_replace_from = ['prerequisite = { focus = '+tag_input+'_bomber_focus focus = fighter_focus }','prerequisite = { focus = '+tag_input+'_flexible_navy focus = large_navy }','prerequisite = { focus = '+tag_input+'_large_navy focus = flexible_navy }','prerequisite = { focus = '+tag_input+'_foreign_expeditions focus = deterrence }','prerequisite = { focus = '+tag_input+'_paramilitarism focus = political_commissars }','prerequisite = { focus = '+tag_input+'_ideological_fanaticism focus = why_we_fight }']
                extra_replace_to = ['prerequisite = { focus = '+tag_input+'_bomber_focus focus = '+tag_input+'_fighter_focus }','prerequisite = { focus = '+tag_input+'_flexible_navy focus = '+tag_input+'_large_navy }','prerequisite = { focus = '+tag_input+'_large_navy focus = '+tag_input+'_flexible_navy }','prerequisite = { focus = '+tag_input+'_foreign_expeditions focus = '+tag_input+'_deterrence }','prerequisite = { focus = '+tag_input+'_paramilitarism focus = '+tag_input+'_political_commissars }','prerequisite = { focus = '+tag_input+'_ideological_fanaticism focus = '+tag_input+'_why_we_fight }']
                
                #choose file
                tk.Tk().withdraw()
                common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game")
                
                #check file is a valid one
                try:
                    while not (os.path.basename(common_folder_location) == 'common') or invalid_ind == 1:
                        if os.path.basename(common_folder_location) == 'common':
                            with open(common_folder_location+'/national_focus/generic.txt', "r") as generic_file:
                                generic_file_data = generic_file.read()
                                generic_file_data = generic_file_data.replace('\t\tid = ','\t\tid = '+tag_input+'_')
                                generic_file_data = generic_file_data.replace('relative_position_id = ','relative_position_id = '+tag_input+'_')
                                generic_file_data = generic_file_data.replace('prerequisite = { focus = ','prerequisite = { focus = '+tag_input+'_')
                                generic_file_data = generic_file_data.replace('mutually_exclusive = { focus = ','mutually_exclusive = { focus = '+tag_input+'_')
                                for replace_from in extra_replace_from:
                                    generic_file_data = generic_file_data.replace(replace_from,extra_replace_to[extra_replace_from.index(replace_from)])
                                
                                new_focus_file = open(extra_path_array[0]+'/'+extra_file_names[0], "a")
                                new_focus_file.write(generic_file_data)
                                new_focus_file.close()
                                
                                new_focus_file = open(extra_path_array[0]+'/'+extra_file_names[0], "r")
                                lines = new_focus_file.readlines()
                                new_focus_file = open(extra_path_array[0]+'/'+extra_file_names[0], "w")
                                for number, line in enumerate(lines):
                                    if number not in range(17,51):
                                        new_focus_file.write(line)
                                new_focus_file.close()
                            invalid_ind = 0
                        else:
                            print("INVALID FOLDER, it should be called common")
                            tk.Tk().withdraw()
                            common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game")
                except ValueError:
                    print("Ended early")
                
                #open file, get lines with focus id's and then add them to the localisation file
                new_focus_file = open(extra_path_array[0]+'/'+extra_file_names[0], "r")
                loc_lines = new_focus_file.readlines()
                loc_lines_array = []
                focus_check = '\t\tid = '+tag_input
                for line in loc_lines:
                    if focus_check in line and not 'relative_position' in line:
                        loc_lines_array.append(line[7:])
                
                with open(path_array[5]+'/'+tag_input+'_l_english.yml', "a") as loc_file:
                    loc_file.write('\n\n #FOCUS LOCALISATIONS')
                    for loc_line in loc_lines_array:
                        loc_line_id = loc_line.replace('\n','')
                        loc_line_loc = loc_line.replace('_',' ').replace(tag_input,'').replace('\n','').title()
                        loc_file.write('\n '+loc_line_id+': "'+loc_line_loc[1:]+'"')
                        loc_line_id = loc_line.replace('\n','')
                        loc_line_loc = loc_line.replace('_',' ').replace(tag_input,'').replace('\n','').title()
                        loc_file.write('\n '+loc_line_id+'_desc: "'+loc_line_loc[1:]+' Description"')
                
                new_focus_file.close()
               
            invalid_ind = 1
            
            #choose whether you want to assign states, keeps going until you enter y or n
            while len(create_states_ind)==0:
                create_states_ind = input("Choose starting states for your nation? \nEnter 'n' for No, or enter state ids separated by commas - the first being your capital (e.g. 123,376,200): ")
            
            if not create_states_ind == 'n' and (create_states_ind.replace(',','')).isnumeric():
                create_states_ind = create_states_ind.replace(' ','')
                create_states_array = create_states_ind.split(',')
                
                warning_ind = input("WARNING, any states you have selected which are already present in your mod will be ovewritten by the game game files \nEnter 'y' to continue: ")
                if warning_ind.lower()=='y':
                    if not (os.path.basename(common_folder_location) == 'common' or os.path.basename(history_folder_location)=='states'):
                        try:
                            #choose file
                            tk.Tk().withdraw()
                            history_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the history folder from the base game") 
                        except ValueError:
                            print("Ended early") 
                            
                    if os.path.basename(history_folder_location) == 'history':
                        history_folder_location = history_folder_location+'/states'            
                    elif os.path.basename(common_folder_location) == 'common':
                        history_folder_location = os.path.dirname(common_folder_location)+'/history/states'            
                    
                    state_file_array = []
                    for files in os.listdir(history_folder_location):
                        state_file_array.append(files)
                        sort_nicely(state_file_array)
                        
                    for state in create_states_array:
                        state_num = int(state) - 1
                        shutil.copyfile(history_folder_location+'/'+state_file_array[state_num], 'history/states/'+state_file_array[state_num])
                        with open('history/states/'+state_file_array[state_num], "r") as state_file:
                            state_file_data = state_file.read()
                            state_file_data = state_file_data.replace('owner = ', 'owner = '+tag_input+' #')
                            state_file_data = state_file_data.replace('add_core_of = ', 'add_core_of = '+tag_input+' #',1)
                        with open('history/states/'+state_file_array[state_num], "w") as state_file:  
                            state_file.write(state_file_data)
                    
                    with open(path_array[3]+'/'+tag_input+' - '+name_input+'.txt', "r") as history_file:
                        history_file_data = history_file.read()
                    history_file_data = history_file_data.replace('capital = 1', 'capital = '+create_states_array[0])
                    with open(path_array[3]+'/'+tag_input+' - '+name_input+'.txt', "w") as history_file:
                        history_file.write(history_file_data)  
                    
            invalid_ind == 1       
        #choose whether you want to do the colors file, keeps going until you enter y or n
        while len(create_colour_ind)==0:
            create_colour_ind = input("Choose a colour for your nation? \nEnter 'n' for No, or enter RGB values separated by commas (e.g. 10,20,30): ")
            
        if not create_colour_ind == 'n':
            create_colour = create_colour_ind.replace(',',' ')
            
            if os.path.exists('common/countries/colors.txt'):
                with open('common/countries/colors.txt', "a") as colours_file:
                    colours_file.write('\n'+tag_input+' = {\n\tcolor = rgb { '+create_colour+' }\n\tcolor_ui = rgb { '+create_colour+' }\n}')
            elif os.path.basename(common_folder_location) == 'common':
                shutil.copyfile(common_folder_location+'/countries/colors.txt', 'common/countries/colors.txt')
                with open('common/countries/colors.txt', "a") as colours_file:
                    colours_file.write('\n'+tag_input+' = {\n\tcolor = rgb { '+create_colour+' }\n\tcolor_ui = rgb { '+create_colour+' }\n}')
                invalid_ind = 0
            elif os.path.basename(history_folder_location) == 'states':
                history_folder_location = os.path.dirname(os.path.dirname(history_folder_location))+'/common'
                shutil.copyfile(common_folder_location+'/countries/colors.txt', 'common/countries/colors.txt')
                with open('common/countries/colors.txt', "a") as colours_file:
                    colours_file.write('\n'+tag_input+' = {\n\tcolor = rgb { '+create_colour+' }\n\tcolor_ui = rgb { '+create_colour+' }\n}')
                invalid_ind = 0
            else:
                try:
                    #choose file
                    tk.Tk().withdraw()
                    common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game") 
                    while not (os.path.basename(common_folder_location) == 'common') or invalid_ind == 1:
                        if os.path.basename(common_folder_location) == 'common':
                            shutil.copyfile(common_folder_location+'/countries/colors.txt', 'common/countries/colors.txt')
                            with open('common/countries/colors.txt', "a") as colours_file:
                                colours_file.write('\n'+tag_input+' = {\n\tcolor = rgb { '+create_colour+' }\n\tcolor_ui = rgb { '+create_colour+' }\n}')
                            invalid_ind = 0
                        else:
                           print("INVALID FOLDER, it should be called common")
                           tk.Tk().withdraw()
                           common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game") 
                except ValueError:
                    print("Ended early")
    
    #flag stuff, almost identical to above
    elif mode_val == '2':
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
            
    elif mode_val == '3':
        focus_input = filedialog.askopenfilename(initialdir = '/',title = 'Select Your National_Focus File',filetypes = (("Text files","*.txt*"),('All files', '*.*')))
        common_folder_location = os.path.dirname(os.path.dirname(focus_input))
        mod_name = str(os.path.basename(os.path.dirname(common_folder_location))).replace(' ','').lower()
        
        options_array = ["tag = ","add_ideas"]
        tag_found_ind = False
        supp_ideas_ind = ''
    
        with open(focus_input, "r") as focus_file:
            focus_file_data = focus_file.readlines()
    
        for line in focus_file_data:
            if tag_found_ind == False and options_array[0] in line:
                tag_input = substring_after(line, '=')
                tag_found_ind = True
        
        #choose whether you want to do ideas, keeps going until you enter y or n
        while not (supp_ideas_ind =='y' or supp_ideas_ind == 'n'):
            supp_ideas_ind = input("Ideas (y/n)? ")
        
        if supp_ideas_ind == 'y':
        
            ideas_array = []
            ideas_contents = ["\nideas = {\n\tcountry = {\n\t"," = {\n\t\t\t","picture = generic_economic_increase\n\n\t\t\tallowed = { always = no }\n\t\t\tallowed_civil_war = { always = no }\n\t\t\tremoval_cost = -1\n\n\t\t\tmodifier = {}\n\t\t}\n\t","}\n}"]
            old_idea_ind = False
            
            for line in focus_file_data:
                if options_array[1] in line:
                    if '{' in line:
                        print("Invalid Idea Found")
                    elif substring_after(line, '=') not in ideas_array:
                        ideas_array.append(substring_after(line, '='))
            
            if os.path.exists("saved_additions_"+mod_name+".txt"):
                with open("saved_additions_"+mod_name+".txt", "r") as save_file:
                    save_file_data = save_file.readlines()
                    for old_idea_orig in save_file_data:
                        old_idea = old_idea_orig.replace('IDEA:','').replace('\n','')
                        if old_idea in ideas_array:
                            ideas_array.remove(old_idea)
                            old_idea_ind = True
                            
            if ideas_array:
                os.makedirs(common_folder_location+"/ideas/",exist_ok=True)
                os.makedirs(os.path.dirname(common_folder_location)+"/localisation/english/",exist_ok=True)
                
                if old_idea_ind == True:
                    remove_last_line(common_folder_location+"/ideas/"+tag_input+"_ideas.txt")
                    remove_last_line(common_folder_location+"/ideas/"+tag_input+"_ideas.txt")
                
                with open(common_folder_location+"/ideas/"+tag_input+"_ideas.txt", "a") as idea_file:
                    if old_idea_ind == True:
                        idea_file.write("\t")
                    else:
                        idea_file.write(ideas_contents[0])
                             
                    for idea in ideas_array:
                        idea_file.write("\t"+idea+ideas_contents[1]+ideas_contents[2])
                    idea_file.write(ideas_contents[3])
                
                with open(os.path.dirname(common_folder_location)+"/localisation/english/"+tag_input+"_l_english.yml", "r") as localisation_file:
                    first_char_loc = localisation_file.read(1)
                    
                with open(os.path.dirname(common_folder_location)+"/localisation/english/"+tag_input+"_l_english.yml", "a", encoding='utf-8-sig') as localisation_file:
                    if not first_char_loc:
                        localisation_file.write("l_english:")
                    else:
                        localisation_file.write("\n")
                        
                    for idea in ideas_array:
                        if idea[:4] == tag_input+'_':
                            idea_proper = idea.replace(tag_input+'_', '').replace('_',' ').title()
                        else:
                            idea_proper = idea.replace('_',' ').title()
                        localisation_file.write('\n '+idea+': "'+idea_proper+'"')
                        localisation_file.write('\n '+idea+'_desc: "'+idea_proper+' Description"')
                
                if not os.path.exists("saved_additions_"+mod_name+".txt"):
                    save_file = open("saved_additions_"+mod_name+".txt", "w")
                    save_file.close()
                         
                with open("saved_additions_"+mod_name+".txt", "r") as save_file:
                    first_char_save = save_file.read(1)
                
                with open("saved_additions_"+mod_name+".txt", "a") as save_file:    
                    if not first_char_save:
                        save_file.write("#Additions already made by the tool for the mod: "+mod_name+"\n#This avoids duplication so don't remove this or any lines from it!")
                    for idea in ideas_array:
                        print("Added idea "+idea+" to '"+tag_input+"_ideas.txt' and '"+tag_input+"_l_english.yml'")
                        save_file.write("\nIDEA:"+idea)
    
    elif mode_val == '4':
        character_mass_ind = ''
        
        while not (character_mass_ind =='1' or character_mass_ind == '2'):
            character_mass_ind = input("Create a single character (1) or import character_creator.txt (2)? ")
    
        if character_mass_ind == '1':
            #choose a tag, keeps going until you input a three character tag where the first is a letter
            while not len(tag_input)==3 or not tag_input[0:1].isalpha():
                tag_input = str(input("Choose a tag to recruit the character: ")).upper()
                
            #choose a character name, keeps going until you actually enter something
            while not len(character_input)>0:
                character_input = str(input("Enter the name of your character: "))
                
            #choose an ideology
            while not len(ideology_input)>0:
                ideology_input = str(input("Enter your ideology or sub-ideology (anything not recognised as an ideology will be assumed to be a sub-ideology): ")).lower()
        
            find_mod_folder()
            create_character(tag_input, character_input, ideology_input)
        
        if character_mass_ind == '2':
            file_input = filedialog.askopenfilename(initialdir = '/',title = 'Select your character creator file',filetypes = (("Text files","*.txt*"),('All files', '*.*')))
            characters = read_without_comments(file_input, 3)
            find_mod_folder()
            
            for character in characters:
                character_info = character.split(';')
                print(character_info)
                
                tag_input = character_info[0]
                character_input = character_info[1]
                ideology_input = character_info[2].replace('\n','')
                create_character(tag_input, character_input, ideology_input)
            
    elif mode_val == '5':
        
        states_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the history folder from your mod")
        victory_points = []
        indicator = 0
        
        for files in os.listdir(states_folder_location+'/states'):
            with open(states_folder_location+'/states/'+files, "r") as state_file:
                lines = state_file.readlines()
                for line in lines:
                    if indicator == 1:
                        victory_points.append((line.split(' ')[0].replace('\t', '')))
                        indicator = 0
                    if 'victory_points = {' in line:
                        indicator = 1
        
        map_folder_location = os.path.dirname(states_folder_location)+'/map' 
        
        with open(map_folder_location+'/supply_nodes_temp.txt', 'a') as supply_node_file:
            for victory_point in victory_points:
                supply_node_file.write('1 '+victory_point+'\n')
                
    elif mode_val == '6':
        
        map_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the map/strategic regions folder from your mod")
        
        for files in os.listdir(map_folder_location):
            lines_array = []
            indicator = 0
            with open(map_folder_location+'/'+files, "r") as map_file:
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
                
    elif mode_val == '7':
        
        map_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the map folder from your mod")
        with open(map_folder_location+'/adjacencies.csv', 'r') as csv_file:
            csv_file_lines = csv_file.readlines()
        
        for num, line in enumerate(csv_file_lines,1):
            with open('base_adjacency.txt', "r") as base_file:
                base_file_data = base_file.read()
            if num > 1:
                csv_info = line.split(';')
                if not csv_info[0] == '-1':
                    print('Added ' + csv_info[8])
                    base_file_data = base_file_data.replace('NAME_REPLACE', csv_info[8])
                    base_file_data = base_file_data.replace('ID1', csv_info[0])
                    base_file_data = base_file_data.replace('ID2', csv_info[1])
                    base_file_data = base_file_data.replace('ID3', csv_info[3])
            
                    with open(map_folder_location+'/adjacency_rules.txt', 'a') as txt_file:
                        txt_file.write('\n'+base_file_data)
    
    elif mode_val == '8':
       
        common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from your mod")
        log_folder_location = folder_up(common_folder_location, 4, 'logs')
        focus_array = []
        
        with open(log_folder_location+'/error.log', 'r') as error_file:
            error_file_lines = error_file.readlines()
            for line in error_file_lines:
                if 'has_completed_focus = ' in line:
                    print(line)
                    focus_array.append(substring_after(line, 'has_completed_focus = ').split('(')[0])
            
            if focus_array:
                focus_array = remove_duplicates(focus_array)
                
                with open('base_tree.txt', 'r') as base_tree:
                    base_tree_data = base_tree.read()
                
                with open(common_folder_location+'/national_focus/error_focus.txt', 'w') as focus_file:
                    focus_file.write(base_tree_data)
                    for focus in focus_array:
                        with open('base_focus.txt', 'r') as base_focus:
                            base_focus_data = base_focus.read()
                            base_focus_data = base_focus_data.replace('FOCUS_ID', focus)
                            focus_file.write('\n'+base_focus_data)
                    focus_file.write('\n}')
        
    #close = input("\nDone? ")
    
    #elif mode_val == '0':
        #main_window.destroy()
    

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
available_modes = ['0','1','2','3','4','5','6','7','8']

#option to create folders, keeps going until you actually answer y or n
while not mode_val in available_modes:
    mode_val = str(input("1 - Full Country Creation\n2 - Flag Resizing\n3 - Focus Tree Supplementor\n4 - Character Creator\n5 - Victory Points -> Supply Nodes\n6 - Overlapping Temperature Fix\n7 - Adjacency CSV to TXT\n8 - Has Completed Focus Error Fix\n0 - Exit \nWhich mode would you like? "))
    major_function(mode_val)













