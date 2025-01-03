import pathlib
import os
#import system
#import codecs
import tkinter
from tkinter import filedialog
from PIL import Image
import shutil
import re

#makes sure the sort is in state number order
def sort_nicely(l):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    l.sort( key=alphanum_key )

#stuff needed later on
base_path = pathlib.Path(__file__).parent.resolve()
create_folders_ind = ''
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

#ideology set up
ideologies = ['d','c','f','n']
ideologies_full = ['democratic', 'communism', 'fascism', 'neutrality']
ideologies_sub = ['conservatism', 'marxism', 'gen_nazism', 'despotism']

#option to create folders, keeps going until you actually answer y or n
while not (create_folders_ind =='y' or create_folders_ind == 'n'):
    create_folders_ind = input("Create folders (y/n)? ").lower()

#various paths to folders needed
path_array = ["common/country_tags","common/countries","common/characters","history/countries","history/units","localisation/english","gfx/flags/medium","gfx/flags/small","history/states"]

#creates all the folders if they don't exist
if create_folders_ind == 'y':
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
    loc_file.write('l_english:\n '+tag_input+': "'+name_input+'"\n '+tag_input+'_DEF: "'+name_input+'"\n '+tag_input+'_AJG: "'+name_input+'"')

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
    tkinter.Tk().withdraw()
    flag_input = filedialog.askopenfilename(initialdir = "/",title = "Select a Flag",filetypes = (("PNG files","*.png*"),("JPG files","*.jpg*"),("TGA files","*.tga*")))
    flag_orig = Image.open(flag_input)
    flag_name = (os.path.basename(flag_input))[:-4]
    
    flag_large = flag_orig.resize((82, 52))
    flag_large.save(str(base_path)+'/gfx/flags/'+flag_name+'.tga')
    flag_medium = flag_orig.resize((41, 26))
    flag_medium.save(str(base_path)+'/gfx/flags/medium/'+flag_name+'.tga')
    flag_small = flag_orig.resize((10, 7))
    flag_small.save(str(base_path)+'/gfx/flags/small/'+flag_name+'.tga')

    while not (create_mult_flag_ind =='y' or create_mult_flag_ind == 'n'):
        create_mult_flag_ind = input("Create up to three more flags for each other ideology (y/n)? ")
    
    if create_mult_flag_ind == 'y':
        for x in range(1,4):
            try:
                flag_input = filedialog.askopenfilename(initialdir = "/",title = "Select a Flag",filetypes = (("PNG files","*.png*"),("JPG files","*.jpg*"),("TGA files","*.tga*")))
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
        file_name = extra_file_names[folder_num]
        
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
        tkinter.Tk().withdraw()
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
                    tkinter.Tk().withdraw()
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
            if os.path.basename(common_folder_location) == 'common' or os.path.basename(history_folder_location)=='states':
                path = 1
            else:
                path = 2
                try:
                    #choose file
                    tkinter.Tk().withdraw()
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
            tkinter.Tk().withdraw()
            common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game") 
            while not (os.path.basename(common_folder_location) == 'common') or invalid_ind == 1:
                if os.path.basename(common_folder_location) == 'common':
                    shutil.copyfile(common_folder_location+'/countries/colors.txt', 'common/countries/colors.txt')
                    with open('common/countries/colors.txt', "a") as colours_file:
                        colours_file.write('\n'+tag_input+' = {\n\tcolor = rgb { '+create_colour+' }\n\tcolor_ui = rgb { '+create_colour+' }\n}')
                    invalid_ind = 0
                else:
                   print("INVALID FOLDER, it should be called common")
                   tkinter.Tk().withdraw()
                   common_folder_location = filedialog.askdirectory(initialdir = "/",title = "Select the common folder from the base game") 
        except ValueError:
            print("Ended early")

 
    
    
    
    
    
    
    
    
