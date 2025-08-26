from tkinter import *
from tkinter import ttk
from gui_logic import AppLogic
from usbcommunication import USBCommunication
from tkinter.scrolledtext import ScrolledText

FONT_LABEL = ("Arial", 11)
FONT_ENTRY = ("Arial", 10)
FONT_BUTTON = ("Arial", 10)
BUTTON_HEIGHT = 1
BUTTON_WIDTH = 11

COLOR_BG = "black"
COLOR_FG = "white"
COLOR_ENTRY_BG = "gray"
COLOR_ENTRY_FG = "black"
COLOR_SELECT = "green"
COLOR_LINE = "white"
COLOR_HIGHLIGHT = "black"

class AppGUI:
    def __init__(self, app, settings, update_gui_callback, state):
        self.app = app
        self.settings = settings
        self.state = state
        self.update_gui_callback = update_gui_callback
        self.usb_comm = USBCommunication(state, baudrate=115200, mode="force")
        self.engine_comm = USBCommunication(state, baudrate=115200, mode="engine")
        self.logic = AppLogic(self)
        self._setup_ui()
        self.app_controller = None

    def _setup_ui(self):
        self.app.title("App")
        self.app.configure(bg=COLOR_BG)

        self.main_frame = Frame(self.app, bg=COLOR_BG)
        self.main_frame.pack(fill=BOTH, expand=True)

        self._create_video_frame()
        self._create_bottom_layout()

        self.label_widget.after(10, self.update_gui_callback)
        self._disable_tab_autofocus()

    def _disable_tab_autofocus(self):
        def remove_focus(event):
            self.app.after_idle(lambda: self.app.focus_set())
        self.control_notebook.bind("<<NotebookTabChanged>>", remove_focus)

    def _create_video_frame(self):
        self.video_frame = Frame(self.main_frame, bg=COLOR_BG)
        self.video_frame.pack(fill=X, padx=10, pady=(5, 0))

        self.label_widget = Label(self.video_frame, bg=COLOR_BG)
        self.label_widget.pack()
    def _create_bottom_layout(self):
        # Zakładki sterujące
        self.control_notebook = ttk.Notebook(self.main_frame)
        self.control_notebook.pack(fill=X, padx=10, pady=(5, 0))

        # Kamera - zakładka 1
        self.camera_tab = Frame(self.control_notebook, bg=COLOR_BG)
        self.control_notebook.add(self.camera_tab, text="Camera Settings")

        self.camera_inner_frame = Frame(self.camera_tab, bg=COLOR_BG)
        self.camera_inner_frame.pack(fill="x", padx=10, pady=(10, 5), anchor="nw")

        self._create_settings_controls(self.camera_inner_frame)

        # Analiza - zakładka 2
        self.analysis_tab = Frame(self.control_notebook, bg=COLOR_BG)
        self.control_notebook.add(self.analysis_tab, text="Analysis")

        self.analysis_tab_inner = Frame(self.analysis_tab, bg=COLOR_BG)
        self.analysis_tab_inner.pack(fill="x", padx=5, pady=5)

        self.info_frame = LabelFrame(self.analysis_tab_inner, text="Info", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.info_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self._create_info_section(self.info_frame)

        self.engine_frame = LabelFrame(self.analysis_tab_inner, text="Engine", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.engine_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self._create_engine_section(self.engine_frame)

        self.analysis_frame = LabelFrame(self.analysis_tab_inner, text="Analysis", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.analysis_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)
        self._create_analysis_section(self.analysis_frame)

        # Zakładki wykresów
        self.chart_notebook = ttk.Notebook(self.main_frame)
        self.chart_notebook.pack(fill="x", padx=10, pady=(0, 10), expand=False)
        self.chart_notebook.configure(height=300)

        self.force_tab = Frame(self.chart_notebook, bg=COLOR_BG)
        self.time_tab = Frame(self.chart_notebook, bg=COLOR_BG)
        self.force_time_tab = Frame(self.chart_notebook, bg=COLOR_BG)
        self.multi_test_force_tab = Frame(self.chart_notebook, bg=COLOR_BG)

        self.chart_notebook.add(self.force_tab, text="Deformation vs. Force")
        self.chart_notebook.add(self.time_tab, text="Deformation over Time")
        self.chart_notebook.add(self.force_time_tab, text="Force over Time")
        self.chart_notebook.add(self.multi_test_force_tab, text="Multiple Tests: Deformation vs Force")

        self.group4_multi_test_force_frame = self.multi_test_force_tab
        self.group4_force_time_frame = self.force_time_tab
        self.group4_force_frame = self.force_tab
        self.group4_time_frame = self.time_tab

        self.log_box = ScrolledText(self.main_frame, height=5, state='disabled', font=("Courier", 9), bg=COLOR_BG,
                                    fg=COLOR_FG)
        self.log_box.pack(fill='x', padx=10, pady=(0, 10))

    def _create_settings_controls(self, parent):
        self.entries = {}

        for col in range(8):
            parent.grid_columnconfigure(col, weight=0)

        # Wiersz 0
        self._add_input("Contrast", "contrast", 0, 0, parent)
        self._add_input("Brightness", "brightness", 0, 2, parent)

        # Detected Blobs (readonly label)
        self.detected_blobs_gui_label = Label(
            parent,
            text="Detected Blobs: 0",
            bg=COLOR_BG,
            fg=COLOR_FG,
            font=FONT_LABEL,
            anchor="w"
        )
        self.detected_blobs_gui_label.grid(row=0, column=4, columnspan=2, padx=0, pady=2, sticky="w")

        self.distance_gui_label = Label(
            parent,
            text="Distance: N/A",
            bg=COLOR_BG,
            fg=COLOR_FG,
            font=FONT_LABEL,
            anchor="w"
        )
        self.distance_gui_label.grid(row=1, column=4, columnspan=2, padx=0, pady=2, sticky="w")

        # Wiersz 1
        self._add_input("Min Area", "minArea", 1, 0, parent)
        self._add_input("Max Area", "maxArea", 1, 2, parent)


        # Wiersz 2
        self._add_input("ROI Width", "roi_width", 2, 0, parent)
        self._add_input("ROI Height", "roi_height", 2, 2, parent)

        self._add_input("Small ROI Size", "small_roi_size", 2, 4, parent)

        # Wiersz 3 – checkboxy i small ROI size
        self.grayscale_var = BooleanVar(value=self.settings["grayscale"])
        self._add_checkbox("Grayscale", self.grayscale_var, 3, 0, parent, self._on_checkbox_change)

        self.negative_var = BooleanVar(value=self.settings["negative"])
        self._add_checkbox("Negative", self.negative_var, 3, 1, parent, self._on_checkbox_change)

        self.calibrate_scale_button = Button(
            parent,
            text="Calibrate Scale",
            command=self.logic.dynamic_scale_calibration,
            font=FONT_BUTTON,
            height=BUTTON_HEIGHT,
            width=16
        )
        self.calibrate_scale_button.grid(row=3, column=2, columnspan=2, padx=5, pady=2, sticky="w")


        self.scale_label = Label(
            parent,
            text="Scale: N/A",
            bg=COLOR_BG,
            fg=COLOR_FG,
            font=FONT_LABEL,
            anchor="w"
        )
        self.scale_label.grid(row=3, column=4, columnspan=2, padx=0, pady=2, sticky="w")

        # Wiersz 4
        self.detect_blobs_button = Button(parent, text="Detect blobs", command=self.logic.force_blob_detection, font=FONT_BUTTON, height=BUTTON_HEIGHT,width=12)
        self.detect_blobs_button.grid(row=4, column=1, padx=5, pady=4, sticky="w")

        self.apply_button = Button(parent, text="Apply changes", command=self._apply_settings,
                                   font=FONT_BUTTON, height=BUTTON_HEIGHT, width=12)
        self.apply_button.grid(row=4, column=2, padx=5, pady=4, sticky="w")

    def _create_info_section(self, parent):
        label_width = 15

        # Rząd 0: FPS + Detected Blobs
        self.fps_label = Label(parent, text="FPS: N/A", width=label_width,
                               anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.fps_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        self.blob_count_label = Label(parent, text="Detected Blobs: 0", width=label_width,
                                      anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.blob_count_label.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Rząd 1: COM + Refresh + Connect
        self.device_list = self.usb_comm.get_serial_devices()
        default_device = self.device_list[0] if self.device_list else "No devices found"
        self.device_var = StringVar(value=default_device)
        self.device_combobox = ttk.Combobox(parent, textvariable=self.device_var, values=self.device_list,
                                            state="readonly", font=FONT_ENTRY, width=10)
        self.device_combobox.grid(row=1, column=0, padx=5, pady=4, sticky="ew")

        self.refresh_button = Button(parent, text="Refresh", command=lambda: self.logic.refresh_ports("force"),
                                     font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.refresh_button.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        self.connect_button = Button(parent, text="Connect", command=lambda: self.logic.connect_to("force"),
                                     font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.connect_button.grid(row=1, column=2, padx=5, pady=4, sticky="ew")

        # Rząd 2: Distance + Initial Dist + Calculate
        self.distance_label = Label(parent, text="Distance: N/A", width=label_width,
                                    anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.distance_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.initial_distance_label = Label(parent, text="Initial Dist: N/A", width=label_width,
                                            anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.initial_distance_label.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.calculate_button = Button(parent, text="Calculate", font=FONT_BUTTON, height=BUTTON_HEIGHT,
                                       command=self.logic.handle_calculate_button, width=BUTTON_WIDTH)
        self.calculate_button.grid(row=2, column=2, padx=5, pady=2, sticky="w")

        # Rząd 3: ε i Force
        self.deformation_label = Label(parent, text="ε: N/A", width=label_width,
                                       anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.deformation_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.force_label = Label(parent, text="Force: ---", width=label_width,
                                 anchor="w", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.force_label.grid(row=3, column=1, padx=5, pady=2, sticky="w")

    def _create_analysis_section(self, parent):
        self.analysis_frame = Frame(parent, bg=COLOR_BG)
        self.analysis_frame.grid(row=0, column=2, sticky="nsew", padx=5, pady=5)

        self.time_label = Label(self.analysis_frame, text="Time: 0.000", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL)
        self.time_label.grid(row=0, column=0, columnspan=2, padx=5, pady=(2, 4), sticky="w")

        self.start_button = Button(self.analysis_frame, text="Start", command=self.logic.start_timer,
                                   height=BUTTON_HEIGHT, width=BUTTON_WIDTH, font=FONT_BUTTON,
                                   bg="green", fg="white", activebackground="#006400")
        self.start_button.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.stop_button = Button(self.analysis_frame, text="Stop", command=self.logic.stop_timer,
                                  height=BUTTON_HEIGHT, width=BUTTON_WIDTH, font=FONT_BUTTON,
                                  bg="red", fg="white", activebackground="#8B0000")
        self.stop_button.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        self.filename_entry = Entry(self.analysis_frame, width=15, font=FONT_ENTRY)
        self.filename_entry.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        self.save_button = Button(self.analysis_frame, text="Save", command=self.logic.save_data_to_file,
                                  font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.save_button.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.next_sample_button = Button(self.analysis_frame, text="Next Sample", command=self.logic.next_sample,
                                         font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.next_sample_button.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.clear_button = Button(self.analysis_frame, text="Clear", command=self.logic.clear_all,
                                   font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.clear_button.grid(row=3, column=1, padx=5, pady=2, sticky="w")

        self._create_analysis_parameters_section(parent)

    def _create_analysis_parameters_section(self, parent):
        self.analysis_param_frame = LabelFrame(parent, text="Analysis Parameters", bg=COLOR_BG, fg=COLOR_FG,
                                               font=FONT_LABEL)
        self.analysis_param_frame.grid(row=0, column=3, sticky="nsew", padx=5, pady=5)

        # Mini układ: label + entry + label + entry w 1 rzędzie (bez rozciągania kolumn)
        self.auto_analysis_var = BooleanVar(value=False)
        self.auto_analysis_checkbox = Checkbutton(self.analysis_param_frame, text="Pre-tension sample",
                                                  variable=self.auto_analysis_var, bg=COLOR_BG, fg=COLOR_FG,
                                                  font=FONT_LABEL, selectcolor=COLOR_SELECT,
                                                  activebackground=COLOR_HIGHLIGHT)
        self.auto_analysis_checkbox.grid(row=0, column=0, columnspan=4, sticky="w", padx=5)

        Label(self.analysis_param_frame, text="Force:", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL).grid(row=1, column=0,
                                                                                                        sticky="w",
                                                                                                        padx=(5, 2))
        self.auto_force_var = StringVar(value="1.0")
        self.auto_force_entry = Entry(self.analysis_param_frame, textvariable=self.auto_force_var, font=FONT_ENTRY,
                                      width=10, bg=COLOR_ENTRY_BG)
        self.auto_force_entry.grid(row=1, column=1, sticky="w", padx=(2, 10))

        Label(self.analysis_param_frame, text="Speed:", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL).grid(row=1, column=2,
                                                                                                        sticky="w",
                                                                                                        padx=(5, 2))
        self.auto_speed_var = StringVar(value="0.05")
        self.auto_speed_entry = Entry(self.analysis_param_frame, textvariable=self.auto_speed_var, font=FONT_ENTRY,
                                      width=10, bg=COLOR_ENTRY_BG)
        self.auto_speed_entry.grid(row=1, column=3, sticky="w", padx=(2, 5))

        self.constant_strain_var = BooleanVar(value=False)
        self.constant_strain_checkbox = Checkbutton(self.analysis_param_frame, text="Constant strain rate",
                                                    variable=self.constant_strain_var, bg=COLOR_BG, fg=COLOR_FG,
                                                    font=FONT_LABEL, selectcolor=COLOR_SELECT,
                                                    activebackground=COLOR_HIGHLIGHT)
        self.constant_strain_checkbox.grid(row=2, column=0, columnspan=4, sticky="w", padx=5)

        # Strain rate w jednym wierszu – label zajmuje dwie kolumny, potem entry + apply
        Label(self.analysis_param_frame, text="Strain rate [1/s]:", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL).grid(
            row=3, column=0, columnspan=2, sticky="w", padx=(5, 2))

        self.strain_rate_var = StringVar(value="0.001")
        self.strain_rate_entry = Entry(self.analysis_param_frame, textvariable=self.strain_rate_var,
                                       font=FONT_ENTRY, width=8, bg=COLOR_ENTRY_BG)
        self.strain_rate_entry.grid(row=3, column=2, sticky="w", padx=(2, 5))

        self.analysis_param_apply_button = Button(self.analysis_param_frame, text="Apply",
                                                  command=self.logic.apply_analysis_parameters_settings,
                                                  font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.analysis_param_apply_button.grid(row=3, column=3, padx=5, pady=2, sticky="w")

    def _create_engine_section(self, parent):
        #Row 0 — COM port selection
        self.engine_device_list = self.usb_comm.get_serial_devices()
        default_engine = self.engine_device_list[0] if self.engine_device_list else "No devices found"
        self.engine_device_var = StringVar(value=default_engine)
        self.engine_combobox = ttk.Combobox(
            parent,
            textvariable=self.engine_device_var,
            values=self.engine_device_list,
            state="readonly",
            font=FONT_ENTRY,
            width=10
        )
        self.engine_combobox.grid(row=0, column=0, padx=5, pady=4, sticky="ew")

        self.engine_refresh_button = Button(
            parent,
            text="Refresh",
            command=lambda: self.logic.refresh_ports("engine"),
            font=FONT_BUTTON,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        self.engine_refresh_button.grid(row=0, column=1, padx=5, pady=4, sticky="ew")

        self.engine_connect_button = Button(
            parent,
            text="Connect",
            command=lambda: self.logic.connect_to("engine"),
            font=FONT_BUTTON,
            height=BUTTON_HEIGHT,
            width=BUTTON_WIDTH
        )
        self.engine_connect_button.grid(row=0, column=2, padx=5, pady=4, sticky="ew")

        #Row 1 — Direction: Stretch / Compress
        Label(parent, text="Direction:", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL).grid(row=1, column=0, padx=5,
                                                                                         pady=2, sticky="w")

        self.engine_dir_var = IntVar(value=1)

        Radiobutton(parent, text="Stretch", variable=self.engine_dir_var, value=1,
                    bg=COLOR_BG, fg=COLOR_FG, selectcolor=COLOR_SELECT,
                    font=FONT_LABEL, activebackground=COLOR_HIGHLIGHT).grid(row=1, column=1, sticky="w", padx=5)

        Radiobutton(parent, text="Compress", variable=self.engine_dir_var, value=0,
                    bg=COLOR_BG, fg=COLOR_FG, selectcolor=COLOR_SELECT,
                    font=FONT_LABEL, activebackground=COLOR_HIGHLIGHT).grid(row=1, column=2, sticky="w", padx=5)

        #Row 2 — Speed input + Apply + Start + Save position
        Label(parent, text="Speed [mm/s]:", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL).grid(row=2, column=0, padx=5,
                                                                                            pady=2, sticky="w")

        self.engine_speed_var = StringVar(value="0.010")
        self.engine_speed_entry = Entry(parent, textvariable=self.engine_speed_var, width=8, font=FONT_ENTRY,
                                        bg=COLOR_ENTRY_BG, fg=COLOR_ENTRY_FG)
        self.engine_speed_entry.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        self.engine_speed_button = Button(parent, text="Apply",
                                          command=self.logic.apply_engine_speed,
                                          font=FONT_BUTTON, height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.engine_speed_button.grid(row=2, column=2, padx=5, pady=2, sticky="w")

        self.engine_start_button = Button(parent, text="Start",
                                          command=self.logic.start_engine,
                                          font=FONT_BUTTON,
                                          height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.engine_start_button.grid(row=2, column=3, padx=5, pady=2, sticky="w")

        #Row 3 — Save position + Return to position (wide) + Stop
        self.engine_save_position_button = Button(parent, text="Save position",
                                                  command=self.logic.engine_save_position,
                                                  font=FONT_BUTTON, width=BUTTON_WIDTH)
        self.engine_save_position_button.grid(row=3, column=0, padx=5, pady=2, sticky="w")

        self.engine_return_position_button = Button(parent, text="Return to position",
                                                    command=self.logic.engine_return_to_position,
                                                    font=FONT_BUTTON, width=16)  # szerszy przycisk
        self.engine_return_position_button.grid(row=3, column=1, columnspan=2, padx=5, pady=2, sticky="we")

        self.engine_stop_button = Button(parent, text="Stop",
                                         command=self.logic.stop_engine,
                                         font=FONT_BUTTON,
                                         height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
        self.engine_stop_button.grid(row=3, column=3, padx=5, pady=5, sticky="w")

    def _add_input(self, label_text, setting_key, row, col, parent):
        label = Label(parent, text=label_text + ":", bg=COLOR_BG, fg=COLOR_FG, font=FONT_LABEL, anchor="e")
        label.grid(row=row, column=col, padx=(0, 2), pady=2, sticky="w")

        entry = Entry(parent, width=6, bg=COLOR_ENTRY_BG, fg=COLOR_ENTRY_FG, font=FONT_ENTRY,
                      highlightthickness=0, bd=1, relief="solid")

        default_value = self.settings.get(setting_key, "10.0" if setting_key == "real_distance_mm" else "0")
        entry.insert(0, str(default_value))

        entry.grid(row=row, column=col + 1, padx=(0, 8), pady=2, sticky="w")

        self.entries[setting_key] = entry

    def _add_checkbox(self, text, variable, row, col, parent, command=None):
        checkbox = Checkbutton(parent, text=text, variable=variable, bg=COLOR_BG, fg=COLOR_FG,
                               font=FONT_LABEL, selectcolor=COLOR_SELECT, activebackground=COLOR_HIGHLIGHT,
                               anchor="w", command=command, height=1)
        checkbox.grid(row=row, column=col, padx=5, pady=(2, 0), sticky="nw")

    def _apply_settings(self):
        self.logic.validate_and_apply_settings()

    def _on_checkbox_change(self):
        if hasattr(self.logic, "processor"):
            self.logic.processor.update_active_settings()

def create_gui(app, settings, update_gui_callback, state):
    return AppGUI(app, settings, update_gui_callback, state)
