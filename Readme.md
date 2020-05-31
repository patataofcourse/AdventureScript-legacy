# AdventureScript
AdventureScript is a text game engine in progress, made specifically for the game codenamed Yet Another Text Game or YATG, and written in Python. It's meant to be imported as a library and can be used asynchronously.

**WARNING: IT'S NOT MEANT TO BE USED BY OTHERS AS OF RN. WILL TRY TO CLEAN UP FOR 2.0**

## Commands right now:
- [n] - wait for input
- [goto] - goes to a specific line
- [flag] - sets flags
- [choice] - prompts player with choice between options and a way to save/load data
- [loadscript] - changes script
- [ending] - ends the script managing and returns
- [saveoff] / [saveon] - Turns on or off the ability to save and restore saves.
- [checkflag] - goes to a different position depending on whether a flag is true or false
- [setvar] - sets variables
- [checkvar] - goes to a different position depending on a conditional between a variable and a given value
- [incvar] - basically +=
- [deflist] - create a list
- [append] - add an item to a list
- [remove] - remove an item from a list. can also remove it based on the value, not the position
- [checklist] - checks if an item is in a list, and goes to a different position whether it's true or false

## What you'll need in your game's directory:
 - AdventureScript folder - You'll have to import this into your "main" python file.
 - script/(game name)/ folder - The first script to be loaded will always be start.adv.
 - save/(game name)/ folder - You'll need to add a "save ID" when you call AdventureScript. That way, multiple save files can be stored.
 - The Python file which'll run your game.

## Loading AS games:
To load a game synchronously, use the parse_sync() function. Otherwise, use parse().
AS works by default in the terminal, but you can use addons or specifically change the I/O functions when calling the parse function.
These parse functions take the following arguments:
 - game [required] - Your game's name. It'll be used to get the script/ and save/ files.
 - save_id [optional] - The ID/filename for the save file. Defaults to 0.
 - show [optional] - A function to replace the default "print text" function (print).
 - wait [optional] - A function to replace the default "wait for user input" function.
 - query [optional] - A function to replace the default choice function.
 - pass_info [optional] - Whether it should pass the ContextInfo to the I/O functions. Defaults to False.
 - addons [optional] - An iterable of addons (python modules) to load. More info below.
 - is_async [optional] - Whether it should run the I/O functions as standard functions (False) or coroutines (True). Defaults to False. Can theoretically be used in parse_sync, but that makes no sense.

## Addons
Addons must have:
 - a synchronous setup function which takes the ContextInfo as an argument.
 - a list called commands which includes all addon command functions (can be empty if there are none)
 Currently, the only addon is AScord.
