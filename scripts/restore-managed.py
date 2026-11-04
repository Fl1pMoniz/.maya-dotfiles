#!/usr/bin/env python3
"""Restore replaced Kitty/Waybar links; never overwrite correctly linked edits."""
from pathlib import Path
import subprocess
from links import backup_root, ensure_link
from kool import repair_dropdown, repair_kitty_config
from themes import ALIASES, install_profiles
root = Path(__file__).resolve().parents[1]
home = Path.home()
backup = backup_root(home)
repair_dropdown(home, backup)
waybar_changed = False
managed = ['.config/hypr/scripts/DarkLight.sh', '.config/hypr/hyprland.lua', '.config/waybar/config', '.config/waybar/style.css', '.config/kitty/kitty.conf', '.config/hypr/maya-appearance.conf', '.config/rofi/config.rasi', '.config/hypr/hyprlock.conf', '.config/hypr/hypridle.conf', '.config/wofi/config', '.config/wofi/style.css', '.config/waybar/palette.css']
for name in managed:
    if name in ALIASES:
        continue
    changed = ensure_link(root / 'home' / name, home / name, home, backup)
    waybar_changed |= changed and name.startswith('.config/waybar/')
for folder in ['.local/share/kitty-personal', '.config/kitty/kitty-themes', '.config/hypr/UserConfigs', '.config/hypr/lua', '.config/rofi/themes', '.config/swaync']:
    for src in (root / 'home' / folder).rglob('*'):
        if src.is_file() and str(src.relative_to(root / "home")) not in ALIASES:
            ensure_link(src, home / src.relative_to(root / 'home'), home, backup)
for src in (root / 'color-palette').iterdir():
    if src.is_file() and ".config/maya-theme/" + src.name not in ALIASES:
        ensure_link(src, home / '.config/maya-theme' / src.name, home, backup)
waybar_changed |= install_profiles(root, home, backup)
repair_kitty_config(home, backup)
if waybar_changed:
    subprocess.run(['systemctl', '--user', '--no-block', 'try-restart',
                    'maya-waybar.service'], stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL, check=False)
