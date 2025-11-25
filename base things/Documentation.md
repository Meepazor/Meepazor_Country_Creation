Are you wondering what it does?
Well then this is the place for you!
Any numbered item is an input from you, any letter within it is what it does.

INSTRUCTIONS:
	1) Copy .py file into your mod's folder (same place as descriptor.mod file)
	2) Run and follow through, more details below

1) "Create folders (y/n)? "
	a) If you enter 'y' it creates the following folders in your mod if they don't exist
		i) common/country_tags
		ii) common/countries
		iii) common/characters
		iv) history/countries
		v) history/units
		vi) localisation/english
		vii) gfx/flags/medium
		viii) gfx/flags/small
		ix) history/states
	b) If you enter 'n' it will assume you have them all
		i) There's no reason to pick 'n' as if you have the folders this step will do nothing
		ii) This acts more of a input to start the whole process

2) "Choose a tag: "
	a) Requires a three character tag that doesn't start with a number
		i) Does not currently have validation it won't clash with the base game

3) "Choose a country name: "
	a) Name of your country, ideally with the correct capitalisation
	b) No other validation
	
4) "Which ideology is your country: Democratic (d); Communism (c); Fascism (f); Neutrality (n)? "
	a) Enter the letter of the ideology for your country to start as this one
	b) You will have 70% of your chosen ideology and 10% of the others
		i) Will not work with custom ideologies

5) Quick Checklist Creation
	a) Checks if you have a 02_countries.txt file
		i) If you do, add your tag and country on the end of it
		ii) If you don't, create a new file and add your tag and country in it
	b) Creates a common/countries file that will be called by 02_countries
		i) Currently defines GFX as 'eastern_european_gfx' - arbitrary
		ii) Currently defines colour as {0,0,0} - will be overwritten by colors.txt file later on
	c) Creates a common/characters file
		i) Inserts an empty characters block for when you need to add one
	d) Creates a history/countries file
		i) Sets capital to 1
		ii) Calls an oob that will be created
		iii) Adds a commented out set_technology line
		iv) Adds a commented out recruit_character line - mostly to stop people adding it as the last line
		v) Sets politics based on your answer in (4)
		vi) Sets popularities based on your answer in (4)
	e) Creates a history/units file
		i) Adds an empty division_template and units block
	f) Creates a localisation/english file and adds the following:
		i) {TAG}
		ii) {TAG}_DEF
		iii) {TAG}_AJG

6) "Create a leader?\nEnter 'n' for No, or enter their name: "
	a) If you enter 'n', nothing happens
		i) No, your leader can't be called 'n' and no that's not a limitation
	b) If you enter a name if will create the following
		i) A character with the id and name of {TAG}_{CHARACTER_NAME}
		ii) A large civilian portrait for the character of the form GFX_portrait_{TAG}_{CHARACTER_NAME}
		iii) A country_leader block with an expire in 1960 and ideology to match the country's:
			d) conservatism
			c) marxism
			f) gen_nazism
			n) despotism
		iv) Add the character and a placeholder description for them in the localisation/english file

7) "Use existing .png, .jpg or .tga file to create flags (y/n)? "
	a) If 'n', this does nothing and locks you out from (8)
	b) If 'y', this opens up a file explorer dialog to pick a .png, .jpg or .tga file
	c) It will then convert this file into a .tga file and resize it to
		i) 82x52 pixels and put it in the gfx/flags folder
		ii) 41x26 pixels and put it in the gfx/flags/medium folder
		iii) 10x7 pixels and put it in the gfx/flags/small folder
	d) There is no validation on the name of the file, so make sure it's named correctly

8) If (7) - "Create up to three more flags for each other ideology (y/n)? "
	a) The same as (7) but three more times so you can have one for each ideology

9) "Create extra files your country may need, including states (y/n)? "
	a) If 'n', this does nothing and locks you out from (10) and (11)
	b) If 'y', it creates the following files/folders in your mod if they don't exist
		i) common/national_focus/{TAG}_focus.txt
			- Also adds basic tree information so your country gets an empty tree
		ii) common/ideas/{TAG}_ideas.txt
			- Adds an empty ideas block
			- Adds an empty country block within that
		iii) common/decisions/{TAG}_decisions.txt
		iv) common/decisions/categories/{TAG}_decision_categories.txt
		v) common/scripted_localisation/{TAG}_scripted_loc.txt
		vi) common/scripted_effects/{TAG}_scripted_effects.txt
		vii) common/scripted_triggers/{TAG}_scripted_triggers.txt
		viii) common/dynamic_modifiers/{TAG}_dynamic_modifiers.txt
		ix) common/on_actions/{TAG}_on_actions.txt
			- Adds an empty on_actions block
		x) common/country_leader/{TAG}_traits.txt
			- Adds an empty leader_traits block
		xi) events/{TAG}_events.txt
			- Adds a commented out example namespace
			- Adds a commented out country_event block
			- Adds a commented out news_event block
		xii) common/names/{TAG}_names.txt
			- Adds arbitrary names for your characters based on what names I could immediately think of
			- Only added as this is now required to avoid a new error that the game flags

10) If (9) - "Import a generic focus tree for your country (y/n)? "
	a) If 'n', this does nothing
	b) If 'y', this opens up a folder explorer dialog to pick the base game "common" folder
		i) Can be in various places, but you should know where this is
			- For me, it's "C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common"
			- If you pick a folder that isn't named "common", it will ask you to do so again
			- If you pick a folder that is named "common" but is the wrong one, it will likely just error
		ii) Will then copy the contents of common/national_focus/generic.txt file and add it to your mod, with a few amendments
			- Keeps the initial information added in step 9bi
			- Adds your tag to the front of national focus id's
		iii) Also adds all focuses (and a desc version) to the localisation/english file
			- What it decides to name then is purely based on the id, so this may differ from the base game
			- Biggest culprit being NAV_focus for naval bombers

11) If (9) - "Choose starting states for your nation? \nEnter 'n' for No, or enter state ids separated by commas - the first being your capital (e.g. 123,376,200): "
	a) If 'n', this does nothing
	b) If 'y', this will flag it will overwrite any states in your mod that you've chosen in the list
		i) The validation on the states entered isn't very good so make sure to match the format closely, I've added an example below:
			- 500,1,250
			- Although it should know to remove spaces
	c) If 'y' and you didn't do 10b, this opens up a folder explorer dialog to pick the base game "history" folder 
		i) If you did do 10b it figures it out from where the "common" folder is
			- Same limitations on validation as in 10bi
		ii) This will then copy the state from the base game and add it to your mod
			- Which state it chooses is based on a natural sorting order, so if you're missing a state in your base game, every state later than it will not copy over correctly
			- Otherwise this should be reliable enough
		iii) It will replace the owner and the FIRST core to be your tag, leaving the original commented out
			- Replacing only the first core is intentional so you don't get duplicates and secondary cores remain
		iv) It will also set your capital in your history/countries files to be the FIRST state you entered
			- So in the example in 11bi it will be "capital = 500"
		v) This step will likely take a few seconds (everything else is usually instant)
			- Due to the sorting

12) "Choose a colour for your nation? \nEnter 'n' for No, or enter RGB values separated by commas (e.g. 10,20,30): "
	a) If 'n', this does nothing
	b) If 'y' and you didn't do 10b OR 11c, this opens up a folder explorer dialog to pick the base game "common" folder 
		i) It will figure it out otherwise
			- Same limitations on validation as in 10bi
		ii) Like 10bi, the validation isn't great, so be sure to match the format
			- Specifically DO NOT add "{", "}" or "rgb"
		iii) If a colors.txt file exists in your mod, adds your country to the end of it
			- Forgot to mention but 12b also won't open the file explorer if this is the case
		iv) If a colors.txt file does not exist in your mod, it copies the one from the base game, then adds your country to the end of it
		v) This will not change the color in the common/countries file because I'm lazy and there's no point
		
Then ta da!
If you said yes to everything you should now have a full functional country on the map!
Time to get to making an actual tree, ideas, lore, events, decisions and all that modding goodness.

If you know Python or are a curious human, there should be some comments to explain some elements, but the rest should be fairly self-explanatory
Please don't use this file to learn things about Python

If you have any suggestions for any content or HOI4-related improvements please let me know
If you have any suggestions that would save a third of a nanosecond by changing the Python, I really don't care as long as it works