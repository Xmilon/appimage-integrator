"""AppImage Integrator: right-click menu for AppImages in GNOME Files (Nautilus).

Adds an "AppImage" submenu to .AppImage files with Install / Run / Update /
Uninstall / Show in launcher entries. The actual work is done by the
`appimage-integrator` command, so the menu stays fast and never blocks Files.
"""

import os
import shutil
from pathlib import Path

from gi import require_version

require_version("Nautilus", "4.1")

from gi.repository import GObject, Gio, Nautilus  # noqa: E402

APPIMAGE_MIME_TYPES = {
    "application/vnd.appimage",
    "application/x-iso9660-appimage",
    "application/x-appimage",
}
MARKER = "X-AppImage-Integrated-By=appimage-integrator"
DATA_HOME = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
DESKTOP_DIR = DATA_HOME / "applications"


def _cli():
    found = shutil.which("appimage-integrator")
    if found:
        return found
    fallback = Path.home() / ".local/bin/appimage-integrator"
    return str(fallback) if fallback.exists() else None


def _installed_paths():
    """Map of installed AppImage path -> app name, read from launcher entries."""
    installed = {}
    for entry in DESKTOP_DIR.glob("appimage-*.desktop"):
        try:
            text = entry.read_text(errors="replace")
        except OSError:
            continue
        if MARKER not in text:
            continue
        name = path = None
        for line in text.splitlines():
            if line.startswith("[") and line != "[Desktop Entry]":
                break
            if line.startswith("Name="):
                name = line[5:]
            elif line.startswith("X-AppImage-Path="):
                path = line[16:]
        if path:
            installed[path] = name or Path(path).stem
    return installed


class AppImageIntegratorMenu(GObject.GObject, Nautilus.MenuProvider):
    def _appimage_paths(self, files):
        paths = []
        for file in files:
            if file.is_directory():
                continue
            location = file.get_location()
            path = location.get_path() if location else None
            if not path:
                continue
            mime = file.get_mime_type() or ""
            if mime in APPIMAGE_MIME_TYPES or path.lower().endswith(".appimage"):
                paths.append(os.path.realpath(path))
        return paths

    def _spawn(self, argv):
        try:
            Gio.Subprocess.new(argv, Gio.SubprocessFlags.NONE)
        except Exception:  # never let a failed launch break the Files window
            pass

    def _item(self, key, label, icon, tip, callback, *data):
        item = Nautilus.MenuItem(
            name=f"AppImageIntegrator::{key}", label=label, tip=tip, icon=icon
        )
        item.connect("activate", lambda _item: callback(*data))
        return item

    # -- actions -----------------------------------------------------------

    def _install(self, paths, copy=False):
        argv = [_cli(), "install", "--notify"]
        if copy:
            argv.append("--copy")
        self._spawn(argv + paths)

    def _remove(self, paths):
        self._spawn([_cli(), "remove", "--notify", "--confirm", *paths])

    def _run(self, path):
        self._spawn([_cli(), "run", path])

    def _make_executable(self, paths):
        for path in paths:
            try:
                mode = os.stat(path).st_mode
                os.chmod(path, mode | 0o111)
            except OSError:
                pass

    # -- menu --------------------------------------------------------------

    def get_file_items(self, *args):
        files = args[0] if len(args) == 1 else args[1]
        if not _cli():
            return []
        paths = self._appimage_paths(files)
        if not paths:
            return []

        installed = _installed_paths()
        new = [p for p in paths if p not in installed]
        done = [p for p in paths if p in installed]
        single = len(paths) == 1

        top = Nautilus.MenuItem(
            name="AppImageIntegrator::menu",
            label="AppImage",
            tip="Install, run or remove this AppImage",
            icon="application-x-executable",
        )
        submenu = Nautilus.Menu()
        top.set_submenu(submenu)

        if single:
            submenu.append_item(
                self._item("run", "Run", "media-playback-start",
                           "Start the app without installing it", self._run, paths[0])
            )

        if new:
            label = "Install to App Launcher" if len(new) == 1 else f"Install {len(new)} AppImages"
            submenu.append_item(
                self._item("install", label, "system-software-install",
                           "Move to ~/Applications and add to the app launcher",
                           self._install, new)
            )
            if not any(p.startswith(str(Path.home() / "Applications") + os.sep) for p in new):
                submenu.append_item(
                    self._item("install-copy", "Install a Copy (keep this file)", "edit-copy",
                               "Copy to ~/Applications and add to the app launcher",
                               self._install, new, True)
                )

        if done:
            label = "Reinstall / Refresh Icon" if len(done) == 1 else f"Reinstall {len(done)} AppImages"
            submenu.append_item(
                self._item("reinstall", label, "view-refresh",
                           "Re-read the name and icon from the AppImage", self._install, done)
            )
            label = (f"Uninstall {installed[done[0]]}" if len(done) == 1
                     else f"Uninstall {len(done)} AppImages")
            submenu.append_item(
                self._item("remove", label, "edit-delete",
                           "Remove from the app launcher and move to the trash",
                           self._remove, done)
            )

        not_exec = [p for p in paths if not os.access(p, os.X_OK)]
        if not_exec:
            submenu.append_item(
                self._item("chmod", "Make Executable", "emblem-system",
                           "Allow this file to run as a program", self._make_executable, not_exec)
            )

        return [top]
