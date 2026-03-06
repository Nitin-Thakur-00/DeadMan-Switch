import json
import os
import time
import ctypes
import requests
import sys
import tkinter as tk
from tkinter import filedialog, simpledialog
import shredder #imports the logic from shredder.py file.

API_URL= API_URL = "http://127.0.0.1:8000/status"
LOCAL_CONFIG = "local_config.json"

def get_vault_config():  # Checks if a vault is already selected. ask for the directory and the offline limit in minutes.
    if os.path.exists(LOCAL_CONFIG):
        with open(LOCAL_CONFIG,"r") as f:
            return json.load(f)
            
    root = tk.Tk() # Setup Phase: Initialize a hidden Tkinter window.
    root.withdraw() # Hide the main tiny tk window
    root.attributes("-topmost", True) # Bring the dialog to the front
    
    selected_path = filedialog.askdirectory(title="Select the Directory.")  # Directory selection.
    if not selected_path:
        sys.exit()

    
    limit = simpledialog.askinteger("Settings", "Offline Limit (minutes) before Hiding files:", initialvalue=120, minvalue=1, maxvalue=1440)
    if limit is None:
        sys.exit()
    
    config = {"vault_path": selected_path, "offline_limit_mins": limit}
    with open(LOCAL_CONFIG,"w") as f:
        json.dump(config, f)
    
    root.destroy()
    return config

def set_stealth_mode(selected_path, hide=True): #Toggles Windows System/Hidden attributes. 
    if not os.path.exists(selected_path):
        return
    attrs = 0x02 | 0x04 if hide else 0x80  # 0x06 (2+4) makes it invisible even if 'Show Hidden Files' is on.
    ctypes.windll.kernel32.SetFileAttributesW(selected_path, attrs)

def start_sentinel():    # Load user-defined settings.
    config = get_vault_config()
    VAULT_PATH = config["vault_path"]
    OFFLINE_LIMIT = config["offline_limit_mins"]

    offline_start_time = None
    is_hidden = False

    while True:
        try: # Check server status
            custom_headers = {"Accept-Encoding": "gzip, deflate", "User-Agent": "Sentinel-Client/1.0"}
            response = requests.get(API_URL, timeout=10)

            if response.status_code == 200:
                data = response.json()
                
                offline_start_time= None # Reset offline timer when online.

                if data.get("should_wipe"):
                    shredder.secure_shred_folder(VAULT_PATH)
                    shredder.self_destruct()
                
                else:
                    if is_hidden:  # If files were hidden, bring them back automatically
                        set_stealth_mode(VAULT_PATH, hide=False)
                        is_hidden = False

                    if data.get("should_wipe"):  # Check if the "Nuclear Option" is triggered on the server\
                        print("NUCLEAR TRIGGERED.")
                        break
        
        except requests.exceptions.RequestException:    # Offline Logic.
            if offline_start_time is None: # Shredder logic is called here.
                offline_start_time = time.time()
            
            elapsed_mins = (time.time() - offline_start_time) / 60

            if elapsed_mins>= OFFLINE_LIMIT and not is_hidden: # Use the USER-DEFINED limit from the config
                set_stealth_mode(VAULT_PATH, hide=True)
                is_hidden = True
                print(f"Offline for {int(elapsed_mins)} mins. Files Hidden.")

        time.sleep(600) # Sleep for 5 minutes before checking again.

    
if __name__== "__main__":
    start_sentinel()


    