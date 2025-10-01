# Imports json data
import json

# Read network-devices.json in utf-8 format
data = json.load(open("network-devices.json","r",encoding = "utf-8"))

# Create a variable that holds our whole text report
report = ""
report += "===============\n" + "Nätverksrapport" + "\n===============\n"

# loop through the "locations" list
for location in data["locations"]:
    # print the "site/name" of the location
    
    report += "\n" + location["site"] + "\n---------------\n"
    # print a list of the host names of the devices on the location
    for device in location["devices"]:
        report += " " + device["hostname"] + "\n"

# Write the report to textfile
with open ("report.txt", "w", encoding="utf-8") as f:
    f.write(report)