#!/usr/bin/env bash
# Run on the reinstalled CachyOS system, before install.sh.
set -euo pipefail
if ! command -v pacman >/dev/null; then
  echo 'Este instalador de pacotes é para CachyOS/Arch. Consulte README.md.' >&2
  exit 1
fi
packages=(
  niri noctalia-qs alacritty btop zsh python python-evdev python-gobject at-spi2-core fzf eza
  adw-gtk-theme adwaita-icon-theme qt6ct fontconfig
  nautilus firefox wl-clipboard cliphist brightnessctl ddcutil
  imagemagick libnotify networkmanager bluez bluez-utils
  pipewire wireplumber pipewire-pulse xdg-desktop-portal-gtk
  xdg-desktop-portal-gnome xwayland-satellite
)
if [[ "${1:-}" == --print ]]; then
  printf '%s\n' "${packages[@]}"
  exit 0
fi
echo 'Pacotes necessários ao desktop (sudo pacman -Syu --needed):'
printf ' %s' "${packages[@]}"
printf '\n'
sudo pacman -Syu --needed "${packages[@]}"
repo_dir="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
bash "$repo_dir/scripts/setup-input.sh"
echo 'Pacotes instalados. Agora execute ./install.sh como seu usuário normal.'
