#!/usr/bin/env python3
"""Install into the current user's home; back up replaced files first."""
from pathlib import Path
from datetime import datetime
import argparse, shutil, subprocess, sys, re, os, runpy, tempfile
p = argparse.ArgumentParser()
p.add_argument('--skip-dependencies', action='store_true', help='Skip dependency downloads (offline config-only install)')
p.add_argument('--no-theme-apply', action='store_true', help='Link palettes without changing desktop preferences or reloading apps')
p.add_argument('--no-services', action='store_true', help='Install links without systemd services')
mvim = p.add_mutually_exclusive_group()
mvim.add_argument('--with-mvim', dest='with_mvim', action='store_true', help='Install Maya Neovim and its launcher')
mvim.add_argument('--without-mvim', dest='with_mvim', action='store_false', help='Skip the optional Maya Neovim installation')
p.set_defaults(with_mvim=None)
a = p.parse_args()
root = Path(__file__).resolve().parent
subprocess.run([sys.executable, str(root / "scripts/generate-palette.py")], check=True)
home = Path.home()
if not a.skip_dependencies:
    # Do this before copying custom themes, which also live under .oh-my-zsh.
    deps = runpy.run_path(str(root / 'scripts/install-dependencies.py'))
    deps['install_all'](root, home)
if a.with_mvim is None:
    a.with_mvim = (sys.stdin.isatty() and
                   input('Install Maya Neovim (maya-nvim) too? [y/N] ').strip().lower() in ('y', 'yes'))
if a.with_mvim:
    # Upstream installers may write in place. Detach our links first so they
    # cannot modify the committed personal overrides through a symlink.
    for name in ['init.lua', 'lazy-lock.json']:
        dst = home / '.config/mvim' / name
        if dst.is_symlink() and dst.resolve().is_relative_to(root / 'home'):
            with tempfile.TemporaryDirectory(dir=dst.parent) as tmp:
                copy = Path(tmp) / name
                shutil.copy2(dst, copy)
                os.replace(copy, dst)
    # Run before copying overrides so the saved personal config wins afterward.
    subprocess.run(['bash', str(root / 'bootstrap-mvim.sh'), '--from-installer'], check=True)
sys.path.insert(0, str(root / 'scripts'))
if not a.skip_dependencies:
    from rofi_extensions import install as install_rofi_extensions
    for warning in install_rofi_extensions(root, home):
        print(warning, file=sys.stderr)
from links import backup_root, ensure_link, ensure_managed, save_existing
from kool import repair_dropdown, repair_kitty_config
from services import archive_conflicts
from themes import ALIASES, install_profiles
backup = backup_root(home)
repair_dropdown(home, backup)


def write_unit(path, content):
    """Write a Maya-owned unit, preserving any pre-existing copy in the backup."""
    if path.is_file() and not path.is_symlink() and path.read_text() == content:
        return
    if path.exists() or path.is_symlink():
        save_existing(path, home, backup)
        if path.is_symlink():
            path.unlink()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
# Preserve single-line credential assignments before replacing a pre-existing zshrc.
# Never print their values or copy them into the repository.
zshrc = home / '.zshrc'
if zshrc.is_file():
    private = []
    for line in zshrc.read_text().splitlines():
        match = re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=', line)
        if match and re.search(r'(?i)(token|secret|password|passwd|api_?key|account_sid|credential)', match[1]):
            if line.rstrip().endswith('\\'):
                raise SystemExit('Move multiline credentials to ~/.config/zsh/secrets.zsh before installing.')
            private.append(line)
    if private:
        secrets = home / '.config/zsh/secrets.zsh'
        secrets.parent.mkdir(parents=True, exist_ok=True)
        current = secrets.read_text() if secrets.exists() else '# Machine-local credentials; never commit this file.\n'
        additions = [line for line in private if line not in current.splitlines()]
        fd = os.open(secrets, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(current.rstrip() + '\n' + ('\n'.join(additions) + '\n' if additions else ''))
        secrets.chmod(0o600)
# The only local entry point is .zshrc; common shell config is linked separately.
loader = (root / 'scripts/zshrc-loader.zsh').read_text()
if not zshrc.is_file() or zshrc.is_symlink() or zshrc.read_text() != loader:
    if zshrc.exists() or zshrc.is_symlink():
        save_existing(zshrc, home, backup)
        if zshrc.is_symlink():
            zshrc.unlink()
    zshrc.write_text(loader)
    zshrc.chmod(0o600)
ensure_managed(root, home, backup, ALIASES)
install_profiles(root, home, backup)
repair_kitty_config(home, backup)
subprocess.run([sys.executable, str(home / '.local/bin/maya-lock'), '--prepare'], check=True)
if shutil.which('fc-cache'): subprocess.run(['fc-cache', '-f'], check=True)
if not a.no_services:
    units = home / '.config/systemd/user'; units.mkdir(parents=True, exist_ok=True)
    restore = units / 'maya-dotfiles-restore.service'
    write_unit(restore, '[Unit]\nDescription=Restore Maya paper appearance after vendor updates\n[Service]\nType=oneshot\nExecStart=/usr/bin/python3 "' + str(root / 'scripts/restore-managed.py') + '"\n')
    write_unit(units / 'maya-dotfiles.path', """[Unit]
Description=Protect Maya Waybar and Kitty configuration
[Path]
PathChanged=%h/.config
PathChanged=%h/.config/waybar
PathChanged=%h/.config/waybar/config
PathChanged=%h/.config/waybar/style.css
PathChanged=%h/.config/maya-theme
PathChanged=%h/.config/kitty
PathChanged=%h/.config/kitty/kitty.conf
PathChanged=%h/.local/share/kitty-personal
PathChanged=%h/.config/hypr
PathChanged=%h/.config/hypr/UserConfigs
PathChanged=%h/.config/hypr/scripts
PathChanged=%h/.config/rofi
PathChanged=%h/.config/rofi/config.rasi
PathChanged=%h/.config/rofi/themes
PathChanged=%h/.config/swaync
PathChanged=%h/.config/swaync/config.json
PathChanged=%h/.config/swaync/style.css
PathChanged=%h/.config/wofi
PathChanged=%h/.config/wofi/config
PathChanged=%h/.config/wofi/style.css
Unit=maya-dotfiles-restore.service
[Install]
WantedBy=default.target
""")
    restore_script = root / 'scripts/restore-managed.py'
    write_unit(units / 'maya-waybar.service', f"""[Unit]
Description=Maya Paper Waybar
After=graphical-session-pre.target
[Service]
ExecStartPre=/usr/bin/python3 "{restore_script}"
ExecStart=%h/.local/bin/maya-waybar
Restart=always
RestartSec=3
[Install]
WantedBy=default.target
""")
    def ctl(*args, check=True): subprocess.run(['systemctl', '--user', *args], check=check)
    ctl('disable', '--now', 'kitty-notebook.path', check=False)
    ctl('disable', '--now', 'waybar-watchdog.service', check=False)
    for conflict in archive_conflicts(home, backup, units):
        print(f'Archived conflicting Waybar unit: {conflict}')
    ctl('disable', '--now', 'waybar.service', check=False)
    # KooL explicitly starts waybar.service even when it is disabled.
    ensure_link(units / 'maya-waybar.service', units / 'waybar.service', home, backup)
    ctl('daemon-reload')
    ctl('import-environment', 'WAYLAND_DISPLAY', 'XDG_CURRENT_DESKTOP', check=False)
    subprocess.run(['pkill', '-x', 'waybar'], check=False)
    ctl('enable', '--now', 'maya-dotfiles.path', 'maya-waybar.service')
    ctl('restart', 'maya-waybar.service')
if not a.no_theme_apply:
    subprocess.run([str(home / '.local/bin/maya-theme'), 'apply'], check=True)
print('Installed. Backups:', backup)
