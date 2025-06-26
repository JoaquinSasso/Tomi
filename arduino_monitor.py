import os
import time
import serial
import serial.tools.list_ports


def find_arduino_port():
    """Return the device name of the first likely Arduino port."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if (
            "Arduino" in port.description
            or "ttyACM" in port.device
            or "ttyUSB" in port.device
            or "usbmodem" in port.device
        ):
            return port.device
    if ports:
        return ports[0].device
    return None


def open_serial(port, baudrate=500000, timeout=1):
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)


def get_next_filename(prefix="Datos", ext=".txt", limit=100):
    """Return the next available filename DatosXX.txt (00-99)."""
    for i in range(limit):
        name = f"{prefix}{i:02d}{ext}"
        if not os.path.exists(name):
            return name
    return None


def main():
    ser = None
    buffer = []

    while True:
        if ser is None or not ser.is_open:
            port = find_arduino_port()
            if port:
                try:
                    ser = open_serial(port)
                    print(f"Connected to {port}")
                except serial.SerialException as e:
                    print(f"Failed to connect to {port}: {e}")
                    ser = None
                    time.sleep(1)
                    continue
            else:
                time.sleep(1)
                continue

        try:
            line = ser.readline()
            if not line:
                continue
            decoded = line.decode("utf-8", errors="replace").rstrip()
            print(decoded)
            buffer.append(decoded)
        except (serial.SerialException, OSError):
            print("Connection lost. Saving data and reconnecting...")
            if buffer:
                filename = get_next_filename()
                if filename is None:
                    print("Reached Datos99.txt. Exiting.")
                    return
                print(f"Saving data to {filename}")
                with open(filename, "w") as f:
                    for entry in buffer:
                        f.write(entry + "\n")
                buffer.clear()
            if ser:
                try:
                    ser.close()
                except Exception:
                    pass
            ser = None
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping by user request.")
            if buffer:
                filename = get_next_filename()
                if filename is not None:
                    print(f"Saving data to {filename}")
                    with open(filename, "w") as f:
                        for entry in buffer:
                            f.write(entry + "\n")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
