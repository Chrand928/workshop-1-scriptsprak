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

# Summary of the report
summary = ""

# Adds company name variable to the report
summary += "==============================\n" + "Nätverksrapport - " 
for company in data["company"]:
    summary += company
summary += "\n==============================\n"

# Adds time and date value to the report
summary += f"Rapportdatum: {time_format}\n"

# Adds time of the creation of the json report data
summary += "Datauppdatering: "
for last_updated in data["last_updated"]:
    summary += last_updated
summary += "\n"

summary += "\nEXECUTIVE SUMMARY\n" + "------------------------------\n"

# Summary of devices with offline status 
total_offline_devices = sum( 1 
    for location in data["locations"] 
    for device in location["devices"]
    if device["status"] == "offline")
summary += f"⚠ KRITISKT: {total_offline_devices} enheter offline\n"

# Summary of devices with warning status
total_warning_devices = sum( 1
                            for location in data["locations"]
                            for device in location["devices"]
                            if device["status"] == "warning")
summary += f"⚠ VARNING: {total_warning_devices} enheter med varningsstatus\n"

# Summary of devices with low uptime
total_low_uptime_devices = sum ( 1
                                for location in data["locations"]
                                for device in location["devices"]
                                if device["uptime_days"] < 30)
summary += (f"⚠ {total_low_uptime_devices} enheter med låg uptime (<30 dagar) - kan indikera instabilitet\n")

# Summary of switches with high port usage
high_usage_switches = 0
for location in data["locations"]:
    for device in location["devices"]:
        if device["type"] == "switch":
            used_ports = device["ports"]["used"]
            total_ports = device["ports"]["total"]
            usage_percent = (used_ports / total_ports) * 100
            if usage_percent > 80:
                high_usage_switches += 1
summary += f"⚠ {high_usage_switches} switchar har hög portanvändning (>80%)\n"

# Create a variable that holds our whole text report
report = ""

report += "\n" + "ENHETER MED PROBLEM" + "\n------------------------------"

# Loop to collect all "offline" devices in a list
report += "\nStatus: OFFLINE\n"

for location in data["locations"]:   
    for device in location["devices"]:
        if device["status"] == "offline":
            formatted_type = format_device_type(device["type"])    
            report +=( " "
                    + device["hostname"].ljust(17, " ") 
                    + device["ip_address"].ljust(17, " ") 
                    + formatted_type.ljust(17, " ") 
                    + location["site"] 
                    + "\n")

# Loop to collect all "warning" devices in a list
report += "\nStatus: WARNING\n"
for location in data["locations"]:
    for device in location["devices"]:
        if device["status"] == "warning":
            formatted_type = format_device_type(device["type"])
            # Line code to add the necessary information to the report
            line = (" "
                  + device["hostname"].ljust(17, " ")
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

        if device["status"] == "offline":
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

# Gathers information and adds formulas to count the sum of the ports
for location in data["locations"]:
    switches = [device for device in location["devices"] if device["type"] == "switch"]
    num_switches = len(switches)
    used_ports = sum(sp["ports"]["used"] for sp in switches)
    total_site_ports = sum(sp["ports"]["total"] for sp in switches)

    if num_switches == 0:
        continue
    
    # Calculates the usage percentage of ports
    usage_percent = (used_ports / total_site_ports) * 100

    total_used_ports += used_ports
    total_ports += total_site_ports

    # Adds criteria for when a warning message gets added
    warning = " ⚠ " if usage_percent > 80 else ""
    critical = "KRITISKT! ⚠" if usage_percent > 90 else ""
    report += (
            f"{location["site"]}".ljust(18) +
            f"{num_switches}".ljust(1) + " st".ljust(9) +
            f"{used_ports}/{total_site_ports}".ljust(15) + 
            f"{usage_percent:.1f}%".ljust (6) + 
            f"{warning}{critical}\n"
    )

total_usage_percent = (total_used_ports / total_ports) * 100 if total_ports > 0 else 0
report += f"\nTotalt: ".ljust(5) + f"{total_used_ports}/{total_ports} portar används ({total_usage_percent:.1f}%)\n"


report += "\n" + "SWITCHAR MED HÖG PORTANVÄNDNING (>80%)" + "\n------------------------------\n"

#Gather information and combine "ports" with "used" and "total" values to use in a calculation
for location in data ["locations"]:
    for device in location ["devices"]:
        if device ["type"] == "switch":
            used_ports = device["ports"]["used"]
            total_ports = device["ports"]["total"]
            usage_percent = (used_ports / total_ports) * 100

            # Adds variables for when warning messages get added to the report 
            if usage_percent > 80:
                warning = " ⚠ "
                full = "FULLT! ⚠" if used_ports == total_ports else ""
                
                # Adds gathered information to the report
                report += (
                    f"{device["hostname"]}".ljust(18) + 
                    f"{used_ports}/{total_ports}".ljust(10) + 
                    f"{usage_percent:.1f}%".ljust(8) +
                    f"{warning}{full}\n"
                )


report += "\n" + "VLAN-ÖVERSIKT" + "\n------------------------------\n"

# Gathers all unique VLANs to a list
vlans_list = set()
for location in data ["locations"]:
    for device in location["devices"]:
        if device["type"] == "switch" and "vlans" in device:
            vlans_list.update(device["vlans"])

# Sorts the list from low to high
vlans_sorted = sorted(vlans_list)

# Adds total amount of VLANs to the report
report += f"Totalt antal unika VLANs i nätverket: {len(vlans_sorted)} st\n\n"

# Formatting the VLAN list loop
vlans_rows = []
current_row = []
for vlan_count, vlan in enumerate(vlans_sorted, 1):
    current_row.append(f"{vlan}")
    if vlan_count % 10 == 0: # Maximum of 10 VLANs per row in the list
        vlans_rows.append(", ".join(current_row))
        current_row = []

if current_row:
    vlans_rows.append(", ".join(current_row))

# Adds the VLAN list to the report
report += "VLANs:\n" + vlans_rows[0] + "\n"
for row in vlans_rows[1:]:
    report += "" + row + "\n"


report += "\n" + "STATISTIK PER SITE" + "\n------------------------------\n"

for location in data["locations"]:
    
    # Counts the units by their status
    total_devices = len(location["devices"])
    online_devices = sum(1 for device in location["devices"] if device["status"] == "online")
    offline_devices = sum(1 for device in location["devices"] if device["status"] == "offline")
    warning_devices = sum(1 for device in location["devices"] if device["status"] == "warning")

    # String to print out the status
    status_string = f"{online_devices} online, {offline_devices} offline, {warning_devices} warning"

    # Adds all the gathered info to the report
    report += f"{location["site"]} ({location["city"]}):\n"
    report += f" Enheter: {total_devices} ({status_string})\n"
    report += f" Kontakt: {location["contact"]}\n\n"


report += "\n" + "ACCESSPUNKTER - KLIENTÖVERSIKT" + "\n------------------------------\n"

# Gathers information on access points to add to the report
access_points = []
for location in data["locations"]:
    for device in location["devices"]:
        if device["type"] == "access_point" and "connected_clients" in device:
            access_points.append({"hostname": device["hostname"],
                                  "connected_clients": device["connected_clients"]})

# Sorts access points from high to low
access_points_sorted = sorted(access_points, key=lambda ap: ap["connected_clients"], reverse=True)

# Adds the most used access points to the report
for ap in access_points_sorted: 
    if ap["connected_clients"] > 20: # If an access point has more than 20 devices connected it will be added to the list
        warning = " ⚠ Överbelastad ⚠" if ap["connected_clients"] > 40 else ""
        report += (f" {ap["hostname"].ljust(15)} "
                   f"{ap["connected_clients"]} klienter"
                   f"{warning}\n")


report += "\n" + "REKOMMENDATIONER" + "\n------------------------------\n"

offline_devices = sum(1 for location in data["locations"] for device in location ["devices"] if device["status"] == "offline")
report += f"* ⚠ AKUT: Undersök offline-enheter omgående ({offline_devices} st)\n"

datacenter_usage = None
for location in data["locations"]:
    if location["site"] == "Datacenter":
        switches = [device for device in location["devices"] if device["type"] == "switch"]
        used_ports = sum(s["ports"]["used"] for s in switches)
        total_ports = sum(s["ports"]["total"] for s in switches)
        if total_ports > 0:
            usage_percent = (used_ports / total_ports) * 100
            if usage_percent > 90:
                datacenter_usage = usage_percent

if datacenter_usage is not None:
    report += "* ⚠ KRITISKT: Datacenter har extremt låg uptime - planera expansion\n"

report += "* Kontrollera enheter med låg uptime - särskilt de med <5 dagar\n"

# Reccomendation message for the access-point with the most connected clients
access_points = [
    device
    for location in data["locations"]
    for device in location["devices"]
    if device["type"] == "access_point" and "connected_clients" in device
]

if access_points:
    most_ap = max(access_points, key=lambda ap: ap["connected_clients"])
    report += (f"* {most_ap["hostname"]} har {most_ap["connected_clients"]} anslutna klienter (warning) - överväg lastbalansering\n")

report += "\n==============================\n" + "RAPPORT SLUT" + "\n==============================\n"


# Combines summary and report to write to .txt file
full_report = summary + report

# Write the report to textfile
with open ("report.txt", "w", encoding="utf-8") as f:
    f.write(full_report)