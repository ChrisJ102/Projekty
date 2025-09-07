import serial
import serial.tools.list_ports
import threading
import queue
import time

class USBCommunication:
    def __init__(self, state, baudrate=9600,mode="engine"):
        self.state = state
        self.baudrate = baudrate
        self.mode = mode
        self.serial_connection = None
        self.read_thread = None
        self.running = False
        self.engine_thread = None

    def connect(self, port):
        try:
            self.serial_connection = serial.Serial(port, self.baudrate, timeout=1)

            if self.mode == "engine":
                self.engine_thread = EngineThread(self.serial_connection)
                self.engine_thread.start()

            elif self.mode == "force":
                self.running = True
                self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
                self.read_thread.start()

            return True
        except Exception as e:
            print(f"[USB] Connection error: {e}")
            return False

    def disconnect(self):
        self.running = False
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
        if self.engine_thread:
            self.engine_thread.stop()
            self.engine_thread = None

    def send_engine_command(self, command):
        if self.engine_thread:
            self.engine_thread.send_command(command)
        else:
            print("[USB] Engine thread not running.")

    def _read_loop(self):
        while self.running:
            try:
                if self.serial_connection and self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode(errors="ignore").strip()
                    if line:
                        try:
                            clean_line = line.replace(" ", "")
                            value = float(clean_line)
                            self.state.latest_force_value = value
                        except ValueError:
                            print(f"[USB] Non-numeric data received: {line}")
            except Exception as e:
                print(f"[USB] Error reading from serial: {e}")
            #time.sleep(0.001)

    def get_latest_data(self):
        return self.state.latest_force_value

    @staticmethod
    def get_serial_devices():
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

class EngineThread:
    def __init__(self, serial_connection):
        self.serial_connection = serial_connection
        self.command_queue = queue.Queue()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.running = False

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.command_queue.put(None)

    def send_command(self, command_str):
        self.command_queue.put(command_str)

    def _run(self):
        while self.running:
            command = self.command_queue.get()
            if command is None:
                break
            try:
                if self.serial_connection and self.serial_connection.is_open:
                    self.serial_connection.write(command.encode())
                    print(f"[ENGINE] Sent: {command.strip()}")
                else:
                    print("[Engine] Serial connection not open.")
            except Exception as e:
                print(f"[Engine] Error sending command: {e}")
            time.sleep(0.01)
