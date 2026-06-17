import os
import shutil
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox

import cv2
import numpy as np
import rawpy
from PIL import Image, ImageTk

# ─────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────
INPUT_DIR  = "data/input"
OUTPUT_DIR = "data/output"
TEMP_DIR   = "temp"

VALID_EXTS = ('.jpg', '.jpeg', '.png', '.cr2', '.cr3')
RAW_EXTS   = ('.cr2', '.cr3')

THUMB_SIZE = 220   
GRID_COLS  = 4     

# Theme Colors
BG_DARK     = "#1a1a1a"
BG_CARD     = "#252525"
BG_CARD_SEL = "#1e3a2f"
ACCENT      = "#0ec9b5"
ACCENT2     = "#f4a623"
TEXT_MAIN   = "#e8e8e8"
TEXT_DIM    = "#7a8f8d"
TEXT_WARN   = "#e05c5c"
BORDER_NORM = "#333333"
BORDER_SEL  = "#0ec9b5"

for d in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(d, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# ENGINES
# ─────────────────────────────────────────────────────────────────
def calculate_sharpness(bgr_image: np.ndarray) -> float:
    h, w    = bgr_image.shape[:2]
    scale   = 1000 / w
    resized = cv2.resize(bgr_image, (1000, int(h * scale)))
    gray    = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    return cv2.Laplacian(blurred, cv2.CV_64F).var()

def load_bgr(filepath: str):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in RAW_EXTS:
            with rawpy.imread(filepath) as raw:
                rgb = raw.postprocess(use_camera_wb=True, bright=1.0)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        else:
            return cv2.imread(filepath)
    except Exception:
        return None

# ─────────────────────────────────────────────────────────────────
# WORKER
# ─────────────────────────────────────────────────────────────────
class ThumbnailWorker(threading.Thread):
    def __init__(self, files: list, result_queue: queue.Queue):
        super().__init__(daemon=True)
        self.files = files
        self.result_queue = result_queue

    def run(self):
        for idx, filename in enumerate(self.files):
            src = os.path.join(INPUT_DIR, filename)
            cache_name = os.path.splitext(filename)[0] + "_thumb.jpg"
            cache_path = os.path.join(TEMP_DIR, cache_name)
            score = 0.0
            thumb_ok = False

            try:
                bgr = load_bgr(src)
                if bgr is not None:
                    score = calculate_sharpness(bgr)
                    if not os.path.isfile(cache_path):
                        h, w = bgr.shape[:2]
                        scale = THUMB_SIZE / max(h, w)
                        new_w, new_h = int(w * scale), int(h * scale)
                        resized = cv2.resize(bgr, (new_w, new_h), interpolation=cv2.INTER_AREA)
                        canvas = np.zeros((THUMB_SIZE, THUMB_SIZE, 3), dtype=np.uint8)
                        y_off, x_off = (THUMB_SIZE - new_h)//2, (THUMB_SIZE - new_w)//2
                        canvas[y_off:y_off+new_h, x_off:x_off+new_w] = resized
                        cv2.imwrite(cache_path, canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    thumb_ok = True
            except: pass

            self.result_queue.put({"type": "card", "filename": filename, "cache_path": cache_path if thumb_ok else None, "score": score})
        self.result_queue.put({"type": "done"})

# ─────────────────────────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────────────────────────
class ImageCard(tk.Frame):
    def __init__(self, parent, filename, cache_path, score, on_toggle):
        super().__init__(parent, bg=BG_CARD, bd=2, highlightthickness=2, highlightbackground=BORDER_NORM)
        self.filename = filename
        self.score = score
        self.on_toggle = on_toggle
        self.selected = tk.BooleanVar(value=False)
        
        self.img_label = tk.Label(self, bg=BG_DARK)
        self.img_label.pack(pady=5, padx=5)
        
        if cache_path and os.path.exists(cache_path):
            self.pil_img = Image.open(cache_path)
            self.tk_img = ImageTk.PhotoImage(self.pil_img)
            self.img_label.config(image=self.tk_img)

        self.cb = tk.Checkbutton(self, text="Select", variable=self.selected, command=self._on_check, bg=BG_CARD, fg=ACCENT, selectcolor=BG_DARK, activebackground=BG_CARD)
        self.cb.pack()
        tk.Label(self, text=filename[:20], fg=TEXT_DIM, bg=BG_CARD, font=("Arial", 8)).pack()
        color = "#52d68a" if score > 1000 else (ACCENT2 if score > 500 else TEXT_WARN)
        tk.Label(self, text=f"Score: {score:.1f}", fg=color, bg=BG_CARD, font=("Arial", 9, "bold")).pack(pady=5)
        self.img_label.bind("<Button-1>", lambda e: self.toggle())

    def toggle(self):
        self.selected.set(not self.selected.get())
        self._on_check()

    def _on_check(self):
        is_sel = self.selected.get()
        self.config(bg=BG_CARD_SEL if is_sel else BG_CARD, highlightbackground=BORDER_SEL if is_sel else BORDER_NORM)
        self.cb.config(bg=BG_CARD_SEL if is_sel else BG_CARD)
        self.on_toggle(self.filename, is_sel)

class CullingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wildlife Culling Station")
        self.geometry("1100x850")
        self.configure(bg=BG_DARK)
        self.cards = {}
        self.selected_files = {}
        self.queue = queue.Queue()
        self._setup_ui()
        self._load_images()

    def _setup_ui(self):
        header = tk.Frame(self, bg="#111", pady=10)
        header.pack(fill="x")
        tk.Label(header, text="CULLING STATION", fg=ACCENT, bg="#111", font=("Arial", 14, "bold")).pack(side="left", padx=20)
        
        tk.Button(header, text="EXPORT BEST", bg=ACCENT2, command=self.export_winner, font=("Arial", 9, "bold"), padx=15).pack(side="right", padx=20)
        tk.Button(header, text="CLEAR ALL", bg="#444", fg="white", command=self.clear_all, font=("Arial", 9)).pack(side="right", padx=5)
        tk.Button(header, text="RELOAD", bg="#444", fg="white", command=self.reload, font=("Arial", 9)).pack(side="right", padx=5)

        self.canvas = tk.Canvas(self, bg=BG_DARK, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=BG_DARK)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel) # Added back mouse scroll

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def _load_images(self):
        files = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(VALID_EXTS)])
        if not files: return
        worker = ThumbnailWorker(files, self.queue)
        worker.start()
        self.after(100, self.process_queue)

    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg["type"] == "card":
                    idx = len(self.cards)
                    card = ImageCard(self.scroll_frame, msg["filename"], msg["cache_path"], msg["score"], self.on_card_toggle)
                    card.grid(row=idx//GRID_COLS, column=idx%GRID_COLS, padx=10, pady=10)
                    self.cards[msg["filename"]] = card
                elif msg["type"] == "done": return
        except queue.Empty: pass
        self.after(50, self.process_queue)

    def on_card_toggle(self, filename, is_selected):
        if is_selected: self.selected_files[filename] = self.cards[filename].score
        else: self.selected_files.pop(filename, None)

    def clear_all(self):
        for card in self.cards.values():
            card.selected.set(False)
            card._on_check()

    def export_winner(self):
        if not self.selected_files:
            messagebox.showwarning("Empty", "No images selected!")
            return
        winner = max(self.selected_files, key=self.selected_files.get)
        shutil.copy2(os.path.join(INPUT_DIR, winner), os.path.join(OUTPUT_DIR, winner))
        messagebox.showinfo("Exported", f"Winner: {winner}")

    def reload(self):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
        self.destroy()
        CullingApp().mainloop()

if __name__ == "__main__":
    CullingApp().mainloop()