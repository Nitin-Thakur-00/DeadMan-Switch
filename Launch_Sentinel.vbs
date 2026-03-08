Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")

' Dynamically get the exact folder where this .vbs file is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Build the paths relative to this folder
pythonExe = scriptDir & "\.venv\Scripts\pythonw.exe"
mainScript = scriptDir & "\main.py"

' Launch silently in the background (0 = hidden window)
WshShell.Run """" & pythonExe & """ """ & mainScript & """", 0, False