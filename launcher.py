import multiprocessing
import sys
import os

# --- КРИТИЧЕСКИЙ ФИКС ДЛЯ ПАЙТОН 3.14 (ЗАПУСКАТЬ ПЕРВЫМ) ---
if __name__ == '__main__':
    multiprocessing.freeze_support()

# Исправление вылета CustomTkinter в EXE без консоли
if sys.stderr is None: sys.stderr = open(os.devnull, 'w')
if sys.stdout is None: sys.stdout = open(os.devnull, 'w')

import subprocess
import threading
import time
import requests
import random
import shutil
from concurrent.futures import ThreadPoolExecutor

# --- АВТОУСТАНОВКА ---
def install_libs():
    libs = ['customtkinter', 'requests[socks]', 'pillow']
    for lib in libs:
        try:
            if "[" in lib: __import__(lib.split('[')[0])
            else: __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

install_libs()
import customtkinter as ctk

# --- ОКНО-УВЕДОМЛЕНИЕ ПОВЕРХ ВСЕХ ПРИЛОЖЕНИЙ ---
class OverlayWarning(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry("520x240")
        self.attributes("-topmost", True)
        self.overrideredirect(True)
        self.configure(fg_color="#121212")
        
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{int(sw/2-260)}+{int(sh/2-120)}")

        self.frame = ctk.CTkFrame(self, fg_color="#16161a", border_width=2, border_color="#ffcc00", corner_radius=20)
        self.frame.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(self.frame, 
            text="сервер загружается примерно 1 мин или 5 мин\nподождите пожалуйста\n\n- разработчик TATAR_506 -", 
            font=("Segoe UI", 14, "bold"), text_color="#ffcc00").pack(pady=(40, 20))

        ctk.CTkButton(self.frame, text="Я ВСЁ ПОНЯЛ", fg_color="#ffcc00", text_color="black",
                      font=("Segoe UI", 12, "bold"), hover_color="#e6b800",
                      command=self.destroy).pack(pady=15)

class TTModLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- ДИЗАЙН NIGHTCORE ---
        self.title("TT DESKTOP MOD")
        self.geometry("450x850")
        self.overrideredirect(True) 
        self.configure(fg_color="#0b0b0d")

        self.old_x, self.old_y = 0, 0
        self.found_proxy = None
        self.stop_search = False
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], 'TT_OBS_Ready_V33')

        self.setup_ui()
        self.after(500, lambda: OverlayWarning(self))

    def setup_ui(self):
        self.top_bar = ctk.CTkFrame(self, fg_color="transparent", height=60)
        self.top_bar.pack(fill="x", padx=20, pady=10)
        self.top_bar.bind("<Button-1>", self.get_pos)
        self.top_bar.bind("<B1-Motion>", self.move_window)

        ctk.CTkLabel(self.top_bar, text="⚡ TT DESKTOP", font=("Segoe UI", 20, "bold"), text_color="white").pack(side="left")
        ctk.CTkButton(self.top_bar, text="✕", width=30, height=30, fg_color="transparent", 
                      hover_color="#ff4444", text_color="white", command=self.quit).pack(side="right", padx=5)
        
        self.status_card = ctk.CTkFrame(self, fg_color="#16161a", corner_radius=20, border_width=1, border_color="#222226")
        self.status_card.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(self.status_card, text="СТАТУС СИСТЕМЫ", font=("Segoe UI", 12, "bold"), text_color="#888888").pack(anchor="w", padx=20, pady=(15, 0))
        
        self.active_frame = ctk.CTkFrame(self.status_card, fg_color="transparent")
        self.active_frame.pack(fill="x", padx=20, pady=5)
        self.dot = ctk.CTkLabel(self.active_frame, text="●", text_color="#eab308", font=("Arial", 18))
        self.dot.pack(side="left")
        self.status_text = ctk.CTkLabel(self.active_frame, text="Ожидание...", font=("Segoe UI", 18, "bold"), text_color="white")
        self.status_text.pack(side="left", padx=10)

        self.info_row = ctk.CTkFrame(self.status_card, fg_color="transparent")
        self.info_row.pack(fill="x", padx=15, pady=15)
        for txt, clr in [("Версия\nv34.5.2", "#888888"), ("Регион\nGlobal", "#0ea5e9")]:
            b = ctk.CTkFrame(self.info_row, fg_color="#1c1c22", corner_radius=12)
            b.pack(side="left", expand=True, fill="x", padx=5)
            ctk.CTkLabel(b, text=txt, font=("Segoe UI", 11), text_color=clr).pack(pady=8)

        self.console = ctk.CTkTextbox(self, fg_color="#000000", font=("Consolas", 10), text_color="#00ff41", height=100)
        self.console.pack(fill="x", padx=25, pady=5)

        self.launch_btn = ctk.CTkButton(self, text="▶\n\nЗАПУСТИТЬ ТИКТОК", 
                                        font=("Segoe UI", 22, "bold"),
                                        fg_color="#16161a", border_color="#33333a", border_width=2,
                                        hover_color="#1c1c24", corner_radius=25,
                                        height=220, command=self.start_engine)
        self.launch_btn.pack(fill="x", padx=25, pady=10)

        self.bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_row.pack(fill="x", padx=20, pady=10)
        for icon, title, desc, clr in [("🛡", "Безопасность", "Трафик защищен", "#22c55e"), ("📥", "Загрузка", "Без знаков", "#0ea5e9")]:
            f = ctk.CTkFrame(self.bottom_row, fg_color="#16161a", corner_radius=20, height=100)
            f.pack(side="left", expand=True, fill="both", padx=5)
            ctk.CTkLabel(f, text=icon, font=("Arial", 20), text_color=clr).pack(pady=(10,0))
            ctk.CTkLabel(f, text=title, font=("Segoe UI", 13, "bold"), text_color="white").pack()
            ctk.CTkLabel(f, text=desc, font=("Segoe UI", 10), text_color="#666666").pack()

        ctk.CTkLabel(self, text="TT MOD BY TATAR_506 • v2.0.1", font=("Segoe UI", 10), text_color="#333333").pack(side="bottom", pady=15)

    def log(self, msg):
        self.console.insert("end", f"> {msg}\n")
        self.console.see("end")

    def get_pos(self, event):
        self.old_x, self.old_y = event.x, event.y
    def move_window(self, event):
        self.geometry(f"+{self.winfo_x() + (event.x - self.old_x)}+{self.winfo_y() + (event.y - self.old_y)}")

    # --- ЛОГИКА ОБХОДА (ОПТИМИЗИРОВАНО ДЛЯ ОБС) ---
    def start_engine(self):
        self.launch_btn.configure(state="disabled", text="ОПТИМИЗАЦИЯ...")
        self.status_text.configure(text="Подготовка...", text_color="#eab308")
        self.console.delete("1.0", "end")
        self.stop_search = False
        self.found_proxy = None
        threading.Thread(target=self.main_logic, daemon=True).start()

    def check_proxy(self, p_data):
        if self.stop_search: return
        p_type, p_addr = p_data
        try:
            p_dict = {"http": f"{p_type}://{p_addr}", "https": f"{p_type}://{p_addr}"}
            # ТАЙМАУТ 8 СЕКУНД (Чтобы пробить сеть при включенном ОБС)
            r = requests.get("https://www.google.com/generate_204", proxies=p_dict, timeout=8)
            if r.status_code == 204:
                self.found_proxy = p_data
                self.stop_search = True
        except: pass

    def main_logic(self):
        self.log("Подключение к базе (Режим записи: ВКЛ)...")
        sources = {
            "socks5": ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt", "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt"],
            "socks4": ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt"],
            "http": ["https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"]
        }
        all_p = []
        for t, urls in sources.items():
            for u in urls:
                try: all_p.extend([(t, p) for p in requests.get(u, timeout=5).text.splitlines() if p])
                except: continue
        random.shuffle(all_p)
        
        self.log("Проверка туннеля (100 потоков)...")
        # УМЕНЬШЕНО ДО 100 ПОТОКОВ ДЛЯ СТАБИЛЬНОСТИ ОБС
        with ThreadPoolExecutor(max_workers=100) as executor:
            for p_data in all_p[:2000]:
                if self.found_proxy: break
                executor.submit(self.check_proxy, p_data)

        if self.found_proxy:
            self.log(f"Узел: {self.found_proxy[1]}.")
            self.status_text.configure(text="Запущено!", text_color="#22c55e")
            self.dot.configure(text_color="#22c55e")
            self.run_browser(self.found_proxy)
        else:
            self.log("Ошибка: Перегрузка сети при записи.")
            self.status_text.configure(text="Ошибка", text_color="#ef4444")
            self.launch_btn.configure(state="normal", text="▶\n\nЗАПУСТИТЬ ТИКТОК")

    def run_browser(self, p_data):
        p_type, p_addr = p_data
        url = "https://www.tiktok.com/foryou"
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        
        args = [
            f"--app={url}", f"--user-data-dir={self.profile_path}", f"--proxy-server={p_type}://{p_addr}",
            f"--user-agent={ua}", "--lang=ru-RU", "--ignore-certificate-errors",
            "--disable-blink-features=AutomationControlled", "--window-size=1550,950",
            "--disable-gpu", "--disable-software-rasterizer", # ФИКС ОБС
            "--proxy-connection-timeout=30" # Ждать туннель дольше
        ]

        for path in [os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"), 
                     os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe")]:
            if os.path.exists(path):
                subprocess.Popen([path] + args)
                time.sleep(5)
                self.withdraw()
                return

if __name__ == "__main__":
    app = TTModLauncher()
    app.mainloop()