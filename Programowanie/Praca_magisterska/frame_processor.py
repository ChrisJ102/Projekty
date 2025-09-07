from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import queue
import time
import cv2
from PIL import Image, ImageTk
from image_processing import (
    apply_filters, extract_settings, get_roi, get_cached_blob_detector,
    calculate_distance, calculate_deformation, extract_roi_region
)


class FrameProcessor:
    def __init__(self, camera, gui, state):
        self.camera = camera
        self.gui = gui
        self.state = state
        self._last_distances = []
        self._distance_values = []
        self._initial_distance = None
        self.frame_queue = queue.Queue()
        self.running = True
        self._strain_log = []
        self._last_strain_control_time = 0
        self.last_logged_frame_id = -1


        self.plot_manager_force = PlotManager(self.gui.group4_force_frame)
        self.plot_manager_time = TimePlotManager(self.gui.group4_time_frame)
        self.plot_manager_force_time = ForceTimePlotManager(self.gui.group4_force_time_frame)
        self.multi_test_force_plot_manager = MultiTestForcePlotManager(self.gui.group4_multi_test_force_frame)

        self.last_active_tab = 0
        self.gui.chart_notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        self.active_settings = extract_settings(self.gui.entries, self.gui.grayscale_var, self.gui.negative_var)

    def start(self):
        threading.Thread(target=self._processing_loop, daemon=True).start()
        self._update_image_from_queue()
        self._update_labels_from_queue()
        self.update_plot_periodically()

    def _processing_loop(self):
        while self.running:
            frame, frame_id = self.camera.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            s = self.active_settings
            roi_width = s["roi_width"]
            roi_height = s["roi_height"]
            roi_size = self.gui.app_controller.settings["small_roi_size"]

            display_roi, (roi_offset_x, roi_offset_y, _, _) = get_roi(frame, roi_width, roi_height)
            display_with_boxes = display_roi.copy()

            if not self.state.blobs_ok:
                self._detect_initial_blobs(display_roi, s, roi_width, roi_height)

            keypoints1, keypoints2, roi1_x, roi1_y, roi2_x, roi2_y = self._prepare_rois(
                frame, s, roi_offset_x, roi_offset_y, roi_width, roi_height, roi_size, display_with_boxes
            )

            distance = deformation = None
            if len(keypoints1) == 1 and len(keypoints2) == 1:
                kp1 = keypoints1[0].pt
                kp2 = keypoints2[0].pt
                global_kp1 = (kp1[0] + roi1_x - roi_size // 2, kp1[1] + roi1_y - roi_size // 2)
                global_kp2 = (kp2[0] + roi2_x - roi_size // 2, kp2[1] + roi2_y - roi_size // 2)
                distance = calculate_distance(global_kp1, global_kp2)

                if self.state.calculate_initial_distance:
                    self._distance_values.append(distance)
                    if len(self._distance_values) >= 5:
                        self._initial_distance = sum(self._distance_values) / len(self._distance_values)
                        self.state.calculate_initial_distance = False
                        self._distance_values.clear()
                    if self.gui and hasattr(self.gui, "calculate_button"):
                        self.gui.app.after(0, lambda: self.gui.calculate_button.config(text="Calculate again"))

                if self._initial_distance:
                    deformation = calculate_deformation(distance, self._initial_distance)
                    self._handle_constant_strain_rate_control(deformation, distance)

            if self.state.blobs_ok:
                self._update_roi_tracking(keypoints1, keypoints2, roi1_x, roi1_y, roi2_x, roi2_y,
                                          roi_offset_x, roi_offset_y, roi_width, roi_height, roi_size)

            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break

            self.frame_queue.put({
                "image": display_with_boxes,
                "distance": distance,
                "initial_distance": self._initial_distance,
                "deformation": deformation,
                "blobs": len(keypoints1) + len(keypoints2)
            })

            if self.state.is_timer_running and frame_id != self.last_logged_frame_id:
                self.last_logged_frame_id = frame_id
                current_time = round(time.time() - self.gui.logic.start_time, 3)
                force = self.state.latest_force_value if self.state.latest_force_value else "N/A"
                deformation_val = deformation if deformation is not None else "N/A"
                fps_val = self.camera.fps
                self.gui.logic.logger.log(current_time, deformation_val, force, fps_val)

    def _handle_constant_strain_rate_control(self, deformation, distance):
        if (
                not self.state.constant_strain_mode or
                not self.state.is_timer_running or
                not self.state.px_to_mm_ratio or
                not distance or
                deformation is None
        ):
            return

        now = time.time()

        if not self.gui.logic.start_time or (now - self.gui.logic.start_time < 1.0):
            return  # pomijamy 1. sekundę od startu

        if not hasattr(self, "_last_strain_control_time"):
            self._last_strain_control_time = 0

        if now - self._last_strain_control_time < 1.0:
            return  # sterujemy nie częściej niż co 1 sekundę

        strain_rate = self.state.target_strain_rate
        mm_per_px = self.state.px_to_mm_ratio
        l_px = distance
        elapsed = now - self.gui.logic.start_time

        expected_deformation = strain_rate * elapsed
        deformation_error = expected_deformation - deformation
        percent_error = deformation_error / max(abs(expected_deformation), 1e-6)

        print(
            f"[STR-CONTROL] ε_expected: {expected_deformation:.6f} | ε_actual: {deformation:.6f} | Error: {percent_error:.2%}")

        if abs(percent_error) > 0.01:
            v_mm_s = l_px * strain_rate * mm_per_px
            v_mm_s = max(0.001, min(v_mm_s, 10.0))
            print(f"[STR-CONTROL] v_now = {v_mm_s:.6f} | v_last = {getattr(self, '_last_sent_speed', None)}")

            if not hasattr(self, "_last_sent_speed"):
                send = True
            else:
                abs_diff = abs(v_mm_s - self._last_sent_speed)
                if abs_diff > 0.001:
                    send = True
                    print(f"[STR-CONTROL] Δv = {abs_diff:.6f} mm/s -> sending update")
                else:
                    send = False
                    print(f"[STR-CONTROL] Δv = {abs_diff:.6f} mm/s -> skip")

            if send and hasattr(self.gui.app_controller, "engine_comm") and self.gui.app_controller.engine_comm:
                cmd = f"SPEED:{v_mm_s:.5f}\n"
                self.gui.app_controller.engine_comm.send_engine_command(cmd)
                self._last_sent_speed = v_mm_s
                print(f"[STR-CONTROL] Sent: {cmd.strip()}")

        # zaktualizuj znacznik czasu nawet jeśli nie wysłano
        self._last_strain_control_time = now

    def _detect_initial_blobs(self, roi, settings, roi_width, roi_height):
        filtered = apply_filters(roi.copy(), settings)
        detector = get_cached_blob_detector(settings["min_area"], settings["max_area"])
        keypoints = detector.detect(filtered)

        if len(keypoints) == 2:
            kp1, kp2 = sorted(keypoints, key=lambda k: k.pt[0])
            roi1_x_rel = int(kp1.pt[0] - roi_width // 2)
            roi1_y_rel = int(kp1.pt[1] - roi_height // 2)
            roi2_x_rel = int(kp2.pt[0] - roi_width // 2)
            roi2_y_rel = int(kp2.pt[1] - roi_height // 2)

            self.gui.app_controller.settings.update({
                "roi1_x": roi1_x_rel,
                "roi1_y": roi1_y_rel,
                "roi2_x": roi2_x_rel,
                "roi2_y": roi2_y_rel
            })

            self.state.blobs_ok = True
            print(f"[ROI] 2 markers found. ROI1=({roi1_x_rel},{roi1_y_rel}) ROI2=({roi2_x_rel},{roi2_y_rel})")

    def _prepare_rois(self, frame, s, ox, oy, w, h, roi_size, display):
        rel = self.gui.app_controller.settings
        rel1_x = rel["roi1_x"] + ox + w // 2
        rel1_y = rel["roi1_y"] + oy + h // 2
        rel2_x = rel["roi2_x"] + ox + w // 2
        rel2_y = rel["roi2_y"] + oy + h // 2

        roi1 = extract_roi_region(frame, rel1_x, rel1_y, roi_size)
        roi2 = extract_roi_region(frame, rel2_x, rel2_y, roi_size)
        proc1 = apply_filters(roi1.copy(), s)
        proc2 = apply_filters(roi2.copy(), s)

        detector = get_cached_blob_detector(s["min_area"], s["max_area"])
        kps1 = detector.detect(proc1)
        kps2 = detector.detect(proc2)

        for proc, kps, cx, cy in [(proc1, kps1, rel1_x, rel1_y), (proc2, kps2, rel2_x, rel2_y)]:
            if len(proc.shape) == 2:
                proc = cv2.cvtColor(proc, cv2.COLOR_GRAY2BGR)
            with_blobs = cv2.drawKeypoints(proc, kps, None, (0, 255, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            with_blobs = cv2.resize(with_blobs, (roi_size, roi_size))
            self._paste_roi(display, with_blobs, cx, cy, ox, oy)

        return kps1, kps2, rel1_x, rel1_y, rel2_x, rel2_y

    def _update_roi_tracking(self, kps1, kps2, x1, y1, x2, y2, ox, oy, w, h, roi_size):
        alpha = 0.3
        max_rx, max_ry = w // 2, h // 2

        def smooth(keypoint, current_x, current_y, abs_x, abs_y):
            if keypoint is None:
                return current_x, current_y
            new_abs_x = keypoint.pt[0] + abs_x - roi_size // 2
            new_abs_y = keypoint.pt[1] + abs_y - roi_size // 2
            new_rel_x = new_abs_x - ox - w // 2
            new_rel_y = new_abs_y - oy - h // 2
            sx = int((1 - alpha) * current_x + alpha * new_rel_x)
            sy = int((1 - alpha) * current_y + alpha * new_rel_y)
            sx = max(-max_rx + roi_size // 2, min(max_rx - roi_size // 2, sx))
            sy = max(-max_ry + roi_size // 2, min(max_ry - roi_size // 2, sy))
            return sx, sy

        rel = self.gui.app_controller.settings
        curr1_x, curr1_y = rel["roi1_x"], rel["roi1_y"]
        curr2_x, curr2_y = rel["roi2_x"], rel["roi2_y"]

        rel["roi1_x"], rel["roi1_y"] = smooth(kps1[0] if len(kps1) == 1 else None, curr1_x, curr1_y, x1, y1)
        rel["roi2_x"], rel["roi2_y"] = smooth(kps2[0] if len(kps2) == 1 else None, curr2_x, curr2_y, x2, y2)

    def _paste_roi(self, base, roi_img, cx, cy, ox, oy):
        h, w = roi_img.shape[:2]
        x1 = int(cx - w // 2) - ox
        y1 = int(cy - h // 2) - oy
        x2 = x1 + w
        y2 = y1 + h
        if 0 <= x1 < x2 <= base.shape[1] and 0 <= y1 < y2 <= base.shape[0]:
            base[y1:y2, x1:x2] = roi_img
            cv2.rectangle(base, (x1, y1), (x2, y2), (255, 0, 0), 2)

    def _update_image_from_queue(self):
        try:
            data = self.frame_queue.queue[-1]
            image = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(data["image"], cv2.COLOR_BGR2RGBA)))
            self.gui.label_widget.photo_image = image
            self.gui.label_widget.configure(image=image)
        except IndexError:
            pass

        self.gui.app.after(10, self._update_image_from_queue)

    def _update_labels_from_queue(self):
        try:
            data = self.frame_queue.queue[-1]
            self.gui.blob_count_label.config(text=f"Detected Blobs: {data['blobs']}")
            self.gui.detected_blobs_gui_label.config(text=f"Detected Blobs: {data['blobs']}")
            if hasattr(self.gui, "distance_gui_label"):
                if data["distance"] is not None:
                    self.gui.distance_gui_label.config(text=f"Distance: {data['distance']:.3f}")
                else:
                    self.gui.distance_gui_label.config(text="Distance: N/A")

            self.gui.fps_label.config(text=f"FPS: {self.camera.fps:.3f}")

            if data["distance"] is not None:
                self.gui.distance_label.config(text=f"Distance: {data['distance']:.3f}")
            else:
                self.gui.distance_label.config(text="Distance: N/A")

            if data["initial_distance"]:
                self.gui.initial_distance_label.config(text=f"Initial Dist: {data['initial_distance']:.3f}")

            if data["deformation"] is not None:
                deformation_val = max(0.0, data["deformation"])
                self.gui.deformation_label.config(text=f"ε: {deformation_val:.6f}")
            else:
                self.gui.deformation_label.config(text="ε: N/A")

        except IndexError:
            pass

        self.gui.app.after(100, self._update_labels_from_queue)

    def on_tab_changed(self, event):
        index = self.gui.chart_notebook.index("current")
        if not self.state.is_timer_running and self.state.recorded_data:
            if index == 0:
                self.plot_manager_force.update_plot(self.state.recorded_data)
            elif index == 1:
                self.plot_manager_time.update_plot(self.state.recorded_data)
            elif index == 2:
                self.plot_manager_force_time.update_plot(self.state.recorded_data)

    def update_plot_periodically(self):
        index = self.gui.chart_notebook.index("current")
        if self.state.is_timer_running and self.state.recorded_data:
            if index == 0:
                self.plot_manager_force.update_plot(self.state.recorded_data)
            elif index == 1:
                self.plot_manager_time.update_plot(self.state.recorded_data)
            elif index == 2:
                self.plot_manager_force_time.update_plot(self.state.recorded_data)

        self.gui.app.after(1200, self.update_plot_periodically)

    def update_active_settings(self):
        self.active_settings = extract_settings(self.gui.entries, self.gui.grayscale_var, self.gui.negative_var)

    def save_plots_as_png(self, base_filename):
        try:
            if self.state.recorded_data:
                self.plot_manager_force.update_plot(self.state.recorded_data)
                self.plot_manager_time.update_plot(self.state.recorded_data)
                self.plot_manager_force_time.update_plot(self.state.recorded_data)

            self.plot_manager_force.fig.savefig(f"{base_filename}_DvF.png", facecolor='black')
            self.plot_manager_time.fig.savefig(f"{base_filename}_DoT.png", facecolor='black')
            self.plot_manager_force_time.fig.savefig(f"{base_filename}_FoT.png", facecolor='black')
            self.multi_test_force_plot_manager.fig.savefig(f"{base_filename}_MultiTests_DvF.png", facecolor='black')

            print("[ANALYSIS] Charts saved as PNG.")
        except Exception as e:
            print(f"[ANALYSIS] Error saving charts: {e}")


class BasePlotManager:
    def __init__(self, parent_frame, title, xlabel, ylabel, marker, linestyle, color):
        self.fig = Figure(figsize=(8, 2.2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(title, fontsize=12)
        self.ax.set_xlabel(xlabel, fontsize=10, labelpad=4)
        self.ax.set_ylabel(ylabel, fontsize=10, labelpad=10)
        self.ax.grid(True)

        self._apply_dark_theme()

        self.line, = self.ax.plot([], [], marker=marker, linestyle=linestyle, color=color)
        self._finalize_canvas(parent_frame)

    def _apply_dark_theme(self):
        self.ax.set_facecolor("black")
        self.fig.patch.set_facecolor("black")
        self.ax.tick_params(axis='x', colors='white')
        self.ax.tick_params(axis='y', colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.fig.subplots_adjust(left=0.08, right=0.98, top=0.85, bottom=0.20)




    def _finalize_canvas(self, parent_frame):
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.get_tk_widget().configure(height=400)


class PlotManager(BasePlotManager):
    def __init__(self, parent_frame):
        super().__init__(
            parent_frame,
            title="Deformation vs. Force",
            xlabel="Deformation (ε)",
            ylabel="Force (N)",
            marker='o',
            linestyle='-',
            color='white'
        )

    def update_plot(self, data):
        try:
            points = []
            for line in data:
                if "N/A" in line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    _, d, f = parts[:3]
                    points.append((float(d), float(f)))  # ε, siła
            if points:
                deformations, forces = zip(*points)
                self.line.set_data(deformations, forces)
                self.ax.relim()
                self.ax.autoscale_view()
            self.canvas.draw()
        except Exception:
            pass


class TimePlotManager(BasePlotManager):
    def __init__(self, parent_frame):
        super().__init__(
            parent_frame,
            title="Deformation over Time",
            xlabel="Time (s)",
            ylabel="Deformation (ε)",
            marker='x',
            linestyle='--',
            color='blue'
        )

    def update_plot(self, data):
        try:
            points = []
            for line in data:
                if "N/A" in line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    t, d, _ = parts[:3]
                    points.append((float(t), float(d)))  # czas, ε
            if points:
                times, deformations = zip(*points)
                self.line.set_data(times, deformations)
                self.ax.relim()
                self.ax.autoscale_view()
            self.canvas.draw()
        except Exception:
            pass


class ForceTimePlotManager(BasePlotManager):
    def __init__(self, parent_frame):
        super().__init__(
            parent_frame,
            title="Force over Time",
            xlabel="Time (s)",
            ylabel="Force (N)",
            marker='o',
            linestyle='--',
            color='green'
        )

    def update_plot(self, data):
        try:
            points = []
            for line in data:
                if "N/A" in line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    t, _, f = parts[:3]
                    points.append((float(t), float(f)))  # czas, siła
            if points:
                times, forces = zip(*points)
                self.line.set_data(times, forces)
                self.ax.relim()
                self.ax.autoscale_view()
            self.canvas.draw()
        except Exception:
            pass

class MultiTestForcePlotManager(BasePlotManager):
    def __init__(self, parent_frame):
        super().__init__(
            parent_frame,
            title="Multiple Tests: Deformation vs Force",
            xlabel="Deformation (ε)",
            ylabel="Force (N)",
            marker='o',
            linestyle='',
            color='white'
        )
        self.series = []  # lista linii (Line2D)
        self.test_counter = 1  # licznik prób

    def add_series(self, points):
        if points:
            deformations, forces = zip(*points)
            # Każda seria nowa linia
            new_line, = self.ax.plot(deformations, forces, marker='o', linestyle='-', linewidth=1, label=f"Test {self.test_counter}")
            self.series.append(new_line)
            self.test_counter += 1

            self.ax.relim()
            self.ax.autoscale_view()

            # Aktualizacja legendy
            self.ax.legend(loc="best", fontsize=8, facecolor='black', edgecolor='white', labelcolor='white')

            self.canvas.draw()

