import os
import sys
import shutil
import random
import subprocess
import string
import json
import time

def secure_shred_file(filepath, passes=3):
    """
    Overwrites a file with random data multiple times to prevent forensic recovery,
    then renames it to destroy filename metadata before final deletion.
    """
    if not os.path.exists(filepath): return
    try:
        file_size = os.path.getsize(filepath)
        with open(filepath, "ba+", buffering=0) as f:
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(file_size))
        dir_name = os.path.dirname(filepath)
        random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16)) + ".tmp"
        scrambled_path = os.path.join(dir_name, random_name)
        os.rename(filepath, scrambled_path)
        os.remove(scrambled_path)
    except Exception as e:
        print(f"⚠️ Shredding failed for {filepath}, Error: {e}")
        try: os.remove(filepath)
        except: pass

def log_shred_event(path):
    """Logs the details of a shredded folder to a history file."""
    app_data_dir = os.path.join(os.environ['APPDATA'], 'SentinelDefense')
    if not os.path.exists(app_data_dir): os.makedirs(app_data_dir)
    history_path = os.path.join(app_data_dir, 'shred_history.json')
    event = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "folder_name": os.path.basename(path),
        "full_path": path,
        "status": "PERMANENTLY_DESTROYED"
    }
    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path, "r") as f: history = json.load(f)
        except json.JSONDecodeError: history = [] 
    history.append(event)
    with open(history_path, "w") as f: json.dump(history, f, indent=4)

def secure_shred_folder(folder_path):
    """
    Recursively shreds all files inside a vault, then removes the empty directories.
    """
    if not os.path.exists(folder_path): return
    print(f"☢️ INITIATING VAULT SHRED: {folder_path}")
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files: secure_shred_file(os.path.join(root, name))
        for name in dirs:
            dir_path = os.path.join(root, name)
            try: os.rmdir(dir_path)
            except OSError: shutil.rmtree(dir_path, ignore_errors=True)
    try: shutil.rmtree(folder_path, ignore_errors=True)
    except: pass
    log_shred_event(folder_path)

def self_destruct():
    import subprocess, os, sys
    
    # --- THE PYINSTALLER PATH FIX ---
    if getattr(sys, 'frozen', False):
        # If running as a compiled .exe, get the folder where the .exe is sitting
        project_root = os.path.dirname(sys.executable)
    else:
        # If running as a standard Python script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, ".."))
        
    app_data = os.path.join(os.environ['APPDATA'], 'SentinelDefense')
    temp_bat = os.path.join(os.environ['TEMP'], "sentinel_internal_wipe.bat")

    batch_script = f"""@echo off
title SENTINEL_FINAL_PURGE

:: Clear Windows Recent Files securely
del /F /Q "%APPDATA%\\Microsoft\\Windows\\Recent\\*.*" >nul 2>&1

:: Force kill standard Python terminals
taskkill /F /IM "python.exe" /T >nul 2>&1
taskkill /F /IM "pythonw.exe" /T >nul 2>&1
taskkill /F /IM "powershell.exe" /T >nul 2>&1

:: Force kill Compiled Sentinel Executables
taskkill /F /IM "Sentinel_Server.exe" /T >nul 2>&1
taskkill /F /IM "Sentinel_Dashboard.exe" /T >nul 2>&1

:: Silently ping localhost for ~3 seconds to ensure file locks drop
ping 127.0.0.1 -n 4 > nul

:wipe_appdata
rd /s /q "{app_data}" >nul 2>&1
if exist "{app_data}" (
    ping 127.0.0.1 -n 2 > nul
    goto wipe_appdata
)

:wipe_project
:: Wipe all files and subdirectories first
del /f /s /q "{project_root}\\*.*" >nul 2>&1
for /d %%p in ("{project_root}\\*") do rd /s /q "%%p" >nul 2>&1

:: Try to delete the root folder as the final step
cd /d "%TEMP%"
rd /s /q "{project_root}" >nul 2>&1

:: Delete the batch script itself
(goto) 2>nul & del "%~f0"
"""
    with open(temp_bat, "w") as f:
        f.write(batch_script)

    # 0x08000000 = CREATE_NO_WINDOW (100% invisible execution)
    try:
        subprocess.Popen([temp_bat], creationflags=0x08000000)
    except Exception:
        os.startfile(temp_bat) 

    os._exit(0)
    
if __name__ == "__main__":
    print("Shredder module loaded.")