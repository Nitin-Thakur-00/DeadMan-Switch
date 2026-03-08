// ==========================================
// SENTINEL PRO v2 - DASHBOARD LOGIC
// ==========================================

// --- 1. Global State & Config ---
const API_BASE = window.location.origin;
let MASTER_TOKEN = sessionStorage.getItem("sentinel_token");
let failedAttempts = 0;
const MAX_TRIES = 5;
let secondsRemaining = 0;

// Catch hidden mobile errors
window.onerror = function(msg, url, linenumber) {
    console.error('JS Error: ' + msg + '\nOn line: ' + linenumber);
    return true;
};

// --- 2. Initialization & Auth ---
document.addEventListener("DOMContentLoaded", () => {
    checkExistingAuth();
    startLocalClock();
    setInterval(syncWithServer, 10000); // Poll server every 10s
});

async function checkExistingAuth() {
    if (MASTER_TOKEN) {
        const isValid = await verifyToken(MASTER_TOKEN);
        if (isValid) {
            hideOverlay();
            syncWithServer();
        } else {
            sessionStorage.removeItem("sentinel_token");
            MASTER_TOKEN = null;
        }
    }
}

// --- 3. The Handshake (Login) ---
async function unlockSentinel() {
    const input = document.getElementById('tokenInput');
    const errorMsg = document.getElementById('errorMsg');
    
    if (!input || !input.value) {
        errorMsg.innerText = "TOKEN FIELD REQUIRED";
        return;
    }

    const token = input.value;

    try {
        const response = await fetch(`${API_BASE}/status`, {
            method: 'GET',
            headers: { 'token': token }
        });

        if (response.ok) {
            // SUCCESS
            sessionStorage.setItem("sentinel_token", token);
            MASTER_TOKEN = token;
            failedAttempts = 0;
            hideOverlay();
            syncWithServer();
        } else if (response.status === 404) {
            errorMsg.innerText = "⚠️ SYSTEM NOT INITIALIZED ON HOST PC";
        } else if (response.status === 401) {
            // SECURITY LOCKOUT LOGIC
            failedAttempts++;
            const remaining = MAX_TRIES - failedAttempts;
            
            if (remaining <= 0) {
                errorMsg.innerText = "☢️ SYSTEM TERMINATED: MAX TRIES EXCEEDED";
                errorMsg.style.color = "red";
            } else {
                errorMsg.innerText = `❌ ACCESS DENIED: ${remaining} TRIES LEFT`;
            }
            // GSAP Shake Effect
            gsap.to("#tokenInput", { x: 10, duration: 0.1, repeat: 5, yoyo: true });
        } else {
            errorMsg.innerText = "UNKNOWN SERVER ERROR";
        }
    } catch (err) {
        console.error(err);
        errorMsg.innerText = "OFFLINE: CANNOT REACH COMMAND CENTER";
    }
}

async function verifyToken(token) {
    try {
        const res = await fetch(`${API_BASE}/status`, {
            headers: { 'token': token }
        });
        return res.ok; 
    } catch (err) {
        return false;
    }
}

function hideOverlay() {
    const lock = document.getElementById('lockScreen');
    if (lock) {
        gsap.to("#lockScreen", {
            opacity: 0, 
            duration: 0.8, 
            ease: "power2.inOut",
            onComplete: () => lock.style.display = 'none'
        });
    }
}

// --- 4. Interactive Dashboard Controls ---

// Pulse Button Logic
document.getElementById('pulse-btn').addEventListener('click', async () => {
    if (!MASTER_TOKEN) return;

    try {
        const response = await fetch(`${API_BASE}/pulse`, {
            method: 'POST',
            // Notice: /pulse uses 'x-token' per our FastAPI setup
            headers: { 'x-token': MASTER_TOKEN } 
        });

        if (response.ok) {
            // GSAP Expanding Ring Animation
            gsap.fromTo(".pulse-ring", 
                { scale: 1, opacity: 1 }, 
                { scale: 2.5, opacity: 0, duration: 0.8, ease: "power2.out" }
            );
            syncWithServer(); // Immediately update the timer
        } else {
            location.reload(); // Boot if token became invalid
        }
    } catch (err) {
        console.error("Pulse Failed", err);
    }
});

// Toggle (Arm/Disarm) Logic
document.getElementById('toggle-btn').addEventListener('click', async () => {
    if (!MASTER_TOKEN) return;
    
    const btn = document.getElementById('toggle-btn');
    const isCurrentlyArmed = btn.innerText === "ARMED";
    const nextState = !isCurrentlyArmed;

    try {
        const res = await fetch(`${API_BASE}/toggle?status=${nextState}`, {
            method: 'POST',
            headers: { 'token': MASTER_TOKEN }
        });

        if (res.ok) {
            updateToggleUI(nextState);
        } else {
            location.reload();
        }
    } catch (err) {
        console.error("Toggle Failed");
    }
});

function updateToggleUI(isArmed) {
    const btn = document.getElementById('toggle-btn');
    if (isArmed) {
        btn.innerText = "ARMED";
        btn.className = "status-on w-full py-2 font-bold tracking-wider transition-all duration-300";
    } else {
        btn.innerText = "DISARMED";
        btn.className = "status-off w-full py-2 font-bold tracking-wider border border-gray-700 text-gray-400 transition-all duration-300";
    }
}

// --- 5. The 5-Second Panic Button (Nuclear Option) ---
const panicBtn = document.getElementById('panic-btn');
const panicProgress = document.getElementById('panic-progress');
const panicText = document.getElementById('panic-text');

let holdTimer;
const holdDuration = 5000; 

const startHold = (e) => {
    if (!MASTER_TOKEN) return;
    if (e) e.preventDefault(); // Stop mobile haptic/scroll interference
    
    panicText.innerText = "HOLDING...";
    panicBtn.style.borderColor = "#ef4444"; // Turn border red
    
    // Smooth CSS transition for the red fill bar
    panicProgress.style.transition = `width ${holdDuration}ms linear`;
    panicProgress.style.width = '100%';

    holdTimer = setTimeout(() => {
        executePurge();
    }, holdDuration);
};

const cancelHold = () => {
    clearTimeout(holdTimer);
    panicText.innerText = "HOLD 5s TO PURGE";
    panicBtn.style.borderColor = "rgba(127, 29, 29, 0.5)"; // Reset border
    
    // Snap the red bar back to 0 instantly
    panicProgress.style.transition = 'none';
    panicProgress.style.width = '0%';
};

async function executePurge() {
    try {
        const res = await fetch(`${API_BASE}/panic`, {
            method: 'POST',
            headers: { 'token': MASTER_TOKEN }
        });

        if (res.ok) {
            // Visual feedback before reload
            panicText.innerText = "TERMINATED";
            panicProgress.style.backgroundColor = "#ff0000";
            
            setTimeout(() => {
                sessionStorage.clear();
                window.location.reload();
            }, 1000);
        }
    } catch (err) {
        alert("CRITICAL ERROR: SERVER UNREACHABLE");
    }
}

// Bind Panic Events - Using proper option objects for Mobile
panicBtn.addEventListener('mousedown', startHold);
panicBtn.addEventListener('mouseup', cancelHold);   
panicBtn.addEventListener('mouseleave', cancelHold);

// Mobile Touch Events with Passive: False to allow preventDefault()
panicBtn.addEventListener('touchstart', startHold, { passive: false });
panicBtn.addEventListener('touchend', cancelHold, { passive: false });

// --- 6. Synchronization & Background Clock ---

async function syncWithServer() {
    if (!MASTER_TOKEN) return;
    
    try {
        const res = await fetch(`${API_BASE}/status`, {
            headers: { 'token': MASTER_TOKEN }
        });
        
        if (res.status === 401) location.reload(); 
        
        const data = await res.json();
        
        // Sync Time
        secondsRemaining = data.seconds_remaining;
        
        // Sync Toggle UI
        updateToggleUI(data.is_active);

        // Sync Connection Status
        const statusEl = document.getElementById('connection-status');
        if (data.should_wipe) {
            statusEl.innerText = "☢️ PURGE IN PROGRESS";
            statusEl.style.color = "red";
        } else {
            statusEl.innerText = "● SYSTEM LINK ACTIVE";
            statusEl.style.color = "#22d3ee"; // Cyan
        }
    } catch (err) {
        const statusEl = document.getElementById('connection-status');
        statusEl.innerText = "● OFFLINE";
        statusEl.style.color = "red";
    }
}

function startLocalClock() {
    setInterval(() => {
        const timerDisplay = document.getElementById('timer-display');
        
        if (secondsRemaining > 0) {
            secondsRemaining--;
            const h = Math.floor(secondsRemaining / 3600);
            const m = Math.floor((secondsRemaining % 3600) / 60);
            const s = Math.floor(secondsRemaining % 60);
            timerDisplay.innerText = 
                `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
            timerDisplay.style.color = "#22d3ee";
        } else if (secondsRemaining === 0) {
            timerDisplay.innerText = "00:00:00";
            timerDisplay.style.color = "red";
        }
    }, 1000);
}