import tkinter as tk
import subprocess
import cv2
import mss
import numpy as np
import pyautogui
from PIL import Image, ImageTk

class VirtualMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Monitor Control")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.enable_button = tk.Button(root, text="Enable Virtual Monitor", command=self.enable_monitor)
        self.enable_button.pack(pady=10)

        self.disable_button = tk.Button(root, text="Disable Virtual Monitor", command=self.disable_monitor)
        self.disable_button.pack(pady=10)

        self.stream_button = tk.Button(root, text="Start Streaming (Monitor 3)", command=self.start_stream)
        self.stream_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop Streaming", command=self.stop_stream)
        self.stop_button.pack(pady=10)

        self.stream_frame = tk.Frame(root, width=800, height=600)
        self.stream_frame.pack(pady=10)

        self.canvas = tk.Canvas(self.stream_frame, width=800, height=600)
        self.canvas.pack()

        self.streaming = False
        self.img_tk = None

    def on_closing(self):
        self.stop_stream()
        self.root.destroy()

    def enable_monitor(self):
        subprocess.run(["pnputil", "/enable-device", "ROOT\\DISPLAY\\0000"])
        self.root.after(3000, self.start_stream)

    def disable_monitor(self):
        subprocess.run(["pnputil", "/disable-device", "ROOT\\DISPLAY\\0000"])
        self.stop_stream()

    def start_stream(self):
        if not self.streaming:
            self.streaming = True
            self.stream_monitor()

    def stop_stream(self):
        self.streaming = False
        self.canvas.delete("all")

    def stream_monitor(self):
        if not self.streaming:
            return

        with mss.mss() as sct:
            if len(sct.monitors) < 4:
                print("Менше чотирьох моніторів доступно.")
                self.stop_stream()
                return

            monitor = sct.monitors[3]
            screenshot = sct.grab(monitor)

            # Перевірка на наявність зображення
            if screenshot is None:
                print("Не вдалося отримати знімок екрану.")
                self.stop_stream()
                return

            frame = np.array(screenshot)

            # Перевірка на те, що знімок не порожній
            if frame.size == 0 or frame is None:
                print("Отримано порожній знімок екрану.")
                self.stop_stream()
                return

            # Виправлення конверсії кольорів
            try:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            except cv2.error as e:
                print(f"Помилка cvtColor: {e}")
                self.stop_stream()
                return

            cursor_x, cursor_y = pyautogui.position()
            cursor_x -= monitor["left"]
            cursor_y -= monitor["top"]

            # Додайте курсор
            cv2.circle(frame, (cursor_x, cursor_y), 10, (0, 255, 0), -1)

            # Зменште розмір зображення перед відображенням
            frame = cv2.resize(frame, (800, 600))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame)
            self.img_tk = ImageTk.PhotoImage(image=img)

            self.canvas.create_image(0, 0, image=self.img_tk, anchor='nw')
            self.root.after(16, self.stream_monitor)  # Підтримка близько 60 FPS


if __name__ == "__main__":
    root = tk.Tk()
    app = VirtualMonitorApp(root)
    root.mainloop()
