import time
from inputs import devices, get_gamepad

# Известные джойстики: имя -> объект Device
known = {}


def scan_devices():
    """Проверяем devices.gamepads и фиксируем изменения."""
    global known
    current = {}
    for d in devices.gamepads:
        # d.name — имя устройства
        # Не все устройства могут иметь "уникальный" идентификатор в inputs
        # Но можно использовать d.path или d.device_path, если доступно
        # В inputs.Device есть атрибут .path
        key = getattr(d, "path", None) or d.name
        current[key] = d

    added = [current[k] for k in current if k not in known]
    removed = [known[k] for k in known if k not in current]

    known = current
    return added, removed


def print_devices():
    print("\n=== Подключенные джойстики ===")
    if not known:
        print("  (нет)")
    else:
        for k, d in known.items():
            print(f"  {k} — Device object: {d}")
    print("===============================\n")


print("Запуск. Подключи/отключи геймпады.")

# Первый скан
added, removed = scan_devices()
print_devices()

while True:
    added, removed = scan_devices()

    for d in added:
        key = getattr(d, "path", None) or d.name
        print(f"[ПОДКЛЮЧЕН] {d.name} (key={key})")

    for d in removed:
        key = getattr(d, "path", None) or d.name
        print(f"[ОТКЛЮЧЕН] {d.name} (key={key})")

    if added or removed:
        print_devices()

    # Обработка событий геймпада
    try:
        events = get_gamepad()
    except Exception as e:
        # Если что-то пошло не так, просто подождать и продолжить
        time.sleep(0.01)
        continue

    for e in events:
        # У каждого события есть поле device — ссылка на Device
        dev = e.device
        identifier = getattr(dev, "path", None) or dev.name
        print(f"Событие от {identifier}: code={e.code}, state={e.state}, type={e.ev_type}")

    time.sleep(0.01)
