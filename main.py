#!/usr/bin/python
import adventurescript as AS
print('''Yet Another Text Game
Pre-Alpha 1
''')
AS.wait_for_input()
ending = AS.parse("test")
print("Congrats, you got the " + ending + " Ending!")