# Imports json data
import json

# Import realtime date and time and formating it to be used in the report
from datetime import datetime
dtn = datetime.now()
time_format = dtn.strftime("%Y-%m-%d %H:%M:%S")

# Read network-devices.json in utf-8 format
data = json.load(open("network-devices.json","r",encoding = "utf-8"))

def format_device_type(device_type):
    return device_type.replace ("_", " ").title()

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


report += "\n" + "ENHETER MED PROBLEM" + "\n------------------------------"

# Loop to collect all "offline" devices in a list
report += "\nStatus: OFFLINE\n"

for location in data["locations"]:   
    for device in location["devices"]:
        if device["status"] == "offline":
            formatted_type = format_device_type(device["type"])    
            report +=(device["hostname"].ljust (17, " ") 
                    + device["ip_address"].ljust (17, " ") 
                    + formatted_type.ljust (17, " ") 
                    + location["site"] 
                    + "\n")

# Loop to collect all "warning" devices in a list
report += "\nStatus: WARNING\n"
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            formatted_type = format_device_type(device["type"])
            # Line code to add the necessary information to the report
            line = (device["hostname"].ljust(17, " ")
                  + device["ip_address"].ljust(17, " ")
                  + formatted_type.ljust(17, " ")
                  + location["site"].ljust(15, " "))

            # info adds on additional information such as uptime days and 
            # connected clients to the warning report 
            warning_info = []

            if device["uptime_days"] < 6:
                warning_info.append(f"uptime: {device["uptime_days"]} dagar") 

            if "connected_clients" in device and device ["connected_clients"] > 40:
                warning_info.append(f"{device["connected_clients"]} anslutna klienter!")

            if warning_info:
                report += f"{line} ({" ⚠ ".join(warning_info)})\n"

# Loop to gather all units with uptime at 30 days or lower
report += "\n" + "ENHETER MED LÅG UPTIME (<30 dagar)" + "\n------------------------------\n"

# "uptime" Creates variable to be able to sort the list from low to high
uptime = []
for location in data["locations"]:
    for device in location["devices"]:
        if device["uptime_days"] <31:
            uptime.append({
                "hostname": device["hostname"],
                "uptime_days": device["uptime_days"],
                "site": location["site"]})

# Code to sort the uptime from lowest to highest
uptime_sorted = sorted(uptime, key=lambda u_d: u_d["uptime_days"])

for device in uptime_sorted:
    line = (device["hostname"].ljust(17, " ")
            + str(device["uptime_days"]).ljust(3, " ") + " dagar".ljust(12, " ")
            + device["site"].ljust(17, " ")
            )
    # Adds on "KRISTISKT" information to any device with uptime of 3 days or lower
    if device["uptime_days"] < 4:
        line += "⚠ KRITISKT ⚠"
    
    report += line + "\n"


# Adds library to gather information on types of devices in json file
types_of_devices = {}            
total_devices = 0
total_offline = 0

for location in data["locations"]:
    for device in location["devices"]:
        device_type = device["type"]
        total_devices+= 1

        if device_type not in types_of_devices:
            types_of_devices[device_type] = {"total": 0, "offline": 0}

        types_of_devices[device_type]["total"] += 1

        if device.get("status") == "offline":
            total_offline += 1
            types_of_devices[device_type]["offline"] += 1

offline_status = (total_offline / total_devices) * 100 if total_devices > 0 else 0

report += "\n" + "STATISTIK PER ENHETSTYP" + "\n------------------------------\n"        

# Adds formating values to the gathered information to replace "_" symbol 
# with a " " and make it a capital letter at the start for the device type
for device_type, stats in types_of_devices.items():
    formatted_type = format_device_type(device_type)
    report += (
        f"{formatted_type}:".ljust(17) +
        f"{stats["total"]:2d} st ({stats["offline"]} offline)\n"
        )

report += "\nTotalt:".ljust(17) + f"{total_devices} enheter ({total_offline} offline = {offline_status:.1f}% offline)\n"



report += "\n" + "PORTANVÄNDNING SWITCHAR" + "\n------------------------------\n"
report += "Site".ljust(18) + "Switchar".ljust(10) + "Använt/Totalt".ljust(15) + "Användning" + "\n\n"

total_used_ports = 0
total_ports = 0

for location in data["locations"]:
    site = location["site"]
    switches = [device for device in location["devices"] if device["type"] == "switch"]
    num_switches = len(switches)
    used_ports = sum(sp["ports"]["used"] for sp in switches)
    total_site_ports = sum(sp["ports"]["total"] for sp in switches)

    if num_switches == 0:
        continue

    usage_percent = (used_ports / total_site_ports) * 100

    total_used_ports += used_ports
    total_ports += total_site_ports

    warning = " ⚠ " if usage_percent > 80 else ""
    critical = "KRITISKT! ⚠" if usage_percent > 90 else ""
    report += (
            f"{site}".ljust(18) +
            f"{num_switches}".ljust(1) + " st".ljust(9) +
            f"{used_ports}/{total_site_ports}".ljust(15) + 
            f"{usage_percent:.1f}%".ljust (6) + 
            f"{warning}{critical}\n"
    )

total_usage_percent = (total_used_ports / total_ports) * 100 if total_ports > 0 else 0
report += f"\nTotalt: ".ljust(5) + f"{total_used_ports}/{total_ports} portar används ({total_usage_percent:.1f}%)\n"


report += "\n" + "SWITCHAR MED HÖG PORTANVÄNDNING (>80%)" + "\n------------------------------\n"

for location in data ["locations"]:
    for device in location ["devices"]:
        if device ["type"] == "switch":
            used_ports = device["ports"]["used"]
            total_ports = device["ports"]["total"]
            usage_percent = (used_ports / total_ports) * 100

            if usage_percent > 80:
                warning = " ⚠ "
                full = "FULLT! ⚠" if used_ports == total_ports else ""
                report += (
                    f"{device["hostname"]}".ljust(18) + 
                    f"{used_ports}/{total_ports}".ljust(10) + 
                    f"{usage_percent:.1f}%".ljust(8) +
                    f"{warning}{full}\n"
                )


report += "\n" + "VLAN-ÖVERSIKT" + "\n------------------------------\n"

vlans_list = set()
for location in data ["locations"]:
    for device in location["devices"]:
        if device["type"] == "switch" and "vlans" in device:
            vlans_list.update(device["vlans"])

vlans_sorted = sorted(vlans_list)

report += f"Totalt antal unika VLANs i nätverket: {len(vlans_sorted)} st\n\n"

vlans_rows = []
current_row = []
for vlan_count, vlan in enumerate(vlans_sorted, 1):
    current_row.append(f"{vlan}")
    if vlan_count % 10 == 0: 
        vlans_rows.append(", ".join(current_row))
        current_row = []

if current_row:
    vlans_rows.append(", ".join(current_row))

report += "VLANs:\n" + vlans_rows[0] + "\n"
for row in vlans_rows[1:]:
    report += "" + row + "\n"

# Summering av rapporten där summary hamnar ovanför report när den skrivs till .txt fil
#summary = ""
#summary += "Summary:\n"
#summary += device["type"] osv.
#report = summary + report

# Write the report to textfile
with open ("report.txt", "w", encoding="utf-8") as f:
    f.write(report)