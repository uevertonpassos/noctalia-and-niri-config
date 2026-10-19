#!/usr/bin/python3
"""Open Alacritty in a selected/hovered Nautilus folder, or at home."""
import argparse
import fcntl
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

HELPERS = runpy.run_path(str(Path.home() / ".local/bin/codex-mouse-launcher.py"))
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
ACK = RUNTIME / "terminal-context-nautilus-ack"


def launch(directory):
    if not directory.is_dir():
        raise ValueError("A pasta não está acessível.")
    subprocess.Popen(["/usr/bin/alacritty", "--working-directory", str(directory)],
                     start_new_session=True, stdin=subprocess.DEVNULL,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def selection_count(window):
    """Return None when accessibility cannot identify the active file view."""
    try:
        import gi
        gi.require_version("Atspi", "2.0")
        from gi.repository import Atspi
        Atspi.set_timeout(300, 300)
        desktop = Atspi.get_desktop(0)
        for i in range(desktop.get_child_count()):
            app = desktop.get_child_at_index(i)
            if app.get_name() != "org.gnome.Nautilus":
                continue
            frames = [app.get_child_at_index(j) for j in range(app.get_child_count())]
            active = [f for f in frames if f.get_state_set().contains(Atspi.StateType.ACTIVE)]
            if not active:
                active = [f for f in frames if f.get_name() == window.get("title")]
            if len(active) != 1:
                return None
            pending = [active[0]]
            visited = 0
            while pending and visited < 1000:
                obj = pending.pop()
                visited += 1
                if not obj.get_state_set().contains(Atspi.StateType.SHOWING):
                    continue
                if obj.get_role() in (Atspi.Role.TABLE, Atspi.Role.TREE_TABLE):
                    selection = obj.get_selection_iface()
                    if selection is not None:
                        return selection.get_n_selected_children()
                pending.extend(obj.get_child_at_index(j) for j in range(obj.get_child_count()))
    except Exception:
        return None
    return None


def wait_modifiers_released():
    from evdev import InputDevice, ecodes as e, list_devices
    modifiers = {e.KEY_LEFTMETA, e.KEY_RIGHTMETA, e.KEY_LEFTCTRL,
                 e.KEY_RIGHTCTRL, e.KEY_LEFTALT, e.KEY_RIGHTALT,
                 e.KEY_LEFTSHIFT, e.KEY_RIGHTSHIFT}
    devices = []
    try:
        for path in list_devices():
            try:
                device = InputDevice(path)
                if modifiers.intersection(device.capabilities().get(e.EV_KEY, [])):
                    devices.append(device)
                else:
                    device.close()
            except OSError:
                pass
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            held = False
            for device in devices:
                try:
                    held |= bool(modifiers.intersection(device.active_keys()))
                except OSError:
                    pass
            if not held:
                return
            time.sleep(0.025)
        raise ValueError("Solte as teclas após pressionar Super + T e tente novamente.")
    finally:
        for device in devices:
            device.close()


def ensure_focus(window):
    if HELPERS["focused_window"]().get("id") != window["id"]:
        raise ValueError("A janela mudou. Use Super + T novamente com a pasta em foco.")


def tap(keyboard, code):
    from evdev import ecodes as e
    keyboard.write(e.EV_KEY, code, 1)
    keyboard.syn()
    keyboard.write(e.EV_KEY, code, 0)
    keyboard.syn()


def trigger_nautilus(window):
    from evdev import UInput, ecodes as e
    wait_modifiers_released()
    ensure_focus(window)
    count = selection_count(window)
    previous = ACK.read_text() if ACK.exists() else ""
    with UInput({e.EV_KEY: [e.KEY_F19, e.KEY_LEFTSHIFT, e.KEY_ESC]},
                name="Terminal Nautilus shortcut") as keyboard:
        time.sleep(0.2)
        ensure_focus(window)
        if count == 0:
            # Right-click selects an item under the pointer without opening it,
            # including when Nautilus is configured for single-click activation.
            with UInput({e.EV_KEY: [e.BTN_LEFT, e.BTN_RIGHT],
                         e.EV_REL: [e.REL_X, e.REL_Y]},
                        name="Terminal Nautilus folder selector") as mouse:
                time.sleep(0.2)
                ensure_focus(window)
                tap(mouse, e.BTN_RIGHT)
                time.sleep(0.2)
                tap(keyboard, e.KEY_ESC)
                time.sleep(0.1)
        ensure_focus(window)
        keyboard.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
        keyboard.syn()
        try:
            tap(keyboard, e.KEY_F19)
        finally:
            keyboard.write(e.EV_KEY, e.KEY_LEFTSHIFT, 0)
            keyboard.syn()
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if ACK.exists() and ACK.read_text() != previous:
                return
            time.sleep(0.05)
    raise ValueError("O Arquivos não respondeu ao atalho. Feche menus ou diálogos e tente novamente.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nautilus", action="store_true")
    args = parser.parse_args()
    try:
        if args.nautilus:
            ACK.write_text(str(time.monotonic_ns()))
            launch(HELPERS["nautilus_directory"](os.environ))
            return
        with (RUNTIME / "terminal-context-launch.lock").open("w") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            window = HELPERS["focused_window"]()
            if window.get("app_id") == "org.gnome.Nautilus":
                trigger_nautilus(window)
            else:
                launch(Path.home())
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        message = str(error).replace("Codex", "terminal")
        subprocess.run(["notify-send", "Terminal", message], check=False)
        print(message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
