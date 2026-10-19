#!/usr/bin/env bash
# Persistent evdev/uinput access for the user running the desktop.
set -euo pipefail
if (( EUID == 0 )); then
  echo 'Execute este script como seu usuário normal; ele chama sudo quando necessário.' >&2
  exit 1
fi
repo_dir="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
desktop_user="$(id -un)"
getent group input >/dev/null || sudo groupadd --system input
sudo usermod -aG input "$desktop_user"
sudo install -D -m 644 "$repo_dir/system/70-hacker-neon-uinput.rules" /etc/udev/rules.d/70-hacker-neon-uinput.rules
sudo install -D -m 644 "$repo_dir/system/hacker-neon-uinput.conf" /etc/modules-load.d/hacker-neon-uinput.conf
sudo modprobe uinput
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=misc --sysname-match=uinput
echo 'Permissões de mouse/teclado configuradas. Entre novamente na sessão para ativar o grupo input.'
