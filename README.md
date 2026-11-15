# AppImage Integrator

Install AppImages like real apps on Linux: right-click one in **Files** and pick
**AppImage → Install to App Launcher**. It shows up in your launcher with its real
name and icon, and you can uninstall it just as easily.

Built for [Omarchy](https://omarchy.org) / Hyprland with GNOME Files (Nautilus),
and it works on any desktop that uses `.desktop` launcher entries.

## What it does

- **Right-click menu in Files**: an `AppImage` submenu on every `.AppImage` file
  - **Run**: start it without installing
  - **Install to App Launcher**: move it to `~/Applications` and add a launcher entry
  - **Install a Copy (keep this file)**: same, but leaves the original where it is
  - **Reinstall / Refresh Icon**: re-read the name and icon (e.g. after an update)
  - **Uninstall *App***: remove the launcher entry and send the AppImage to the trash, after a confirm dialog
  - **Make Executable**: shown only when the file can't run yet
- **Real metadata**: the name, description, categories, keywords, file types and
  launch arguments come from the `.desktop` file inside the AppImage. The icon is
  the largest one it ships (SVG preferred).
- **Updates**: installing a newer version of an app replaces the old one instead of
  adding a second launcher entry.
- **Uninstall from the launcher**: every app gets an *Uninstall* action, so you can
  remove it from the launcher's right-click or actions menu.
- **Notifications**: progress and results appear as desktop notifications with the
  app's icon.
- **Safe**: nothing needs root. Uninstalling moves files to the trash, and launcher
  entries it didn't create are never touched.

## Install

```bash
git clone https://github.com/Xmilon/appimage-integrator.git
cd appimage-integrator
./install.sh
```

The installer puts the `appimage-integrator` command in `~/.local/bin` and the Files
extension in `~/.local/share/nautilus-python/extensions`, then restarts Files.
On Arch it also installs any missing packages it uses: `nautilus-python`
(the Files menu), `libnotify` (notifications), `zenity` (the confirm dialog) and
`fuse2` (needed to run most AppImages).

To remove the tool again, run `./uninstall.sh`. Apps you already installed stay
installed.

## Command line

```bash
appimage-integrator install ~/Downloads/SomeApp-1.2.3-x86_64.AppImage
appimage-integrator install --copy SomeApp.AppImage   # keep the original file
appimage-integrator list
appimage-integrator info SomeApp.AppImage
appimage-integrator remove SomeApp                    # by name or by file
appimage-integrator remove --keep-file SomeApp        # don't trash the AppImage
appimage-integrator run SomeApp.AppImage -- --some-flag
```

| Option        | Meaning                                                |
| ------------- | ------------------------------------------------------ |
| `--copy`      | copy the AppImage instead of moving it                 |
| `--keep-file` | on remove, leave the AppImage file in place            |
| `--confirm`   | ask before removing (graphical dialog when available)  |
| `--notify`    | report progress with desktop notifications             |

Set `APPIMAGE_DIR` to keep AppImages somewhere other than `~/Applications`.

## Where things go

| What                | Where                                                     |
| ------------------- | --------------------------------------------------------- |
| AppImage files      | `~/Applications/`                                         |
| Launcher entries    | `~/.local/share/applications/appimage-<name>.desktop`     |
| Icons               | `~/.local/share/appimage-integrator/icons/`               |

Each launcher entry records its AppImage in `X-AppImage-Path`. That is how
`list`, `remove` and the Files menu know what's installed. There is no separate
database to get out of sync.

## Troubleshooting

- **The menu doesn't appear**: make sure `nautilus-python` is installed, then run
  `nautilus -q` and open Files again.
- **The app won't start**: install `fuse2` (`sudo pacman -S fuse2`). Some Electron
  apps also need `--no-sandbox`. Add it after `%U` on the `Exec=` line of the
  app's entry in `~/.local/share/applications/`.
- **Generic icon**: the AppImage doesn't ship one. *Reinstall / Refresh Icon* will
  pick it up if a later version does.

## License

MIT
