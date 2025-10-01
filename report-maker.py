# Imports json data
import json


# Read network-devices.json in utf-8 format
data = json.load(open("network-devices.json","r",encoding = "utf-8"))

# Document title with spaces and breaks
print ("\n==============================\n", "== Nätverksrapport ==", "\n==============================\n")


# loop through the "locations" list
for location in data["locations"]:
    # print the "site/name" of the location
    
    print ("\n===============\n", location["site"], "\n===============")
    # print a list of the host names of the devices on the location
    for device in location["devices"]:
        print (" ", device["hostname"])
