from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from datetime import datetime
import json
import re
import os
import socket

# --- 1. Custom Swagger CSS ---
custom_swagger_css = """
.swagger-ui { background-color: #0a0a0a; color: #00f3ff; }
.swagger-ui .topbar { background-color: #000; border-bottom: 2px solid #00f3ff; }
.swagger-ui .info .title, .swagger-ui .info p, .swagger-ui .opblock-summary-path { color: #00f3ff !important; font-family: 'Courier New', monospace; }
.swagger-ui .opblock.opblock-post { background: rgba(0, 243, 255, 0.05); border-color: #00f3ff; }
.swagger-ui .btn.execute { background-color: #00f3ff; color: #000; border: none; }
.swagger-ui section.models { background-color: #111; border: 1px solid #333; }
"""

# Disable default docs to use our custom styled version
app = FastAPI(docs_url=None, redoc_url=None) 
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins (phone, laptop, etc.)
    allow_credentials=True,
    allow_methods=["*"], # Allows POST, GET, OPTIONS, etc.
    allow_headers=["*"], # Allows your custom x-token header
)

app.mount("/static", StaticFiles(directory="static"), name="static")

DB_FILE = "pulse_db.json"
CONFIG_FILE = "config.json"

# --- Utility Functions ---
def load_config():
    if not os.path.exists(CONFIG_FILE): return None
    with open(CONFIG_FILE, "r") as f: return json.load(f)

def save_json(filepath, data):
    with open(filepath, "w") as f: json.dump(data, f)

def is_token_strong(token: str) -> bool:
    if len(token) < 12: return False
    if not re.search(r"[a-z]", token): return False
    if not re.search(r"[A-Z]", token): return False
    if not re.search(r"\d", token): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", token): return False
    return True

# --- Routes ---

@app.middleware("http")
async def lock_docs_middleware(request, call_next):
    # If the system is initialized, block access to any engineering paths
    if os.path.exists(CONFIG_FILE):
        forbidden_paths = ["/docs", "/openapi.json", "/docs/custom.css"]
        if request.url.path in forbidden_paths:
            raise HTTPException(status_code=404)
    
    response = await call_next(request)
    return response

    
# To actually get the CSS to apply, we need to add a middleware 
# or a simple override to the response. 
# Here is the easiest way: add this global CSS override.
@app.get("/docs/custom.css", include_in_schema=False)
async def get_custom_css():
    return Response(content=custom_swagger_css, media_type="text/css")


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1 style='color:red'>Error: index.html not found. Check your directory!</h1>"

@app.post("/initialise")
async def initialise_system(x_token: str = Header(None), hours: int = 24):
    if load_config() is not None:
        raise HTTPException(status_code=400, detail="System already initialised.")
    
    if not x_token or not is_token_strong(x_token):
        raise HTTPException(status_code=400, detail="Token too weak! Needs 12+ chars, Upper, Lower, Num, and Symbol.")

    config_data = {"master_token": x_token, "threshold_hours": hours, "is_active": False}
    save_json(CONFIG_FILE, config_data)
    save_json(DB_FILE, {"last_seen": datetime.now().isoformat()})
    return {"status": "Initialised", "Duration": f"{hours} hours"}

@app.post("/pulse")
async def pulse(x_token: str = Header(None)):
    config = load_config()
    if not config or x_token != config["master_token"]:
        raise HTTPException(status_code=403, detail="Invalid or missing token.")
    save_json(DB_FILE, {"last_seen": datetime.now().isoformat()})
    return {"Status": "Success"}

@app.post("/toggle")
async def toggle_switch(status: bool, x_token: str = Header(None)):
    config = load_config()
    
    # DEBUG PRINTS (Remove these after fixing)
    print(f"DEBUG: Received Token -> '{x_token}'")
    print(f"DEBUG: Master Token   -> '{config['master_token']}'")
    
    if not config or x_token != config["master_token"]:
        raise HTTPException(status_code=403, detail="Unauthorized.")
    
    # ... rest of your code
    
    config["is_active"] = status
    save_json(CONFIG_FILE, config)
    
    return {"Status": "Updated", "Switch_State": "Active" if status else "Inactive"}


@app.get("/status")
async def status():
    config = load_config()
    if config is None or not os.path.exists(DB_FILE):
        return {"is_active": False, "should_wipe": False, "seconds_remaining": 0}
    
    with open(DB_FILE, "r") as f:
        pulse_data = json.load(f)

    last_seen = datetime.fromisoformat(pulse_data["last_seen"])
    elapsed_seconds = (datetime.now() - last_seen).total_seconds()
    limit_seconds = config["threshold_hours"] * 3600
    time_expired = elapsed_seconds > limit_seconds

    return {
        "is_active": config["is_active"],
        "time_expired": time_expired,
        "should_wipe": config["is_active"] and time_expired,
        "seconds_remaining": max(0, limit_seconds - elapsed_seconds)
    }


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    if os.path.exists(CONFIG_FILE):
        raise HTTPException(status_code=404)

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SENTINEL | Initial Setup",
        # Hiding the "Models" section makes it 100% cleaner
        swagger_ui_parameters={"defaultModelsExpandDepth": -1}, 
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    )

    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SENTINEL - Setup",
        swagger_ui_parameters=swagger_ui_parameters,
        # We inject the CSS directly into the head via a script tag for 'brute force' styling
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css"
    )

@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    if os.path.exists(CONFIG_FILE):
        raise HTTPException(status_code=404)
    from fastapi.openapi.utils import get_openapi
    return get_openapi(title="Sentinel", version="1.0", routes=app.routes)



if __name__ == "__main__":
    import uvicorn
    import socket

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
    print("SENTINEL COMMAND CENTER IS ACTIVE..")
    print("═"*50)
    print(f"Local Dashboard:   http://localhost:8000")
    print(f"Mobile Dashboard:  http://{ip}:8000")
    print("═"*50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)