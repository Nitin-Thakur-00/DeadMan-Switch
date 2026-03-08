from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json, os, time
import socket

# --- Path Configuration (AppData Integration) ---
def get_sentinel_path(filename):
    """Ensures server and .exe share the exact same configuration directory."""
    base_dir = os.path.join(os.environ['APPDATA'], 'SentinelDefense')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, filename)

LOCAL_CONFIG = get_sentinel_path("local_config.json")
DB_FILE = get_sentinel_path("pulse_db.json")

# --- Security & Core Settings ---
app = FastAPI()
MAX_TRIES = 5
failed_counter = 0  # Tracks failed dashboard login attempts

# Allow CORS for mobile web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
# Note: Ensure you have a 'static' folder in the same directory as main.py
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Helper Functions ---
def load_config():
    """Loads configuration from AppData. Returns {} if missing/empty."""
    if os.path.exists(LOCAL_CONFIG):
        try:
            with open(LOCAL_CONFIG, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

def get_pulse_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"last_pulse": time.time(), "max_offline_limit": 3600}

# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serves the main HTML interface."""
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Error: index.html not found</h1>", status_code=404)

@app.get("/status")
async def check_status(token: str = Header(None)):
    """Validates token and returns current system state."""
    config = load_config()
    
    # 1. System not initialized on the PC yet
    if not config or not config.get("master_token"):
        raise HTTPException(status_code=404, detail="CREATE_TOKEN")

    # 2. Token mismatch
    if token and token != config.get("master_token"):
        raise HTTPException(status_code=401, detail="INVALID_TOKEN")
        
    # 3. Success: Calculate remaining time
    pulse_data = get_pulse_data()
    elapsed = time.time() - pulse_data["last_pulse"]
    remaining = max(0, pulse_data["max_offline_limit"] - elapsed)
        
    return {
        "is_active": config.get("is_active", False),
        "should_wipe": config.get("should_wipe", False),
        "seconds_remaining": int(remaining),
        "initialized": True
    }

@app.post("/pulse")
async def receive_pulse(x_token: str = Header(None)):
    """Receives heartbeat from the dashboard to reset the timer."""
    config = load_config()
    
    # Must match token
    if not config or x_token != config.get("master_token"):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    # Reset pulse timer
    pulse_data = get_pulse_data()
    pulse_data["last_pulse"] = time.time()
    save_json(DB_FILE, pulse_data)
    
    return {"status": "Pulse Acknowledged", "timestamp": pulse_data["last_pulse"]}
@app.post("/toggle")
async def toggle_switch(status: bool, token: str = Header(None)):
    """Arms/Disarms the system, includes Strike Counter."""
    global failed_counter
    config = load_config()

    if not config or not config.get("master_token"):
        raise HTTPException(status_code=404, detail="INITIALIZATION_REQUIRED")

    # Security Strike Logic
    if token != config.get("master_token"):
        failed_counter += 1
        print(f"⚠️ SECURITY ALERT: Failed attempt {failed_counter}/{MAX_TRIES}")
        
        if failed_counter >= MAX_TRIES:
            print("☢️ CRITICAL: MAX TRIES EXCEEDED. INITIATING AUTO-PURGE.")
            config["should_wipe"] = True 
            config["is_active"] = True
            save_json(LOCAL_CONFIG, config)
            raise HTTPException(status_code=401, detail="TERMINATED: MAX TRIES EXCEEDED")
            
        raise HTTPException(status_code=401, detail=f"ACCESS_DENIED: {MAX_TRIES - failed_counter} TRIES LEFT")
    
    # Success: Reset strikes and update standard state (NO PANIC LOGIC HERE)
    failed_counter = 0
    config["is_active"] = status
    save_json(LOCAL_CONFIG, config)
    
    return {"Status": "Updated", "State": status, "Wipe_Flag": config.get("should_wipe", False)}


@app.post("/panic")
async def trigger_panic(token: str = Header(None)):
    """Dedicated endpoint specifically for the 5-second long-press Nuclear Option."""
    config = load_config()
    
    if not config or token != config.get("master_token"):
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    # Trigger the Purge
    config["should_wipe"] = True 
    config["is_active"] = True
    save_json(LOCAL_CONFIG, config)
    
    return {"Status": "PURGE_INITIATED", "Wipe_Flag": True}
if __name__ == "__main__":
    # Runs the server locally. Make sure to update the host to "0.0.0.0" if accessing via mobile on the same network.
    def get_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    ip = get_ip()
    print("\n" + "═"*50)
    print("SENTINEL COMMAND CENTER IS ACTIVE")
    print("═"*50)
    print(f"Local Dashboard:   http://localhost:8000")
    print(f"Mobile Dashboard:  http://{ip}:8000")
    print("═"*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)