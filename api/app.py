#!/usr/bin/python3
import requests
from flask import Flask, request
import time
from datetime import datetime
import threading

# Global variables
# Datetime of when OUI_TABLE was last updated
LAST_UPDATED = datetime.fromtimestamp(0)
# Hashtable for OUI's. OUI's (hex format) is the key and the owner is the value
OUI_TABLE = {
    "l" : {},
    "m" : {},
    "s" : {}
}

# OUI Code

def ieee_oui_updater(sleep_time_hours=12):
    first_time = True
    url_list = [
                ("http://standards-oui.ieee.org/oui/oui.csv", "l"), # Large blocks
                ("http://standards-oui.ieee.org/oui28/mam.csv", "m"), # Medium blocks
                ("http://standards-oui.ieee.org/oui36/oui36.csv", "s") # Small blocks
            ]
    while True:
        print("Started OUI update")
        if first_time:
            #Don't update files on first run to speed up development
            first_time = False
        else:
            
            

            for block_url in url_list:
                with open("data/" + block_url[1] + ".csv", "w") as f:
                    csv = requests.get(block_url[0])
                    f.write(csv.text)


        for block_url in url_list:
            with open("data/" + block_url[1] + ".csv", "r") as f:
                block_csv_raw = f.read()
                
                # simple CSV handling
                for entry in block_csv_raw.split('\n'):
                    line = entry.split(',')
                    try:
                        OUI_TABLE[block_url[1]][line[1]] = line[2]
                    except:
                        print(f"Error: {line}")

        
        LAST_UPDATED = datetime.now()
        print("Ended OUI update")
        time.sleep(((sleep_time_hours - 3) * (60 * 60)))



def sanitise_mac(mac):
    allowed = list("0123456789abcdef")
    new_mac = ''.join(list(filter(lambda x: x in allowed, list(mac))))
    return new_mac

def vendor_lookup(mac_address):
    #Hex lengths 
    len_l = 6
    len_m = 7
    len_s = 9

    vendor = "Unknown"

    mac = sanitise_mac(mac=mac_address)

    len_mac = len(mac)

    if len_mac >= len_l:
        l_oui = mac[:len_l]
        if l_oui in OUI_TABLE['l'].keys():
            vendor = OUI_TABLE['l'][l_oui]
    
    if len_mac >= len_m:
        l_oui = mac[:len_m]
        if l_oui in OUI_TABLE['m'].keys():
            vendor = OUI_TABLE['m'][l_oui]
    
    if len_mac >= len_s:
        l_oui = mac[:len_s]
        if l_oui in OUI_TABLE['s'].keys():
            vendor = OUI_TABLE['s'][l_oui]
    
    return vendor


# Flask logic

app = Flask(__name__)

@app.route("/api/updated")
def get_update_time():
    return str(LAST_UPDATED)

@app.route("/api/lookup")
def lookup():
    mac = request.args.get("mac")
    return vendor_lookup(mac)

@app.route("/")
@app.route("/api")
def hello():
    s = ""
    s += "Hello\n"
    s += "\n"
    s += "call /api/lookup with a 'mac' parameter to do anything\n"
    s += "Example /api/lookup?mac=00:50:56:3e:1a:2d"
    return s


if __name__ == "__main__":
    t = threading.Thread(target=ieee_oui_updater)
    t.start()
    app.run(host="0.0.0.0", port=80)