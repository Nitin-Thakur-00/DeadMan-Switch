from tkinter.filedialog import FileDialog
import subprocess
import os
import secrets
import subprocess
import sys
import json

CONFIG_FILE = "local_config.json"

def get_protected_path():
    """Reads the local config to find what needs to be destroyed."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            return config.get("vault_path")
    return None

def secure_shred_folder(folder_path): #The 'Nuclear' logic: Overwrites, Renames, and Deletes.
    if not folder_path or not os.path.exists(folder_path):
        print(f"Error: Path {folder_path} does not exist.")
        return
    
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files:
            file_path = os.path.join(root,name)
            try:                                             # Overwrite with random data.
                size = os.path.getsize(file_path)
                with open(file_path,"wb") as f:
                    f.write(secrets.token_bytes(size))

                random_name = secrets.token_hex(8)           # Rename to scramble metadata.
                new_path = os.path.join(root, random_name)
                os.rename(file_path,new_path)

                os.remove(new_path)                          # Final Delete.
                print(f"Successfully Shredded: {name}")
            except exception as e:
                print(f"Failed to shred {name}: {e}")
            
        for name in dirs:  # Remove empty directories.
            try:
                os.rmdir(os.path.join(root,name))
            except:
                pass


def self_destruct(): # Generates a script to erase the app itself.
    bath_content = f"""
    @echo off
    timeout /t 3 /nobreak > nul
    del "{sys.argv[0]}"
    if exists "{config_path}" del "{config_path}"
    (goto) 2>nul & del "%`f0"
    """

    with open("cleanup.bat", "w") as f:
        f.write(batch_content)

    subprocess.Popen(["cmd.exe", "/c", "cleanup.bat"], shell = True)
    os.exit(0)

if __name__ == "__main__":  # Manual Execution (PANIC EXCECUTION).
    if vault:
        print(f"MANUAL EXECUTION TRIGGERED !")
        print(f"Targeting: {vault}") 
        confirm = input("Press ENTER to confirm full system wipe, or close this window to cancel.")  # 'Enter' confirmation so you don't accidental click it
        secure_shred_folder(vault)
        self_destruct()
    else:
        print("No protected path found. Please run the Sentinel setup first.")

