from tkinter import Tk
import threading
import ctypes
from camera import Camera
from settings import load_settings, save_settings
from gui import create_gui
from frame_processor import FrameProcessor
import os
import sys


class AppState:

    def __init__(self):
        self.calculate_initial_distance = False
        self.latest_force_value = None
        self.is_timer_running = False
        self.elapsed_time = 0.0
        self.recorded_data = []
        self.engine_speed = 0.0
        self.engine_dir = 1
        self.auto_analysis_enabled = False
        self.auto_target_force = 0.0
        self.auto_initial_speed = 0.0
        self.auto_analysis_done = False
        self.blobs_ok = False
        self.px_to_mm_ratio = None
        self.constant_strain_mode = False
        self.target_strain_rate = 0.001
        self.px_to_mm_ratio = None

    def reset(self):
        self.elapsed_time = 0.0
        self.recorded_data.clear()
        self.latest_force_value = None
        self.auto_analysis_done = False


class AppController:
    def __init__(self):
        self.state = AppState()
        self.settings = load_settings()
        self.settings["roi1_x"] = -50
        self.settings["roi1_y"] = 0
        self.settings["roi2_x"] = 50
        self.settings["roi2_y"] = 0
        self.camera = Camera(self.settings)
        self.app = Tk()
        roi_height = int(self.settings.get("roi_height", 300))
        roi_width = int(self.settings.get("roi_width", 100))
        self.default_app_width = 1500
        self.app_width = max(self.default_app_width, roi_width)
        self.app_height = roi_height + 640
        self.app.geometry(f"{self.app_width}x{self.app_height}")

        self.app.resizable(False, False)

        self._init_dpi_awareness()

        self.gui = create_gui(self.app, self.settings, None, self.state)
        self.gui.app_controller = self
        self.processor = FrameProcessor(self.camera, self.gui, self.state)

        self.gui.logic.processor = self.processor

        class ConsoleRedirect:
            def __init__(self, log_widget, original_stream):
                self.log_widget = log_widget
                self.original_stream = original_stream  # np. sys.__stdout__ lub sys.__stderr__

            def write(self, message):
                if message.strip():
                    # do pola GUI
                    self.log_widget.config(state='normal')
                    self.log_widget.insert('end', message.strip() + '\n')
                    self.log_widget.see('end')
                    self.log_widget.config(state='disabled')
                # do konsoli
                self.original_stream.write(message)
                self.original_stream.flush()

            def flush(self):
                self.original_stream.flush()

        sys.stdout = ConsoleRedirect(self.gui.log_box, sys.__stdout__)
        sys.stderr = ConsoleRedirect(self.gui.log_box, sys.__stderr__)

        self._setup_events()

    def _init_dpi_awareness(self):
        if os.name == "nt":
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Windows 8.1+
            except:
                try:
                    ctypes.windll.user32.SetProcessDPIAware()  # Starsze wersje
                except:
                    pass

    def _setup_events(self):
        self.app.protocol("WM_DELETE_WINDOW", self._on_close)

    def run(self):
        self._start_threads()
        self.processor.start()
        self.app.mainloop()

    def _start_threads(self):
        capture_thread = threading.Thread(target=self.camera.capture_frames, daemon=True)
        capture_thread.start()

    def _on_close(self):
        save_settings(
            self.settings["camera_mode"],
            self.settings["camera_width"],
            self.settings["camera_height"],
            self.settings["brightness"],
            self.settings["contrast"],
            self.settings["grayscale"],
            self.settings["negative"],
            self.settings["minArea"],
            self.settings["maxArea"],
            self.settings["roi_width"],
            self.settings["roi_height"],
            self.settings["small_roi_size"]
        )

        self.camera.release()
        self.app.destroy()
