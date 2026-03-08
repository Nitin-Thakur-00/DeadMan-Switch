# Dead Man's Switch

> **A Tiered, Remote-Controlled Security Ecosystem that protects local data through stealth, Win32 kernel deception, and cryptographic shredding.**


## Overview
**Sentinel** is not just a hidden folder; it is a proactive defense perimeter for Windows environments, specifically optimized for **Dell G15** hardware. Using a **Zero-Trust tri-modular architecture**, it monitors system "heartbeats" and executes defensive payloads based on remote telemetry.

Unlike standard encryption tools, Sentinel uses **Adaptive Tiered Defense**:
1.  **Stealth Mode:** Automatically hides the vault from the OS kernel using Win32 API attributes if the device stays offline too long.
2.  **Nuclear Mode:** If triggered via the dashboard, it **shreds** data by overwriting it with random bitstreams, making forensic recovery impossible, followed by a full **Self-Destruction** of the client.

---

## Key Features
* **Win32 Kernel Integration:** Uses `ctypes` to manipulate `SYSTEM` and `HIDDEN` attributes, making folders invisible even if "Show Hidden Files" is enabled.
* **Self-Destructing Docs:** The FastAPI `/docs` interface automatically locks (404) once the system is initialized with a Master Token.
* **Anti-Forensic Shredding:** Implements cryptographic wipes that overwrite target sectors multiple times to defeat professional recovery tools.
* **Cyberpunk Dashboard:** An immersive, high-fidelity remote control interface built with **GSAP** for real-time monitoring.
* **Latency Compensation:** Features local ticking logic for smooth TTL displays while maintaining low-frequency server polling.
* **Zero-Trust Handshake:** Requires a high-complexity Master Token to authorize state changes or "Pulse" signals.

---

## File Structure

| File Name | Description |
| :--- | :--- |
| **`main.py`** | **The Command Center.** FastAPI server managing system states and the Master Token handshake. |
| **`index.html`** | **The Interface.** The core dashboard structure featuring the Cyberpunk aesthetic and GSAP animations. |
| **`static/script.js`** | **The Logic.** Manages authentication, smooth TTL countdowns, and real-time polling to the backend. |
 **`static/style.css`** | **The Logic.** Defines the visual presentation and layout of the website. |
| **`sentinel.pyw`** | **The Guardian.** A stealth background service that monitors connectivity and executes local protocols. |
| **`shredder.py`** | **The Payload.** Contains the anti-forensic overwriting logic and the final self-destruct sequence. |
| **`requirements.txt`** | **The Tools.** List of all Python libraries needed to run the ecosystem. |

---

## Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/Nitin-Thakur-00/Sentinel.git](https://github.com/Nitin-Thakur-00/Sentinel.git)
cd Sentinel
```

### 2. Install Dependencies
```Bash
pip install -r requirements.txt
```
## How to Run?
To activate the full defensive perimeter, you must run 3 separate components in sequence.

### Terminal 1: The Command Center (Server)
Start the API hub that listens for your phone and laptop signals.
```Bash
python main.py
Navigate to http://localhost:8000/docs to set your Master Token.
```
* This page will self-destruct after initialization.

### Terminal 2: The Stealth Sentinel (Client Build)
For professional deployment, compile the script into a standalone executable to ensure background persistence.
```Bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name="SystemSentinel" sentinel.pyw
```
* Run SystemSentinel.exe from the dist/ folder.
* Select your Vault Directory and set the Offline Limit.

### Terminal 3: The Dashboard (Remote)
* Open the URL provided in the server terminal on your smartphone.

* Enter your Master Token to decrypt the controls.

* Toggle the system to ARMED to begin active monitoring.

---

## ⚠️ Critical Warnings

* Permanent Data Loss: The Nuclear Trigger is permanent. Shredded data cannot be recovered.

* Privacy: Never push config.json or local_config.json to GitHub, as they contain your Master Token and local paths.
