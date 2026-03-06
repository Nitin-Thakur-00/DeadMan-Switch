// Use the current window location to avoid hardcoding IP addresses
const API_BASE = window.location.origin;

let MASTER_TOKEN = sessionStorage.getItem("sentinel_token");

// 1. Initial Auth Check
if (MASTER_TOKEN) {
    document.getElementById('login-overlay').style.display = 'none';
    updateStatus(); // Start polling if already logged in
}

// 2. Save Token (Login)
function saveToken() {
    const input = document.getElementById('token-input').value;
    if (input.length > 0) {
        sessionStorage.setItem("sentinel_token", input);
        MASTER_TOKEN = input;

        gsap.to("#login-overlay", {
            opacity: 0, duration: 0.5, onComplete: () => {
                document.getElementById('login-overlay').style.display = 'none';
            }
        });
        updateStatus();
    }
}

// --- Animations ---
gsap.to(".pulse-ring", {
    scale: 1.5,
    opacity: 0,
    duration: 2,
    repeat: -1,
    ease: "expo.out"
});

// --- UI Interactions ---

// 3. Send Pulse (Heartbeat)
document.getElementById('pulse-btn').addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_BASE}/pulse`, {
            method: 'POST',
            // CRITICAL: Must match the backend Header name exactly
            headers: { 'x-token': MASTER_TOKEN }
        });

        if (response.ok) {
            gsap.fromTo(".pulse-circle",
                { backgroundColor: "rgba(0, 243, 255, 0.4)" },
                { backgroundColor: "transparent", duration: 0.5 }
            );
        } else {
            alert("Pulse Failed: Check Token");
        }
    } catch (err) {
        console.error("Pulse Failed", err);
    }
});

// 4. Unified Toggle Logic
document.getElementById('toggle-btn').addEventListener('click', async () => {
    const btn = document.getElementById('toggle-btn');
    const isCurrentlyArmed = btn.innerText === "ARMED";
    const nextState = !isCurrentlyArmed;

    try {
        // Query param syntax: /toggle?status=true
        const res = await fetch(`${API_BASE}/toggle?status=${nextState}`, {
            method: 'POST',
            headers: { 'x-token': MASTER_TOKEN }
        });

        if (res.ok) {
            btn.innerText = nextState ? "ARMED" : "DISARMED";
            btn.className = nextState ? "status-on" : "status-off";
        } else {
            const err = await res.json();
            alert("Toggle Denied: " + (err.detail || "Check Token"));
        }
    } catch (err) {
        alert("Server Unreachable");
    }
});

// 5. Status Polling

let secondsRemaining = 0;

// Function A: Get the official time from the Server
async function syncWithServer() {
    try {
        const res = await fetch(`${API_BASE}/status`);
        const data = await res.json();

        // Sync our local variable with the server's truth
        secondsRemaining = data.seconds_remaining;

        // Update the connection indicator
        document.getElementById('connection-status').innerText = "● SYSTEM LINK ACTIVE";
        document.getElementById('connection-status').style.color = "#00f3ff";
    } catch (err) {
        document.getElementById('connection-status').innerText = "● OFFLINE";
        document.getElementById('connection-status').style.color = "red";
    }
}

// Function B: The "Smooth Ticker" (Runs every 1 second locally)
function startLocalClock() {
    setInterval(() => {
        if (secondsRemaining > 0) {
            secondsRemaining--; // Drop 1 second locally

            const h = Math.floor(secondsRemaining / 3600);
            const m = Math.floor((secondsRemaining % 3600) / 60);
            const s = Math.floor(secondsRemaining % 60);

            document.getElementById('timer-display').innerText =
                `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

// Start everything
syncWithServer();           // Initial sync
setInterval(syncWithServer, 10000); // Sync with server every 10s to stay accurate
startLocalClock();          // Start the smooth 1s ticker