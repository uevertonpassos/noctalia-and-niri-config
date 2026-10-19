#!/usr/bin/python3
"""Open Codex at home or in the exact selection supplied by Nautilus."""
import argparse
import fcntl
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import time
from urllib.parse import unquote, urlsplit

HOME = Path.home()
CODEX = HOME / ".local/bin/codex"
RUNTIME = Path(os.environ.get("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
ACK = RUNTIME / "codex-mouse-nautilus-ack"


def notify(message):
    subprocess.run(["notify-send", "Codex", message], check=False)
    print(message, file=sys.stderr)


def local_path(uri):
    parsed = urlsplit(uri)
    if parsed.scheme != "file" or parsed.netloc not in ("", "localhost"):
        raise ValueError("Abra uma pasta local para iniciar o Codex.")
    return Path(unquote(parsed.path))


def nautilus_directory(env):
    uris = env.get("NAUTILUS_SCRIPT_SELECTED_URIS", "").splitlines()
    selected = [local_path(uri) for uri in uris if uri]
    folders = [path for path in selected if path.is_dir()]
    if len(folders) > 1:
        raise ValueError("Selecione apenas uma pasta para abrir no Codex.")
    if folders:
        return folders[0]
    current = env.get("NAUTILUS_SCRIPT_CURRENT_URI", "")
    if current:
        folder = local_path(current)
        if folder.is_dir():
            return folder
    if selected and all(p.parent == selected[0].parent for p in selected):
        return selected[0].parent
    raise ValueError("Não foi possível identificar a pasta. Abra uma pasta local no Arquivos.")


def terminal_command(directory):
    directory = directory.absolute()
    if not directory.is_dir():
        raise ValueError("A pasta não existe mais ou não está acessível.")
    codex = str(CODEX) if os.access(CODEX, os.X_OK) else shutil.which("codex")
    if not codex:
        raise ValueError("Instale o Codex CLI e faça login antes de usar o botão do polegar.")
    return ["/usr/bin/alacritty", "--working-directory", str(directory),
            "--title", f"Codex · {directory.name}",
            "-e", codex, "--cd", str(directory)]


def launch(directory):
    subprocess.Popen(terminal_command(directory), start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)


def focused_window():
    result = subprocess.run(["niri", "msg", "-j", "focused-window"],
                            check=True, capture_output=True, text=True, timeout=2)
    return json.loads(result.stdout) or {}


def trigger_nautilus(window_id):
    from evdev import UInput, ecodes as e
    previous = ACK.read_text() if ACK.exists() else ""
    with UInput({e.EV_KEY: [e.KEY_F19]}, name="Codex Nautilus shortcut") as keyboard:
        time.sleep(0.3)
        if focused_window().get("id") != window_id:
            raise ValueError("A janela mudou. Clique novamente no botão com a pasta em foco.")
        keyboard.write(e.EV_KEY, e.KEY_F19, 1)
        keyboard.syn()
        keyboard.write(e.EV_KEY, e.KEY_F19, 0)
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
    parser.add_argument("--print-directory", action="store_true")
    args = parser.parse_args()
    try:
        if args.nautilus:
            if not args.print_directory:
                ACK.write_text(str(time.monotonic_ns()))
            directory = nautilus_directory(os.environ)
            if args.print_directory:
                print(directory)
            else:
                launch(directory)
            return
        with (RUNTIME / "codex-mouse-launch.lock").open("w") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return
            window = focused_window()
            if window.get("app_id") == "org.gnome.Nautilus":
                trigger_nautilus(window["id"])
            else:
                launch(HOME)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        notify(str(error))
        sys.exit(1)


if __name__ == "__main__":
    main()
