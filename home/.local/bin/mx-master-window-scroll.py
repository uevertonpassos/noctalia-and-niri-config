#!/usr/bin/python3
"""Map the MX Master 3S thumb wheel and thumb-rest button to Niri keys."""
import logging
import signal
import sys
import time
from contextlib import ExitStack, closing

from evdev import InputDevice, UInput, ecodes as e, list_devices

MOUSE_NAME = "MX Master 3S window navigation"
KEYBOARD_NAME = "MX Master 3S navigation keys"
HORIZONTAL = {e.REL_HWHEEL, e.REL_HWHEEL_HI_RES}
COOLDOWN = 0.22


def find_mouse():
    for path in list_devices():
        device = None
        try:
            device = InputDevice(path)
            if (device.info.vendor == 0x046D
                    and device.name in {"Logitech MX Master 3S", "MX Master 3S"}
                    and e.REL_HWHEEL in device.capabilities().get(e.EV_REL, [])):
                return device
        except OSError:
            pass
        if device is not None:
            device.close()
    return None


def remap(device):
    with ExitStack() as stack:
        stack.enter_context(closing(device))
        capabilities = device.capabilities()
        capabilities.pop(e.EV_SYN, None)
        capabilities[e.EV_REL] = [
            code for code in capabilities[e.EV_REL] if code not in HORIZONTAL
        ]
        mouse = stack.enter_context(UInput(
            capabilities, name=MOUSE_NAME, vendor=device.info.vendor,
            product=device.info.product, version=device.info.version,
            bustype=device.info.bustype, phys="mx-master-window-scroll/mouse",
            input_props=device.input_props(),
        ))
        keyboard = stack.enter_context(UInput(
            {e.EV_KEY: [e.KEY_F18, e.KEY_F23, e.KEY_F24]}, name=KEYBOARD_NAME,
            phys="mx-master-window-scroll/keyboard",
        ))
        # Give the compositor time to discover the replacement devices.
        time.sleep(0.3)
        stack.enter_context(device.grab_context())
        logging.info("Connected: %s (%s)", device.name, device.path)
        last_action = float("-inf")
        for event in device.read_loop():
            if event.type == e.EV_SYN and event.code == e.SYN_DROPPED:
                # Recreate the devices to clear any stale pressed-button state.
                raise OSError("Input queue overflow; reconnecting")
            # This mouse's thumb-rest button reports BTN_FORWARD (277).
            # The separate back/forward buttons keep their native events.
            if event.type == e.EV_KEY and event.code == e.BTN_FORWARD:
                if event.value == 1:
                    keyboard.write(e.EV_KEY, e.KEY_F18, 1)
                    keyboard.syn()
                    keyboard.write(e.EV_KEY, e.KEY_F18, 0)
                    keyboard.syn()
                continue
            if event.type == e.EV_REL and event.code in HORIZONTAL:
                # The hardware emits both legacy and high-resolution events.
                # Use legacy ticks once, and suppress both horizontal streams.
                if event.code == e.REL_HWHEEL and event.value:
                    now = time.monotonic()
                    if now - last_action >= COOLDOWN:
                        key = e.KEY_F24 if event.value > 0 else e.KEY_F23
                        keyboard.write(e.EV_KEY, key, 1)
                        keyboard.syn()
                        keyboard.write(e.EV_KEY, key, 0)
                        keyboard.syn()
                        last_action = now
                continue
            mouse.write_event(event)


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    while True:
        device = find_mouse()
        if device is not None:
            try:
                remap(device)
            except OSError as error:
                logging.warning("Mouse unavailable: %s", error)
        time.sleep(2)


if __name__ == "__main__":
    main()
