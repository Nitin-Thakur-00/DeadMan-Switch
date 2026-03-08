Sentinel v2.0 | Dead Man's Switch
=================================

> **A Tiered, Remote-Controlled Security Ecosystem protecting local data through stealth, Win32 kernel deception, and cryptographic shredding.**

Overview
--------

Sentinel v2.0 transitions from a script-based project into a fully compiled, portable security suite. It utilizes a **Zero-Trust tri-modular architecture** to execute defensive payloads based on remote telemetry and local heartbeat monitoring.

Unlike standard encryption tools, Sentinel uses **Adaptive Tiered Defense**:

*   **Stealth Mode:** Automatically hides vault folders from the OS kernel using Win32 API attributes (0x02 | 0x04) if the device loses connection to the server.
    
*   **Nuclear Mode:** Triggered via the mobile dashboard or offline timeout, it shreds data by overwriting it with random bitstreams and initiates a **Total Self-Destruction** of the project directory.
    

🆕 WHAT'S NEW in v2.0
---------------------

*   **Decoupled UI Logic:** Features a zero-latency 30-second warning window that remains synchronized with the backend even under high CPU load.
    
*   **Brute-Force Protection:** The Command Center implements a strike counter that triggers an auto-purge if an incorrect token is entered 5 times via the web interface.
    
*   **Anti-Forensic Shredding:** Implements cryptographic wipes that overwrite target sectors multiple times to defeat professional recovery tools, followed by filename metadata scrambling.
    
*   **Portable Binary Architecture:** Compiled into standalone executables that carry their own Python environment, allowing deployment on any Windows machine without pre-installed dependencies.
    
*   **Ghost Protocol Deletion:** Uses a detached, invisible batch script to bypass Windows "File in Use" locks, ensuring a 100% clean wipe of the root project folder.
    

Key Features
------------

*   **Zero-Latency Sync:** A high-precision timer system using math.ceil logic to ensure the mobile dashboard, local GUI, and warning alerts are locked to the same second.
    
*   **Secure Handshake:** Requires a high-complexity Master Token (8+ chars, Uppercase, Number, & Symbol) to authorize state changes or "Pulse" signals.
    
*   **Shred History:** A persistent local log in AppData that records timestamps and folder names of all successful destruction events.
    
*   **Customizable Aesthetics:** Built-in theme engine supporting Dark, Light, Translucent, and fully custom HEX-coded UI backgrounds.
    

File Structure
--------------

**PathDescriptionSentinel\_Server.exeThe Command Center.** The compiled FastAPI server managing system states and the mobile handshake.**Sentinel\_Dashboard.exeThe Guardian.** The compiled local GUI for managing vaults, themes, and offline limits.**index.htmlThe Interface.** The core mobile dashboard served by the Command Center.**static/The Logic Assets.** Contains script.js and style.css required for the web dashboard.**Sentinel\_v2/Source Code.** Contains the modular sentinel\_v2.pyw and the shredder.py payload.**requirements.txtThe Tools.** Precisely versioned libraries for environment replication.

Installation & Build
--------------------

### 1\. Environment Setup

PowerShell

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   python -m venv .venv  .\.venv\Scripts\activate  pip install -r requirements.txt   `

### 2\. Compilation

To generate portable binaries, run these commands. **Strict Requirement:** Move the resulting .exe files from dist/ to the **Root Folder** after completion.

**Build Command Center:**

PowerShell

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pyinstaller --onefile --name "Sentinel_Server" --hidden-import="uvicorn.logging" --hidden-import="uvicorn.loops" --hidden-import="uvicorn.loops.auto" --hidden-import="uvicorn.protocols" --hidden-import="uvicorn.protocols.http" --hidden-import="uvicorn.protocols.http.auto" --hidden-import="uvicorn.lifespan" --hidden-import="uvicorn.lifespan.on" main.py   `

**Build Local Dashboard:**

PowerShell

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML`   pyinstaller --noconsole --onefile --name "Sentinel_Dashboard" --collect-all customtkinter "Sentinel_v2\sentinel_v2.pyw"   `

How to Run?
-----------

The system must be activated in the following sequence to maintain the Zero-Trust handshake:

### Step 1: The Command Center (Sentinel\_Server.exe)

*   Note the **Mobile Dashboard IP** provided in the terminal.
    

### Step 2: The Guardian (Sentinel\_Dashboard.exe)

*   Initialize your Master Token (8+ chars, Upper, Number, & Symbol).
    
*   Add your target Vaults and set specific **Offline Limits**.
    

### Step 3: The Remote Dashboard

*   Access the IP on your smartphone and enter the Master Token.
    
*   Toggle the system to **ARMED** to begin active monitoring.
    

⚠️ Critical Warnings
--------------------

*   **Permanent Data Loss:** The Nuclear Trigger is irreversible. Shredded data cannot be recovered by forensic software.
    
*   **Operational Order:** Starting the Dashboard before the Server will result in a connection error.
    
*   **Privacy:** Never push local\_config.json, pulse\_db.json, or shred\_history.json to GitHub, as they contain your Master Token and forensic logs.
    
*   **Space Bug:** Avoid project paths with excessive spaces; while v2.0 includes quote-handling fixes, the system remains optimized for standard Windows user directories.
