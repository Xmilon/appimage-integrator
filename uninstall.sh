#!/usr/bin/env bash
# Removes appimage-integrator itself. Apps you installed with it stay installed;
# remove them first with `appimage-integrator remove <name>` if you want them gone.
set -euo pipefail

rm -f "$HOME/.local/bin/appimage-integrator"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/nautilus-python/extensions/appimage_integrator.py"
pgrep -x nautilus >/dev/null && nautilus -q || true
printf '\e[32m ✓\e[0m appimage-integrator removed.\n'
