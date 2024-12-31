Check these, especially if the script opens a window, then immediately closes it:

1) Python is installed and is a fairly recent version (I use 3.10 to test)

2) PIL/Pillow is installed - this is the most likely cause of an issue!
	- If it's not installed, or the script isn't working enter 'pip install Pillow' in your cmd prompt window
	- It will install PIL which is required to edit image files (for the flag stuff)
	- Technical documentation of PIL can be found here: https://pillow.readthedocs.io/en/stable/, it is a very established Python extension
	
3) Your base game files are as expected and has not been edited
	- This shouldn't need updating with every patch, but if you notice any bugs (particularly with states of the focus tree), verify integrity of your game files via Steam
