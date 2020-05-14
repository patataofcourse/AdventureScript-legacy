#!/usr/bin/python
import adventurescript as AS
print('''Yet Another Text Game
Pre-Alpha 1
''')
AS.pause()
ending = AS.parse_sync("test")
print("Congrats, you got the " + ending + " Ending!")