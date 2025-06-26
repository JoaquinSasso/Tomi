import os
import time
import serial
import serial.tools.list_ports


def find_arduino_port():
    """Return the device name of the first likely Arduino port."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if (
            'Arduino' in port.description
            or 'ttyACM' in port.device
            or 'ttyUSB' in port.device
            or 'usbmodem' in port.device
        ):
            return port.device
    if ports:
        return ports[0].device
    return None


def get_next_filename(prefix='Datos', ext='.txt', limit=100):
    """Return the next available filename DatosXX.txt (00-99)."""
    for i in range(limit):
        filename = f"{prefix}{i:02d}{ext}"
        if not os.path.exists(filename):
            return filename
    return None


def open_serial(port, baudrate=9600, timeout=1):
    return serial.Serial(port, baudrate=baudrate, timeout=timeout)#hola


def main():
    filename = get_next_filename()
    if filename is None:
        print("Reached Datos99.txt. Exiting.")
        return
    print(f"Saving data to {filename}")

    ser = None
    ready = False

    with open(filename, 'w', buffering=1) as f:  # line-buffered
        while True:
            if ser is None or not ser.is_open:
                port = find_arduino_port()
                if port:
                    try:
                        ser = open_serial(port)
                        print(f"Connected to {port}")
                        ready = False
                    except serial.SerialException:
                        ser = None
                else:
                    ser = None
                if ser is None:
                    time.sleep(1)
                    continue

            try:
                line = ser.readline()
                if not line:
                    continue
                try:
                    decoded = line.decode('utf-8', errors='replace').strip()
                except Exception:
                    decoded = str(line)

                if not ready:
                    if decoded.upper() == 'READY':
                        ready = True
                        print('Arduino ready. Starting to record.')
                    continue

                f.write(decoded + "\n")
            except (serial.SerialException, OSError):
                print("Connection lost. Waiting for reconnection...")
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


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
