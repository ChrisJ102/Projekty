import time
from datetime import datetime
import os
import threading
import queue
from tkinter import messagebox
import ctypes
import subprocess
from image_processing import calculate_deformation



class AppLogic:
    def __init__(self, gui):
        self.gui = gui
        self.app = gui.app
        self.state = gui.state
        self.usb_comm = gui.usb_comm
        self.engine_comm = gui.engine_comm
        self.start_time = None

        self.app.after(10, self.update_force_display)
        self.app.after(10, self.update_time_display)
        self.logger = DataLogger(self.state)

    def connect_to(self, target="force"):
        if target == "force":
            device = self.gui.device_var.get()
            comm = self.usb_comm
            button = self.gui.connect_button
        elif target == "engine":
            device = self.gui.engine_device_var.get()
            comm = self.engine_comm
            button = self.gui.engine_connect_button
        else:
            print("[USB] Unknown connection target.")
            return

        if device == "No devices found":
            print(f"[USB] No device found ({target}).")
            return

        if comm.connect(device):
            print(f"[USB] Connected to {target} on port {device}")
            button.config(text="Connected", state="disabled")
        else:
            print(f"[USB] Failed to connect to {target} ({device})")

    def update_force_display(self):
        if self.gui.connect_button["state"] == "disabled":
            data = self.usb_comm.get_latest_data()
            if data:
                self.gui.force_label.config(text=f"Force: {data}")

        self.app.after(100, self.update_force_display)

    def start_timer(self):
        if self.state.auto_analysis_enabled:
            threading.Thread(target=self.auto_analysis_sequence, daemon=True).start()
            return

        try:
            # # ✅ Sprawdzenia przed startem
            # missing = []
            #
            # if self.processor._initial_distance is None:
            #     missing.append("Initial distance not calculated.")
            #
            # if not self.state.latest_force_value:
            #     missing.append("Force sensor not connected or no data.")
            #
            # if not self.engine_comm.serial_connection or not self.engine_comm.serial_connection.is_open:
            #     missing.append("Engine not connected.")
            #
            # if self.state.engine_speed <= 0:
            #     missing.append("Engine speed not set (must be > 0).")
            #
            # if self.gui.engine_dir_var.get() != 1:
            #     missing.append("Direction must be set to STRETCH before starting the test.")
            #
            # if missing:
            #     messagebox.showerror("Cannot start test", "\n".join(missing))
            #     return

            # Jeśli aktywny tryb constant strain rate – skala musi być ustawiona
            if self.state.constant_strain_mode and not self.state.px_to_mm_ratio:
                messagebox.showwarning("Missing scale","Please calibrate scale before using constant strain rate mode.")
                return

            self.state.is_timer_running = True
            self.start_time = time.time()
            #self.logger.start()
            self.update_buttons_state()
            print("[ANALYSIS] Logger started")

            direction = self.state.engine_dir

            # ➕ Nowe sterowanie prędkością na podstawie zadanej prędkości odkształcenia
            if self.state.constant_strain_mode and self.state.px_to_mm_ratio and self.processor._initial_distance:
                strain_rate = self.state.target_strain_rate
                l0 = self.processor._initial_distance
                mm_per_px = self.state.px_to_mm_ratio
                start_speed = l0 * strain_rate * mm_per_px
                start_speed = max(0.001, min(start_speed, 10.0))

                # Zapisz w stanie, by była znana w pętli przetwarzania
                self.processor._last_sent_speed = start_speed

                self.engine_comm.send_engine_command(f"DIR:{direction}\n")
                self.engine_comm.send_engine_command(f"SPEED:{start_speed:.5f}\n")
                self.engine_comm.send_engine_command("START\n")

                print(f"[ANALYSIS] Engine start (strain mode) -> DIR:{direction}, SPEED:{start_speed:.5f}")

            else:
                # Klasyczne uruchomienie silnika
                speed = self.state.engine_speed
                self.engine_comm.send_engine_command(f"DIR:{direction}\n")
                self.engine_comm.send_engine_command(f"SPEED:{speed:.5f}\n")
                self.engine_comm.send_engine_command("START\n")
                print(f"[ANALYSIS] Engine start -> DIR:{direction}, SPEED:{speed:.5f}")

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[ANALYSIS] Start_timer error: {e}")

    def auto_analysis_sequence(self):
        try:
            if self.state.auto_analysis_done:
                print("[ANALYSIS] Auto-analysis already completed. Skipping.")
                return

            #  Sprawdzenie połączeń
            if not self.engine_comm.serial_connection or not self.engine_comm.serial_connection.is_open:
                print("[AUTO] Engine not connected. Aborting auto-analysis.")
                return

            if not self.usb_comm.serial_connection or not self.usb_comm.serial_connection.is_open:
                print("[AUTO] Force sensor not connected. Aborting auto-analysis.")
                return

            #  Parametry
            force_target = self.state.auto_target_force
            initial_speed = self.state.auto_initial_speed
            direction = self.state.engine_dir

            print(f"[ANALYSIS] Starting auto-analysis -> Force: {force_target} N | Speed: {initial_speed} mm/s")

            # Wysyłanie ustawień kierunku i prędkości
            self.engine_comm.send_engine_command(f"DIR:{direction}\n")
            self.engine_comm.send_engine_command(f"SPEED:{initial_speed:.5f}\n")
            self.engine_comm.send_engine_command("START\n")

            print("[ANALYSIS] Engine running until force is reached")

            # Czekanie na siłę
            while True:
                time.sleep(0.01)
                value = abs(self.state.latest_force_value)
                if not value:
                    continue
                try:
                    if float(value) >= force_target:
                        print(f"[ANALYSIS] Target force {force_target} N reached")
                        break
                except ValueError:
                    continue

            # Zatrzymanie silnika
            self.engine_comm.send_engine_command("STOP\n")
            time.sleep(1)

            print("[ANALYSIS] Engine stopped")

            self.state.calculate_initial_distance = True
            print("[ANALYSIS] Measuring initial distance")

            # Start właściwej analizy
            print("[ANALYSIS] Starting main test")
            self.state.auto_analysis_enabled = False
            self.start_timer()
            self.state.auto_analysis_done = True

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[ANALYSIS] Error during auto analysis: {e}")

    def stop_timer(self):
        try:
            self.state.is_timer_running = False
            print("[ANALYSIS] Logger stopped")
            self.update_buttons_state()

            print("[DEBUG] Recorded data length:", len(self.state.recorded_data))

            if self.state.recorded_data:
                deformation_force_points = []
                for line in self.state.recorded_data:
                    parts = line.strip().split()
                    if len(parts) >= 3 and not line.startswith("Time"):
                        try:
                            deformation_val = float(parts[1])
                            force_val = float(parts[2])
                            deformation_force_points.append((deformation_val, force_val))
                        except ValueError:
                            continue

                print("[DEBUG] Parsed deformation-force points:", deformation_force_points[:5])

                if deformation_force_points:
                    print(f"[DEBUG] Sending {len(deformation_force_points)} points to add_series()")
                    self.processor.multi_test_force_plot_manager.add_series(deformation_force_points)


                else:
                    print("[DEBUG] No valid deformation-force points to plot.")

            self.engine_comm.send_engine_command("STOP\n")
            print("[ANALYSIS] Engine stop")

            self.save_data_to_file(auto=True)

        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[ANALYSIS] Stop_timer error: {e}")

    def update_time_display(self):
        if self.state.is_timer_running:
            current_time = time.time()
            self.state.elapsed_time = round(current_time - self.start_time, 3)
            self.gui.time_label.config(text=f"Time: {self.state.elapsed_time:.3f}")

        self.app.after(10, self.update_time_display)

    def save_data_to_file(self, auto=False):
        if auto:
            user_filename = ""  # brak dodatku od użytkownika
        else:
            user_filename = self.gui.filename_entry.get().strip()
            if not user_filename:
                user_filename = "default"

        current_time = datetime.now().strftime("%H-%M-%S")

        # Nowa zmienna chart_name do zapisu wykresów
        if auto:
            folder_name = f"Badanie_{current_time}"
            txt_filename = "wyniki.txt"
            chart_name = f"Badanie"
        else:
            folder_name = f"Badanie_{current_time}_{user_filename}"
            txt_filename = f"wyniki_{user_filename}.txt"
            chart_name = f"Badanie_{user_filename}"

        try:
            os.makedirs(folder_name, exist_ok=True)  # Tworzy folder jeśli nie istnieje

            txt_full_path = os.path.join(folder_name, txt_filename)

            with open(txt_full_path, "w") as file:
                file.write("Time Deformation Force FPS\n")
                file.write("\n".join(self.state.recorded_data))

            print(f"[ANALYSIS] Data saved to file: {txt_full_path}")

        except Exception as e:
            print(f"[ANALYSIS] File save error: {e}")
            return

        # Zapis wykresów
        if self.processor:
            base_filename = os.path.join(folder_name, chart_name)
            self.processor.save_plots_as_png(base_filename)

    def refresh_ports(self, target="force"):
        if target == "force":
            conn_btn = self.gui.connect_button
            combobox = self.gui.device_combobox
            var = self.gui.device_var
            comm = self.usb_comm
        else:
            conn_btn = self.gui.engine_connect_button
            combobox = self.gui.engine_combobox
            var = self.gui.engine_device_var
            comm = self.engine_comm

        if conn_btn["state"] == "disabled":
            if comm.serial_connection and comm.serial_connection.is_open:
                print(f"[USB] Disconnected {target} from port {comm.serial_connection.port}")

            comm.disconnect()
            conn_btn.config(text="Connect", state="normal")

        devices = self.usb_comm.get_serial_devices()
        combobox["values"] = devices
        var.set(devices[0] if devices else "No devices found")

    def validate_and_apply_settings(self):
        try:
            entries = self.gui.entries
            brightness = float(entries["brightness"].get())
            contrast = float(entries["contrast"].get())
            min_area = float(entries["minArea"].get())
            max_area = float(entries["maxArea"].get())
            roi_width = int(entries["roi_width"].get())
            roi_height = int(entries["roi_height"].get())
            small_roi_size = int(entries["small_roi_size"].get())
            camera_width = self.gui.app_controller.camera.camera_width

            if os.name == "nt":
                screen_height = ctypes.windll.user32.GetSystemMetrics(1)
            else:
                try:
                    output = subprocess.check_output("xdpyinfo | grep dimensions", shell=True).decode()
                    screen_height = int(output.strip().split()[1].split('x')[1])
                except:
                    screen_height = 800  # fallback

            max_roi_height = screen_height - 640

            # Walidacje
            if not (-100 <= brightness <= 100):
                raise ValueError("Brightness must be between -100 and 100.")
            if not (0.1 <= contrast <= 2.0):
                raise ValueError("Contrast must be between 0.1 and 2.0.")
            if min_area <= 0:
                raise ValueError("Min Area must be greater than 0.")
            if max_area <= min_area:
                raise ValueError("Max Area must be greater than Min Area.")
            if not (1 <= roi_width <= camera_width):
                raise ValueError(f"ROI Width must be between 1 and {camera_width}.")
            if not (1 <= roi_height <= max_roi_height - 50):
                raise ValueError(f"ROI Height must be between 1 and {max_roi_height - 50}.")

            if not (1 <= small_roi_size <= roi_height):
                raise ValueError("Small ROI Size must be > 0 and <= ROI Height.")


            new_app_width = max(self.gui.app_controller.default_app_width, roi_width)
            new_app_height = roi_height + 640

            self.gui.app_controller.app_width = new_app_width
            self.gui.app_controller.app_height = new_app_height
            self.gui.app.geometry(f"{new_app_width}x{new_app_height}")

            self.gui.app_controller.settings.update({
                "brightness": brightness,
                "contrast": contrast,
                "grayscale": self.gui.grayscale_var.get(),
                "negative": self.gui.negative_var.get(),
                "minArea": min_area,
                "maxArea": max_area,
                "roi_width": roi_width,
                "roi_height": roi_height,
                "small_roi_size": small_roi_size
            })

            self.processor.update_active_settings()

        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Input", str(e))

    def dynamic_scale_calibration(self):
        def run_calibration():
            if not self.processor._initial_distance:
                messagebox.showwarning("Missing data", "Please calculate initial distance first.")
                self.gui.calibrate_scale_button.config(text="Calibrate Scale", state="normal")
                return

            if not self.engine_comm.serial_connection or not self.engine_comm.serial_connection.is_open:
                messagebox.showwarning("Engine not connected", "Please connect to the engine before calibration.")
                self.gui.calibrate_scale_button.config(text="Calibrate Scale", state="normal")
                return

            self.gui.calibrate_scale_button.config(text="Calibrating...", state="disabled")
            self.gui.app.update_idletasks()
            speed = self.state.engine_speed

            try:
                l0 = self.processor._initial_distance
                strain_data = []

                self.engine_comm.send_engine_command("DIR:1\n")
                self.engine_comm.send_engine_command(f"SPEED:{speed:.5f}\n")
                self.engine_comm.send_engine_command("START\n")
                print(f"[CALIBRATION] Engine started (DIR=1, SPEED={speed:.5f} mm/s)")

                start_time = time.time()
                while time.time() - start_time < 2.0:
                    if not self.processor.frame_queue.empty():
                        try:
                            l_now = self.processor.frame_queue.queue[-1]["distance"]
                            if l_now:
                                e_now = calculate_deformation(l_now, l0)
                                t = time.time() - start_time
                                if e_now is not None and e_now >= 0:
                                    strain_data.append((t, e_now, l_now))
                        except (IndexError, KeyError):
                            pass
                    time.sleep(0.03)

                self.engine_comm.send_engine_command("STOP\n")
                print("[CALIBRATION] Engine stopped")

                if len(strain_data) < 5:
                    messagebox.showerror("Calibration failed", "Too little data collected.")
                    return

                t1, e1, _ = strain_data[0]
                t2, e2, _ = strain_data[-1]
                avg_l = sum(l for _, _, l in strain_data) / len(strain_data)
                strain_rate = (e2 - e1) / (t2 - t1)

                if strain_rate <= 0 or avg_l <= 0:
                    messagebox.showerror("Calibration failed", "Invalid measurement results.")
                    return

                mm_per_px = 0.1 / (avg_l * strain_rate)
                self.state.px_to_mm_ratio = mm_per_px
                self.gui.scale_label.config(text=f"Scale: {mm_per_px:.4f} mm/px")

                print(f"[CALIBRATION] Dynamic scale = {mm_per_px:.4f} mm/px")

            except Exception as e:
                import traceback
                traceback.print_exc()
                messagebox.showerror("Calibration error", str(e))

            finally:
                self.gui.calibrate_scale_button.config(text="Calibrate Scale Again", state="normal")

        threading.Thread(target=run_calibration, daemon=True).start()

    def next_sample(self):
        self.update_buttons_state()
        self.state.elapsed_time = 0.0
        self.state.recorded_data.clear()
        self.start_time = None
        self.processor._initial_distance = None

        # Zerowanie etykiet w GUI
        self.gui.time_label.config(text="Time: 0.000")
        self.gui.deformation_label.config(text="ε: N/A")
        self.gui.initial_distance_label.config(text="Initial Dist: N/A")

        # 🆕 Zerowanie pola do wpisania nazwy pliku
        self.gui.filename_entry.delete(0, 'end')

        self.gui.auto_analysis_var.set(True)
        self.state.auto_analysis_enabled = False
        self.state.auto_analysis_done = False

        # Zerowanie wykresów pojedynczego testu
        self.processor.plot_manager_force.line.set_data([], [])
        self.processor.plot_manager_time.line.set_data([], [])
        self.processor.plot_manager_force_time.line.set_data([], [])
        self.processor.plot_manager_force.canvas.draw()
        self.processor.plot_manager_time.canvas.draw()
        self.processor.plot_manager_force_time.canvas.draw()

    def clear_all(self):
        self.update_buttons_state()

        # Zerowanie danych pomiarowych
        self.state.elapsed_time = 0.0
        self.state.recorded_data.clear()
        self.start_time = None
        self.processor._initial_distance = None

        # Zerowanie etykiet w GUI
        self.gui.time_label.config(text="Time: 0.000")
        self.gui.deformation_label.config(text="ε: N/A")
        self.gui.initial_distance_label.config(text="Initial Dist: N/A")
        self.gui.filename_entry.delete(0, 'end')

        # Zerowanie pojedynczych wykresów
        self.processor.plot_manager_force.line.set_data([], [])
        self.processor.plot_manager_time.line.set_data([], [])
        self.processor.plot_manager_force_time.line.set_data([], [])
        self.processor.plot_manager_force.canvas.draw()
        self.processor.plot_manager_time.canvas.draw()
        self.processor.plot_manager_force_time.canvas.draw()
        self.gui.auto_force_entry.delete(0, 'end')
        self.gui.auto_force_entry.insert(0, "1.0")

        self.gui.auto_speed_entry.delete(0, 'end')
        self.gui.auto_speed_entry.insert(0, "0.01")

        self.gui.auto_analysis_var.set(False)
        self.state.auto_analysis_enabled = False
        self.state.auto_analysis_done = False

        for line in list(self.processor.multi_test_force_plot_manager.ax.lines):
            line.remove()
        legend = self.processor.multi_test_force_plot_manager.ax.get_legend()
        if legend:
            legend.remove()

        self.processor.multi_test_force_plot_manager.canvas.draw()

    def update_buttons_state(self):
        if self.state.is_timer_running:
            # 🔒 Zablokuj tylko przyciski analizy
            self.gui.next_sample_button.config(state="disabled")
            self.gui.clear_button.config(state="disabled")

            # 🔓 Engine przyciski pozostają aktywne
            self.gui.engine_start_button.config(state="normal")
            self.gui.engine_stop_button.config(state="normal")
        else:
            self.gui.next_sample_button.config(state="normal")
            self.gui.clear_button.config(state="normal")
            self.gui.engine_start_button.config(state="normal")
            self.gui.engine_stop_button.config(state="normal")

    def handle_calculate_button(self):
        self.state.calculate_initial_distance = True
        self.gui.calculate_button.config(text="Calculate again")

    def apply_engine_speed(self):
        try:
            speed = float(self.gui.engine_speed_var.get())
            direction = self.gui.engine_dir_var.get()

            if direction not in (0, 1):
                raise ValueError("Invalid direction")
            if not (0.0001 <= speed <= 10.0):
                raise ValueError("Invalid speed")
            print(f"[DEBUG] Apply -> kierunek z GUI: {direction}")

            self.state.engine_speed = speed
            self.state.engine_dir = direction

            print(f"[ENGINE] Parameters saved: direction={direction}, speed={speed:.5f}")

        except ValueError as e:
            print(f"[ENGINE] Invalid input: {e}")

    def engine_save_position(self):
        if self.engine_comm.serial_connection and self.engine_comm.serial_connection.is_open:
            self.engine_comm.send_engine_command("POS:SAVE\n")
            print("[ENGINE] Saved position")
        else:
            print("[ENGINE] Not connected")

    def engine_return_to_position(self):
        if self.engine_comm.serial_connection and self.engine_comm.serial_connection.is_open:
            self.engine_comm.send_engine_command("POS:GOTO\n")
            print("[ENGINE] Returning to saved position")
        else:
            print("[ENGINE] Not connected")

    def apply_analysis_parameters_settings(self):
        try:
            auto_enabled = self.gui.auto_analysis_var.get()
            auto_force = float(self.gui.auto_force_entry.get())
            auto_speed = float(self.gui.auto_speed_entry.get())

            strain_enabled = self.gui.constant_strain_var.get()
            strain_rate = float(self.gui.strain_rate_entry.get())

            if auto_force <= 0:
                raise ValueError("Preload force must be > 0.")
            if not (0.0001 <= auto_speed <= 10.0):
                raise ValueError("Preload speed must be between 0.0001 and 10.0 mm/s.")
            if strain_enabled and strain_rate <= 0:
                raise ValueError("Strain rate must be > 0.")

            self.state.auto_analysis_enabled = auto_enabled
            self.state.auto_target_force = auto_force
            self.state.auto_initial_speed = auto_speed

            self.state.constant_strain_mode = strain_enabled
            self.state.target_strain_rate = strain_rate

            print(f"[PARAMETERS] Preload -> enabled: {auto_enabled}, force: {auto_force}, speed: {auto_speed}")
            print(f"[PARAMETERS] Strain -> enabled: {strain_enabled}, rate: {strain_rate}")

        except ValueError as e:
            from tkinter import messagebox
            messagebox.showerror("Invalid Input", str(e))

    def start_engine(self):
        try:
            direction = self.state.engine_dir
            speed = self.state.engine_speed
            self.engine_comm.send_engine_command(f"DIR:{direction}\n")
            self.engine_comm.send_engine_command(f"SPEED:{speed:.5f}\n")
            self.engine_comm.send_engine_command("START\n")
            print(f"[ENGINE] START -> DIR:{direction}, SPEED:{speed:.5f}")
        except Exception as e:
            print(f"[ENGINE] Start error: {e}")

    def stop_engine(self):
        try:
            self.engine_comm.send_engine_command("STOP\n")
            print("[ENGINE] STOP")
        except Exception as e:
            print(f"[ENGINE] Stop error: {e}")

    def force_blob_detection(self):
        self.state.blobs_ok = False
        self.state.calculate_initial_distance = False
        self.processor._initial_distance = None

        # Pobierz aktualny rozmiar małego ROI
        small_roi_size = self.gui.app_controller.settings.get("small_roi_size", 50)

        # Ustal minimalny bezpieczny odstęp — np. 2x ROI
        offset = small_roi_size * 2

        # Znaczniki po obu stronach środka
        roi1_x = -offset // 2
        roi2_x = offset // 2

        self.gui.app_controller.settings.update({
            "roi1_x": roi1_x,
            "roi1_y": 0,
            "roi2_x": roi2_x,
            "roi2_y": 0
        })

        print(f"[ANALYSIS] Blob detection forced — ROI1={roi1_x}, ROI2={roi2_x}, size={small_roi_size}")


class DataLogger:
    def __init__(self, state):
        self.state = state
        self.running = False


    def log(self, time_val, deformation, force, fps):
        try:
            deformation_val = float(deformation)
            if deformation_val < 0:
                deformation_val = 0.0
            self.state.recorded_data.append(f"{time_val} {deformation} {force} {fps}")
        except ValueError:
            pass




