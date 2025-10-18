import tkinter as tk
from tkinter import messagebox, font, scrolledtext
from dotenv import load_dotenv, set_key
import os
import subprocess
import threading

ENV_PATH = ".env"
FONT_PATH = "asset/fonts/SejongGeulggot.ttf"
FONT_NAME = "SejongGeulggot"
TITLE = "DC2S GUI"
WINDOW_RESIZABLE = True
BG_COLOR = "#16171B"
FG_COLOR = "white"

if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)

root = tk.Tk()
root.title(TITLE)
root.geometry("600x750")
root.configure(bg=BG_COLOR)
root.resizable(WINDOW_RESIZABLE,WINDOW_RESIZABLE)

try:
    import pyglet
    pyglet.font.add_file(FONT_PATH)
except Exception as e:
    print(f"❌ Font loading failed: {e}")
default_font = font.Font(family=FONT_NAME, size=12)

mode_var = tk.StringVar(value="load")

def toggle_fields():
    mode = mode_var.get()
    if mode == "load": 
        scenario_src_entry.config(state="normal")
        for widget in new_fields:
            widget.config(state="disabled")
    else:
        scenario_src_entry.config(state="disabled")
        for widget in new_fields:
            widget.config(state="normal")

tk.Label(root, text="Select Mode:", bg=BG_COLOR, fg=FG_COLOR, font=default_font).pack(pady=10, anchor="w", padx=20)

load_radio = tk.Radiobutton(
    root, text="Load Existing Scenario", variable=mode_var, value="load",
    command=toggle_fields, bg="#444", fg=FG_COLOR, indicatoron=0, width=25, pady=5, font=default_font
)
load_radio.pack(anchor="w", pady=5, padx=20)

new_radio = tk.Radiobutton(
    root, text="New Scenario", variable=mode_var, value="new",
    command=toggle_fields, bg="#444", fg=FG_COLOR, indicatoron=0, width=25, pady=5, font=default_font
)
new_radio.pack(anchor="w", pady=5, padx=20)

tk.Label(root, text="Scenario File Path:", bg=BG_COLOR, fg=FG_COLOR, font=default_font).pack(pady=5, anchor="w", padx=20)
scenario_src_entry = tk.Entry(root, width=50, font=default_font)
scenario_src_entry.pack(pady=5, padx=20)
scenario_src_entry.insert(0, os.getenv("scenario_src") or "")

new_fields = []

def create_label_entry(parent, text, env_var):
    tk.Label(parent, text=text, bg=BG_COLOR, fg=FG_COLOR, font=default_font).pack(pady=2, anchor="w", padx=20)
    entry = tk.Entry(parent, width=50, font=default_font)
    entry.pack(pady=2, padx=20)
    entry.insert(0, os.getenv(env_var) or "")
    new_fields.append(entry)
    return entry

openrouter_token_entry = create_label_entry(root, "OpenRouter Token:", "OPENROUTERTOKEN")
openrouter_model_entry =create_label_entry(root, "OpenRouter Model:", "OPENROUTER_MODEL") 
channel_entry = create_label_entry(root, "CHANNEL_ID:", "CHANNEL_ID")
filename_entry = create_label_entry(root, "Filename:", "filename")
after_entry = create_label_entry(root, "After (YYYY_M_D_H_m_s):", "after")
before_entry = create_label_entry(root, "Before (YYYY_M_D_H_m_s):", "before")
token_entry = create_label_entry(root, "TOKEN:", "TOKEN")

toggle_fields()

def write_log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)
    root.update_idletasks()

def stream_process_output(process):
    for line in process.stdout:
        if line:
            write_log(line.rstrip())
    process.wait()
    execute_button.config(state="normal")

def execute_scenario():
    log_box.delete("1.0", tk.END)
    execute_button.config(state="disabled")
    mode = mode_var.get()

    if mode == "load":
        scenario_src = scenario_src_entry.get().strip()
        if not scenario_src or not os.path.exists(scenario_src):
            messagebox.showerror("Error", "Scenario file path is invalid.")
            execute_button.config(state="normal")
            return
        os.environ["load_from_scenario_file"] = '1'
        os.environ["scenario_src"] = scenario_src
    else:
        os.environ["load_from_scenario_file"] = '0'
        os.environ["scenario_src"] = " "
        os.environ["filename"] = filename_entry.get().strip()
        os.environ["after"] = after_entry.get().strip()
        os.environ["before"] = before_entry.get().strip()
        os.environ["TOKEN"] = token_entry.get().strip()
        os.environ["CHANNEL_ID"] = channel_entry.get().strip()
        os.environ["OPENROUTERTOKEN"] = openrouter_token_entry.get().strip()
        os.environ["OPENROUTER_MODEL"] = openrouter_model_entry.get().strip()

    for key in ["load_from_scenario_file","scenario_src","filename","after","before","TOKEN","CHANNEL_ID","OPENROUTERTOKEN","OPENROUTER_MODEL"]:
        val = os.environ.get(key, "")
        set_key(ENV_PATH, key, val)

    def run():
        try:
            env = os.environ.copy()
            env["PYTHONUNBUFFERED"] = "1"  # 💡 출력이 실시간으로 나오게 함
            process = subprocess.Popen(
                ["python", "src/main.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            stream_process_output(process)
        except Exception as e:
            write_log(f"❌ Error: {e}")
            execute_button.config(state="normal")

    threading.Thread(target=run, daemon=True).start()

# 버튼
execute_button = tk.Button(
    root, text="Execute Generating Video", command=execute_scenario,
    bg="#888", fg=FG_COLOR, font=default_font
)
execute_button.pack(pady=5)

# 로그 창을 버튼 아래로 이동 💡
log_box = scrolledtext.ScrolledText(root, height=12, bg="#222", fg="white", font=default_font)
log_box.pack(fill="both", padx=20, pady=(5, 20))

root.mainloop()
