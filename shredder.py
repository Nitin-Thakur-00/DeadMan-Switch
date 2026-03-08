import os
import secrets
import subprocess
import sys
import json
import time

CONFIG_FILE = "local_config.json"

def secure_shred_folder(folder_path):
    """The 'Nuclear' logic: Overwrites, Renames, and Deletes a specific path."""
    if not folder_path or not os.path.exists(folder_path):
        print(f"Error: Path {folder_path} does not exist.")
        return
    
    # Image of a secure data shredding process illustrating overwriting data with random bits
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            try:
                # 1. Overwrite with random data to prevent forensic recovery
                size = os.path.getsize(file_path)
                with open(file_path, "wb") as f:
                    f.write(secrets.token_bytes(size))

                # 2. Rename to scramble metadata
                random_name = secrets.token_hex(8)
                new_path = os.path.join(root, random_name)
                os.rename(file_path, new_path)

                # 3. Final Delete
                os.remove(new_path)
                print(f"Successfully Shredded: {name}")
            except Exception as e: # Fixed: changed 'exception' to 'Exception'
                print(f"Failed to shred {name}: {e}")
            
        for name in dirs:  # Remove empty directories
            try:
                os.rmdir(os.path.join(root, name))
            except:
                pass
    
    # Final cleanup of the root protected folder itself
    try:
        if os.path.isdir(folder_path):
            os.rmdir(folder_path)
    except:
        pass

def self_destruct():
    import os, sys, subprocess
    
    exe_path = os.path.abspath(sys.argv[0])
    project_dir = os.path.dirname(os.path.dirname(exe_path)) # Parent of EXE
    
    # Target the new AppData folder
    app_data_dir = os.path.join(os.environ['APPDATA'], 'SentinelDefense')

    batch_content = f"""@echo off
timeout /t 3 /nobreak > nul
taskkill /f /im "{os.path.basename(exe_path)}" /t > nul 2>&1
echo Wiping Application Data...
rd /s /q "{app_data_dir}"
echo Wiping Project Files...
rd /s /q "{project_dir}"
(goto) 2>nul & del "%~f0"
"""
    
    with open("cleanup.bat", "w") as f:
        f.write(batch_content)
        
    subprocess.Popen(["cmd.exe", "/c", "cleanup.bat"], shell=True)
    sys.exit(0)


if __name__ == "__main__":
    # Manual Panic Execution for all vaults in config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            vaults = config.get("vaults", [])
        
        if vaults:
            print(" MANUAL PANIC EXECUTION TRIGGERED!")
            input("Press ENTER to confirm full system wipe, or close this window to cancel.")
            
            for vault in vaults:
                print(f"Targeting: {vault['path']}")
                secure_shred_folder(vault['path'])
            
            self_destruct()
        else:
            print("No vaults found in configuration.")
    else:
        print("No local_config.json found. Please initialize Sentinel Pro first.")