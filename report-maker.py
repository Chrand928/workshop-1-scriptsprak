# Imports json data
import json

# Import realtime date and time and formating it to be used in the report
from datetime import datetime
dtn = datetime.now()
time_format = dtn.strftime("%Y-%m-%d %H:%M:%S")

# Read network-devices.json in utf-8 format
data = json.load(open("network-devices.json","r",encoding = "utf-8"))

# Create a variable that holds our whole text report
report = ""

# Adds company name variable to the report
report += "==============================\n" + "Nätverksrapport - " 
for company in data["company"]:
    report += company
report += "\n==============================\n"

# Adds time and date value to the report
report += f"Rapportdatum: {time_format}\n"

# Adds time of the creation of the json report data
report += "Datauppdatering: "
for last_updated in data["last_updated"]:
    report += last_updated
report += "\n"


report += "\n" + "ENHETER MED PROBLEM" + "\n---------------\n"

# Loop to collect all "offline" devices in a list
report += "\nStatus: OFFLINE\n"
for location in data["locations"]:   
    for device in location["devices"]:
        if device["status"] == "offline":
            report +=(device["hostname"].ljust (17, " ") 
                    + device["ip_address"].ljust (17, " ") 
                    + device["type"].ljust (17, " ") 
                    + location["site"] 
                    + "\n")

# Loop to collect all "warning" devices in a list
report += "\nStatus: WARNING\n"
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            
            # Line code to add the necessary information to the report
            line = (device["hostname"].ljust(17, " ")
                  + device["ip_address"].ljust(17, " ")
                  + device["type"].ljust(17, " ")
                  + location["site"].ljust(15, " "))

            # info_parts add on additional information such as uptime days and 
            # connected clients to the warning report 
            info_parts = []

            if device["uptime_days"] < 6:
                info_parts.append(f"uptime: {device["uptime_days"]} dagar") 

            if "connected_clients" in device and device ["connected_clients"] > 40:
                info_parts.append(f"{device["connected_clients"]} anslutna klienter!")

            if info_parts:
                report += f"{line} ({", ".join(info_parts)})\n"

# Enheter med låg uptime
report += "\n" + "ENHETER MED LÅG UPTIME (<30 dagar)" + "\n---------------\n"
uptime = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["uptime_days"] <31:
            uptime += 1

            report +=(device["hostname"].ljust(17, " ")
                    + str(device["uptime_days"]).ljust(3, " ") + " dagar".ljust(12, " ")
                    + location["site"].ljust(17, " ")
                    + "\n"
                      )
            
            

# Summering av rapporten där summary hamnar ovanför report när den skrivs till .txt fil
#summary = ""
#summary += "Summary:\n"
#summary += device["type"] osv.
#report = summary + report

# Write the report to textfile
with open ("report.txt", "w", encoding="utf-8") as f:
    f.write(report)