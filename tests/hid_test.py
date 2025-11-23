import hid
import struct


def list_controllers():
    devices = []
    for d in hid.enumerate():
        # Фильтруем только геймпады
        usage = d.get("usage")
        usage_page = d.get("usage_page")

        if usage_page == 1 and usage in (4, 5):  # Gamepad / Joystick
            devices.append(d)

    return devices


def open_controller(device_info):
    dev = hid.device(
        vid=device_info['vendor_id'],
        pid=device_info['product_id'],
        serial=device_info['serial_number']
    )
    print("Opened HID:", device_info['product_string'])
    print("Unique ID:", f"{device_info['vendor_id']:04x}:{device_info['product_id']:04x}:{device_info['serial_number']}")
    return dev


# Поиск и подключение
controllers = list_controllers()

if not controllers:
    raise SystemExit("Нет HID-геймпадов")

dev = open_controller(controllers[0])  # Берём первый

print("Listening... Press Ctrl+C to exit")

try:
    while True:
        data = dev.read(64)  # читаем 64 байта отчёта

        if not data:
            continue

        # ⚠ Это пример для Xbox/Generic gamepad:
        # Байты различаются по моделям!
        lx = data[1]    # левый стик X
        ly = data[2]    # левый стик Y
        buttons = data[5]  # битовая маска кнопок

        print(f"LX={lx}  LY={ly}  BTN_MASK={buttons:08b}")

except KeyboardInterrupt:
    dev.close()
    print("Closed")
