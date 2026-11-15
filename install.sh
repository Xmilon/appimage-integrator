#!/usr/bin/env bash
# Installs appimage-integrator for the current user (no sudo needed for the tool itself).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
EXT_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/nautilus-python/extensions"

say() { printf '\e[36m==>\e[0m %s\n' "$*"; }

# Optional dependencies: the Files menu needs nautilus-python, notifications need
# libnotify, and older (type 2) AppImages need fuse2 to run.
missing=()
command -v pacman >/dev/null && for pkg in nautilus-python libnotify fuse2 zenity; do
  pacman -Q "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
done
if ((${#missing[@]})); then
  say "Installing missing packages: ${missing[*]}"
  sudo pacman -S --needed --noconfirm "${missing[@]}"
fi

say "Installing the command to $BIN_DIR/appimage-integrator"
install -Dm755 "$REPO_DIR/bin/appimage-integrator" "$BIN_DIR/appimage-integrator"

say "Installing the Files right-click menu"
install -Dm644 "$REPO_DIR/nautilus/appimage_integrator.py" "$EXT_DIR/appimage_integrator.py"

if pgrep -x nautilus >/dev/null; then
  say "Restarting Files so the menu shows up"
  nautilus -q || true
fi

case ":$PATH:" in
  *":$BIN_DIR:"*) ;;
  *) printf '\e[33m !\e[0m %s is not on your PATH; add it to use the command directly.\n' "$BIN_DIR" ;;
esac

printf '\e[32m ✓\e[0m Done. Right-click any .AppImage in Files → AppImage, or run: appimage-integrator --help\n'
