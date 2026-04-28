# Todoist Taskbar Badge Updater

[![AUR version](https://img.shields.io/aur/version/todoist-taskbar-badge-updater-git?style=flat-square&logo=arch-linux)](https://aur.archlinux.org/packages/todoist-taskbar-badge-updater-git)

![Todoist Taskbar Badge Updater](screenshot.png)

This project updates the count badge on the Todoist desktop application via D-Bus, displaying the number of tasks scheduled for today or overdue. It is designed for Linux desktop environments that support Unity LauncherEntry signals.

## Features
- Fetches tasks from the Todoist API
- Counts tasks due today or overdue
- Updates the badge on the Todoist desktop launcher using D-Bus
- Configurable update interval
- Supports environment variables for API token and desktop ID
- Systemd service integration for background operation

## Requirements
- Python 3
- `requests` library
- `dbus` library

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Run Manually

```bash
export TODOIST_API_TOKEN="<your_token>"
export TODOIST_DESKTOP_ID="application://todoist.desktop"  # Optional
python3 todoist-taskbar-badge-updater.py --interval 300
```

#### Options
- `--token` Todoist API token (or use `TODOIST_API_TOKEN` env var)
- `--desktop-id` D-Bus desktop ID for the Todoist app (default: `application://todoist.desktop`)
- `--interval` Update interval in seconds (default: 300)
- `--verbose` Enable debug logging

### Systemd service (Arch package)

When installed from the provided local `PKGBUILD`, the package places a user unit at
`/usr/lib/systemd/user/todoist-taskbar-badge-updater.service`. The packaged unit intentionally contains no
`Environment=` lines so secrets are not embedded.

Build & install (local PKGBUILD):

```bash
cd packages/arch
makepkg -si
```

Persistent environment (recommended)

Create a configuration file to store the API token persistently. The systemd unit
will load this file automatically when the service starts:

```bash
# create the file ~/.config/todoist-taskbar-badge-updater.conf
cat > ~/.config/todoist-taskbar-badge-updater.conf << 'EOF'
TODOIST_API_TOKEN=your_token_here
TODOIST_DESKTOP_ID=application://todoist.desktop
EOF
```

Ensure the file is only readable by your user:

```bash
chmod 600 ~/.config/todoist-taskbar-badge-updater.conf
```

Start the service:

```bash
systemctl --user daemon-reload   # pick up newly-installed unit files
systemctl --user start todoist-taskbar-badge-updater.service
# (optional) enable to start at login - package does NOT enable automatically
systemctl --user enable todoist-taskbar-badge-updater.service
journalctl --user -u todoist-taskbar-badge-updater.service -f
```

## Logging
- Set `LOG_LEVEL` environment variable to control log verbosity (e.g., `DEBUG`, `INFO`)

## License
MIT
