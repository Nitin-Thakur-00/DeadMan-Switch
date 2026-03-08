import warnings
warnings.filterwarnings("ignore") 

import customtkinter as ctk
import json, os, time, requests, threading, ctypes, sys, re, math
from tkinter import filedialog, messagebox, colorchooser
import shredder 
import winsound

# --- Path Configuration ---
def get_sentinel_path(filename):
    base_dir = os.path.join(os.environ['APPDATA'], 'SentinelDefense')
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return os.path.join(base_dir, filename)

LOCAL_CONFIG = get_sentinel_path("local_config.json")
API_URL = "http://127.0.0.1:8000/status"

def validate_secure_token(token):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, token))

def get_contrasting_text_color(hex_color):
    if not hex_color or len(hex_color) < 6: return "white"
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return "black" if brightness > 125 else "white"

class SentinelPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw() 
        self.title("SENTINEL PRO - DEFENSE INTERFACE")
        self.geometry("1000x650")
        
        self.current_view = "dashboard"
        self.system_online = False
        self.warning_active = False 
        
        self.load_config()
        self.authenticate_user()

    def load_config(self):
        if os.path.exists(LOCAL_CONFIG):
            with open(LOCAL_CONFIG, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {
                "master_token": None, 
                "vaults": [], 
                "theme": "Dark", 
                "custom_bg": "#1f538d",
                "notifications": "on"
            }

    def save_config(self):
        with open(LOCAL_CONFIG, "w") as f:
            json.dump(self.config, f, indent=4)

    # --- SECURITY: LOGIN GATE ---
    def authenticate_user(self):
        self.login_win = ctk.CTkToplevel(self)
        self.login_win.geometry("450x250")
        self.login_win.title("SYSTEM LOCKED")
        self.login_win.attributes("-topmost", True)
        self.login_win.protocol("WM_DELETE_WINDOW", sys.exit)

        is_new = not self.config.get("master_token")
        if is_new:
            lbl_txt = "INITIALIZE MASTER TOKEN"
            btn_txt = "ACTIVATE SYSTEM"
        else:
            lbl_txt = "ENTER MASTER TOKEN"
            btn_txt = "UNLOCK"
            
        ctk.CTkLabel(self.login_win, text=lbl_txt, font=("Arial", 18, "bold")).pack(pady=(30, 10))
        self.entry = ctk.CTkEntry(self.login_win, placeholder_text="Token", show="*", width=300)
        self.entry.pack(pady=10)

        def verify():
            token = self.entry.get()
            if is_new:
                if validate_secure_token(token):
                    self.config["master_token"] = token
                    self.save_config()
                    self.unlock_system()
                else:
                    messagebox.showerror("Error", "Use 8+ chars, Upper, Number, & Symbol")
            else:
                if token == self.config.get("master_token"):
                    self.unlock_system()
                else:
                    messagebox.showerror("Denied", "Invalid Master Token.")

        ctk.CTkButton(self.login_win, text=btn_txt, command=verify).pack(pady=20)

    def unlock_system(self):
        self.login_win.destroy()
        self.build_main_interface()
        self.apply_theme_settings()
        self.deiconify() 
        self.start_background_monitor()

    # --- UI: MAIN INTERFACE ---
    def build_main_interface(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.title_lbl = ctk.CTkLabel(self.sidebar, text="SENTINEL PRO", font=("Arial", 20, "bold"))
        self.title_lbl.pack(pady=30)
        
        self.btn_dash = ctk.CTkButton(self.sidebar, text="DASHBOARD", fg_color="transparent", command=self.show_dashboard)
        self.btn_dash.pack(pady=10, padx=20, fill="x")
        
        self.btn_settings = ctk.CTkButton(self.sidebar, text="SETTINGS", fg_color="transparent", command=self.show_settings)
        self.btn_settings.pack(pady=10, padx=20, fill="x")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        self.show_dashboard()

    def apply_theme_settings(self):
        theme = self.config.get("theme", "Dark")
        self.attributes("-alpha", 1.0)
        
        if theme in ["Dark", "Translucent", "Custom"]:
            ctk.set_appearance_mode("dark")
        else:
            ctk.set_appearance_mode("light")
            
        ctk.set_default_color_theme("blue") 
        text_col = ["black", "white"]

        if theme == "Translucent":
            self.attributes("-alpha", 0.90)
            self.configure(fg_color="#050505")
            self.sidebar.configure(fg_color="#0a0a0a")
        elif theme == "Custom":
            bg_color = self.config.get("custom_bg", "#1f538d")
            text_col = get_contrasting_text_color(bg_color)
            self.configure(fg_color=bg_color)
            self.sidebar.configure(fg_color=bg_color)
        else:
            if theme == "Dark":
                self.configure(fg_color="#111111")
                self.sidebar.configure(fg_color="#1c1c1c")
            else:
                self.configure(fg_color="#F0F2F5")
                self.sidebar.configure(fg_color="#E5E7EB")

        self.title_lbl.configure(text_color=text_col)
        self.btn_dash.configure(text_color=text_col)
        self.btn_settings.configure(text_color=text_col)

    def change_theme(self, choice):
        self.config["theme"] = choice
        if choice == "Custom":
            color = colorchooser.askcolor(title="Select Dashboard Theme Color")[1]
            if color:
                self.config["custom_bg"] = color
            else:
                self.config["theme"] = "Dark"
                
        self.save_config()
        self.apply_theme_settings()
        
        if self.current_view == "settings":
            self.show_settings()
        else:
            self.show_dashboard()

    # --- UI: DASHBOARD ---
    def show_dashboard(self):
        self.current_view = "dashboard"
        self.clear_container()
        
        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        if self.config.get("theme") == "Custom":
            text_col = get_contrasting_text_color(self.config.get("custom_bg"))
        else:
            text_col = ["black", "white"]
            
        ctk.CTkLabel(header, text="PROTECTED VAULTS", font=("Arial", 24, "bold"), text_color=text_col).pack(side="left")
        ctk.CTkButton(header, text="+ ADD VAULT", width=120, command=self.add_vault).pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent")
        self.scroll_frame.pack(fill="both", expand=True)
        self.refresh_vault_display()

    def add_vault(self):
        path = filedialog.askdirectory()
        if path:
            limit = ctk.CTkInputDialog(text="Offline Limit (Minutes):", title="Timer").get_input()
            if limit and limit.isdigit():
                self.config["vaults"].append({"path": path, "limit": int(limit), "is_hidden": False, "off_start": None})
                self.save_config()
                self.refresh_vault_display()

    def refresh_vault_display(self):
        if not hasattr(self, 'scroll_frame') or not self.scroll_frame.winfo_exists():
            return
            
        for w in self.scroll_frame.winfo_children():
            w.destroy()
            
        for v in self.config["vaults"]:
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5, padx=5)
            
            lbl = ctk.CTkLabel(card, text=f"📁 {os.path.basename(v['path'])}", font=("Arial", 16, "bold"), cursor="hand2")
            lbl.pack(side="left", padx=20, pady=15)
            lbl.bind("<Button-1>", lambda e, vault=v: self.show_vault_details(vault))

            shred_btn = ctk.CTkButton(card, text="☢ SHRED", fg_color="#e74c3c", width=80, command=lambda p=v['path']: self.manual_shred(p))
            shred_btn.pack(side="right", padx=10)

    # --- UI: VAULT DETAILS ---
    def show_vault_details(self, vault):
        self.current_view = "details"
        self.clear_container()
        
        if self.config.get("theme") == "Custom":
            text_col = get_contrasting_text_color(self.config.get("custom_bg"))
        else:
            text_col = ["black", "white"]

        detail_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        detail_frame.pack(fill="both", expand=True, pady=40)

        ctk.CTkLabel(detail_frame, text=f"📂 {os.path.basename(vault['path'])}", font=("Arial", 28, "bold"), text_color=text_col).pack()
        
        path_box = ctk.CTkTextbox(detail_frame, height=40, font=("Consolas", 12))
        path_box.pack(pady=10, padx=50, fill="x")
        path_box.insert("0.0", vault['path'])
        path_box.configure(state="disabled")

        ctk.CTkLabel(detail_frame, text="COUNTDOWN STATUS", font=("Arial", 14), text_color=text_col).pack(pady=(30,0))
        
        self.timer_label = ctk.CTkLabel(detail_frame, text="--:--:--", font=("Courier New", 48, "bold"), text_color="#e74c3c")
        self.timer_label.pack(pady=10)

        ctk.CTkButton(detail_frame, text="← BACK TO DASHBOARD", command=self.show_dashboard).pack(pady=40)
        self.update_live_timer(vault)

    def update_live_timer(self, vault):
        if self.current_view != "details" or not hasattr(self, 'timer_label') or not self.timer_label.winfo_exists():
            return

        if self.system_online:
            self.timer_label.configure(text="PAUSED (ONLINE)", text_color="#2ecc71")
        elif vault.get("off_start"):
            raw_rem = max(0, (vault["limit"] * 60) - (time.time() - vault["off_start"]))
            rem_ceil = math.ceil(raw_rem) 
            h = int(rem_ceil // 3600)
            m = int((rem_ceil % 3600) // 60)
            s = int(rem_ceil % 60)
            self.timer_label.configure(text=f"{h:02d}:{m:02d}:{s:02d}", text_color="#e74c3c")
        else:
            self.timer_label.configure(text="AWAITING OFFLINE", text_color="gray")
        
        self.after(50, lambda: self.update_live_timer(vault))

    # --- UI: SETTINGS & HISTORY ---
    def show_settings(self):
        self.current_view = "settings"
        self.clear_container()
        
        if self.config.get("theme") == "Custom":
            text_col = get_contrasting_text_color(self.config.get("custom_bg"))
        else:
            text_col = ["black", "white"]
            
        ctk.CTkLabel(self.container, text="SYSTEM SETTINGS", font=("Arial", 24, "bold"), text_color=text_col).pack(pady=(0, 20), anchor="w", padx=10)

        tabs = ctk.CTkTabview(self.container)
        tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        t_app = tabs.add("Appearance")
        t_not = tabs.add("Notifications")
        t_sec = tabs.add("Security")
        t_his = tabs.add("Shred History")
        t_dan = tabs.add("Danger Zone")

        # 1. Appearance
        ctk.CTkLabel(t_app, text="DASHBOARD THEME", font=("Arial", 16, "bold")).pack(pady=15)
        theme_menu = ctk.CTkOptionMenu(t_app, values=["System", "Dark", "Light", "Translucent", "Custom"], command=self.change_theme)
        theme_menu.set(self.config.get("theme", "Dark"))
        theme_menu.pack()

        # 2. Notifications
        ctk.CTkLabel(t_not, text="ALERT PREFERENCES", font=("Arial", 16, "bold")).pack(pady=15)
        self.notif_var = ctk.StringVar(value=self.config.get("notifications", "on"))
        ctk.CTkSwitch(t_not, text="Enable Desktop Alerts", variable=self.notif_var, onvalue="on", offvalue="off", command=self.save_config).pack(pady=10)
        ctk.CTkSwitch(t_not, text="Enable Beep Alarms", onvalue="on", offvalue="off").pack(pady=10)

        # 3. Security
        ctk.CTkLabel(t_sec, text="UPDATE MASTER TOKEN", font=("Arial", 16, "bold")).pack(pady=15)
        self.new_tok_entry = ctk.CTkEntry(t_sec, placeholder_text="New Secure Token", show="*", width=280)
        self.new_tok_entry.pack(pady=10)
        ctk.CTkButton(t_sec, text="SYNC TOKEN", command=self.update_token_logic).pack()

        # 4. Shred History
        history_frame = ctk.CTkScrollableFrame(t_his, fg_color="transparent")
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        history_file = get_sentinel_path("shred_history.json")
        if os.path.exists(history_file):
            with open(history_file, "r") as f:
                logs = json.load(f)
                for log in reversed(logs):
                    item = ctk.CTkFrame(history_frame)
                    item.pack(fill="x", pady=5)
                    ctk.CTkLabel(item, text=f"🕒 {log['timestamp']}", font=("Arial", 10, "italic")).pack(side="left", padx=10)
                    ctk.CTkLabel(item, text=f"🗑️ {log['folder_name']}", font=("Arial", 12, "bold")).pack(side="left", padx=10)
                    ctk.CTkLabel(item, text="[SHREDDED]", text_color="#e74c3c").pack(side="right", padx=10)
        else:
            ctk.CTkLabel(history_frame, text="No history recorded yet.").pack(pady=20)

        # 5. Danger Zone
        ctk.CTkLabel(t_dan, text="NUCLEAR PURGE PROTOCOL", font=("Arial", 16, "bold"), text_color="#e74c3c").pack(pady=15)
        def trigger_global_purge():
            if messagebox.askyesno("WARNING", "Delete Everything?"):
                import shredder
                shredder.self_destruct()
                
        ctk.CTkButton(t_dan, text="☢ INITIATE GLOBAL PURGE", fg_color="#e74c3c", hover_color="#c0392b", command=trigger_global_purge).pack(pady=20)

    def update_token_logic(self):
        new_tok = self.new_tok_entry.get()
        if validate_secure_token(new_tok):
            self.config["master_token"] = new_tok
            self.save_config()
            messagebox.showinfo("Success", "Token Updated.")
        else:
            messagebox.showerror("Failed", "8+ chars, Upper, Number, Symbol required.")

    # --- ALERT: WARNING TIMER SYNC ---
    def show_critical_warning(self, vault):
        if hasattr(self, 'warn_win') and self.warn_win.winfo_exists():
            return 
            
        self.warn_win = ctk.CTkToplevel() 
        self.warn_win.title("⚠️ SYSTEM LOCKDOWN ⚠️")
        self.warn_win.geometry("400x320")
        self.warn_win.attributes("-topmost", True)
        self.warn_win.configure(fg_color="#7b0000")
        
        ctk.CTkLabel(self.warn_win, text="CRITICAL TIMEOUT", font=("Arial", 22, "bold"), text_color="white").pack(pady=20)
        self.count_lbl = ctk.CTkLabel(self.warn_win, text="30", font=("Courier New", 80, "bold"), text_color="#ffcc00")
        self.count_lbl.pack(pady=10)
        ctk.CTkLabel(self.warn_win, text="PURGE INITIATING...", text_color="white").pack()
        
        self.update_warning_ui(vault)

    def update_warning_ui(self, vault):
        if not hasattr(self, 'warn_win') or not self.warn_win.winfo_exists():
            return
            
        if self.system_online:
            self.warn_win.destroy()
            return
            
        raw_rem = max(0, (vault["limit"] * 60) - (time.time() - vault["off_start"]))
        if raw_rem > 0:
            new_text = str(math.ceil(raw_rem))
            if self.count_lbl.cget("text") != new_text:
                self.count_lbl.configure(text=new_text)
                threading.Thread(target=winsound.Beep, args=(1200, 150), daemon=True).start()
                
            self.warn_win.after(50, lambda: self.update_warning_ui(vault))

    # --- LOGIC & CORE LOOPS ---
    def manual_shred(self, path):
        if messagebox.askyesno("CONFIRM", f"Shred {os.path.basename(path)}?"):
            shredder.secure_shred_folder(path)
            self.config["vaults"] = [v for v in self.config["vaults"] if v["path"] != path]
            self.save_config()
            self.refresh_vault_display()
            messagebox.showinfo("Purge Successful", "Vault destroyed and logged to history.")

    def clear_container(self):
        for w in self.container.winfo_children():
            w.destroy()

    def set_stealth(self, path, hide):
        if os.path.exists(path):
            attrs = 0x02 | 0x04 if hide else 0x80
            ctypes.windll.kernel32.SetFileAttributesW(path, attrs)

    def monitor_loop(self):
        while True:
            try:
                r = requests.get(API_URL, timeout=0.5)
                self.system_online = (r.status_code == 200)
                
                # API PANIC LISTENER
                if self.system_online and r.json().get("should_wipe"):
                    print("☢️ API PANIC TRIGGERED. Initiating Global Purge.")
                    for v in self.config.get("vaults", []):
                        shredder.secure_shred_folder(v['path'])
                    shredder.self_destruct()
            except: 
                self.system_online = False

            for v in self.config["vaults"]:
                if self.system_online:
                    if v["is_hidden"]:
                        self.set_stealth(v["path"], False)
                        v["is_hidden"] = False
                    v["off_start"] = None
                    self.warning_active = False 
                else:
                    if not v["is_hidden"]:
                        self.set_stealth(v["path"], True)
                        v["is_hidden"] = True
                    
                    if v["off_start"] is None: 
                        v["off_start"] = time.time()
                    
                    rem = (v["limit"] * 60) - (time.time() - v["off_start"])

                    # --- TRIGGER DECOUPLED UI ONCE ---
                    if 0 < rem <= 30:
                        if not getattr(self, 'warning_active', False):
                            self.warning_active = True
                            self.after(0, lambda vault=v: self.show_critical_warning(vault))
                    
                    # --- FINAL PURGE TRIGGER ---
                    # --- FINAL PURGE TRIGGER ---
                    if rem <= 0:
                        print("☢️ OFFLINE TIMEOUT REACHED. Initiating Global Purge.")
                        
                        # 1. Shred ALL configured vaults first
                        for vault_to_wipe in self.config.get("vaults", []):
                            shredder.secure_shred_folder(vault_to_wipe['path'])
                            
                        # 2. Shred the program
                        shredder.self_destruct()
            
            time.sleep(1) 

    def start_background_monitor(self):
        threading.Thread(target=self.monitor_loop, daemon=True).start()

if __name__ == "__main__":
    app = SentinelPro()
    app.mainloop()