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


def main():
    ser = None
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
        except (serial.SerialException, OSError):
            print("Connection lost. Reconnecting...")
            if ser:
                try:
                    ser.close()
                except Exception:
                    pass
            ser = None
            time.sleep(1)
        except KeyboardInterrupt:
            print("Stopping by user request.")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
