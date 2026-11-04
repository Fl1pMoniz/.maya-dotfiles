#!/usr/bin/env python3
"""Replace any drifted Maya-managed config with its repo link, after backup."""
from pathlib import Path
import subprocess
from links import backup_root, ensure_managed
from kool import repair_dropdown, repair_kitty_config
from themes import ALIASES, install_profiles
root = Path(__file__).resolve().parents[1]
home = Path.home()
backup = backup_root(home)
repair_dropdown(home, backup)
waybar_changed = ensure_managed(root, home, backup, ALIASES)
waybar_changed |= install_profiles(root, home, backup)
repair_kitty_config(home, backup)
if waybar_changed:
    subprocess.run(['systemctl', '--user', '--no-block', 'try-restart',
                    'maya-waybar.service'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
