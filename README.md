# Todoist Count Badge

![Todoist Count Badge](screenshot.png)

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
python3 todoist-badge-updater.py --interval 300
```

#### Options
- `--token` Todoist API token (or use `TODOIST_API_TOKEN` env var)
- `--desktop-id` D-Bus desktop ID for the Todoist app (default: `application://todoist.desktop`)
- `--interval` Update interval in seconds (default: 300)
- `--verbose` Enable debug logging

### Systemd service (Arch package)

When installed from the provided local `PKGBUILD`, the package places a user unit at
`/usr/lib/systemd/user/todoist-badge-updater.service`. The packaged unit intentionally contains no
`Environment=` lines so secrets are not embedded.

Build & install (local PKGBUILD):

```bash
cd packages/arch
makepkg -si
```

Persistent environment (recommended, systemd v239+)

Create a systemd environment.d file so the user manager picks up the API token persistently
without embedding it into unit files. Example:

```bash
# create the file ~/.config/environment.d/todoist.conf
TODOIST_API_TOKEN=your_token_here
TODOIST_DESKTOP_ID=application://todoist.desktop  
```

Ensure the file is only readable by your user:

```bash
chmod 600 ~/.config/environment.d/todoist.conf
```

Reload the user manager so the environment is picked up (required so `systemctl --user start`
uses the new variables):

```bash
systemctl --user daemon-reexec
systemctl --user show-environment | grep -i todoist
```

Start the service after the environment is loaded:

```bash
systemctl --user daemon-reload   # pick up newly-installed unit files
systemctl --user start todoist-badge-updater.service
# (optional) enable to start at login - package does NOT enable automatically
systemctl --user enable todoist-badge-updater.service
journalctl --user -u todoist-badge-updater.service -f
```

## Logging
- Set `LOG_LEVEL` environment variable to control log verbosity (e.g., `DEBUG`, `INFO`)

## License
MIT
