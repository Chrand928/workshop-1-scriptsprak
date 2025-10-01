# Imports json data
import json

# Read network-devices.json in utf-8 format
data = json.load(open("network-devices.json","r",encoding = "utf-8"))

# Create a variable that holds our whole text report
report = ""
report += "===============\n" + "Nätverksrapport" + "\n===============\n"
report += "\n" + "ENHETER MED PROBLEM" + "\n---------------\n"

# Loop to collect all "offline" devices in a list
report += "\nStatus: OFFLINE\n"
for location in data["locations"]:   
    for device in location["devices"]:
        if device["status"] == "offline":
            report += device["hostname"] + "   " 
            report += device["ip_address"] + "   "
            report += device["type"] + "   "
            report += location["site"] + "\n"

# Loop to collect all "warning" devices in a list
report += "\nStatus: WARNING\n"
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            report += device["hostname"] + "   " 
            report += device["ip_address"] + "   "
            report += device["type"] + "   "
            report += location["site"] + "   "
            report += "Uptime days: " + str(device["uptime_days"])
            report += "\n"

# Write the report to textfile
with open ("report.txt", "w", encoding="utf-8") as f:
    f.write(report)