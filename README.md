# parts
Parts - A text based game written in python


All versions of the game require having Python3 installed.


(def_version)

There are three versions of the game. I had originally written it using all functions and it works just fine.


(class_venv_version)

I have rarely used classes in Python, and wanted to try rewriting the game functionality using classes.
I got it working using classes and have since added some features that weren't a part of the function based version.
There are a couple of packages I use for building and displaying the map. So, to play the game you would need to get into the virtual environment.


(class_nonvenv_version) - Current version

Realized that the venv ends up being 491MB, so I made a version that doesn't rely on an activated venv.
It has a dynamic map but doesn't have the pretty map display at the end game. Lots of code clean up and adding functionality.
I also added some toys to 'pretty' up the text: colors, text formatting, and sleep timers to try and smooth out the text display.


Download, and then in console / terminal, cd into the parts directory, then 'python3 parts.py' to start the game.


Have fun.
