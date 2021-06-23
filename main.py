#!/usr/bin/python
import adventurescript as AS
out = AS.parse_sync("test", save_id=0)
print("Output: " + out) #TODO: this should be handled by AS