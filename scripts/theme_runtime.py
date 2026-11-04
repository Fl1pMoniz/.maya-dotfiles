"""Apply Maya toolkit palettes without wallpaper changes or application restarts."""
from pathlib import Path
import json
import os
import re
import shutil
import subprocess
import configparser
from themes import write_icon_index
from links import save_existing


def run(argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True, timeout=8)
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def patch_ini(path, section, values, home, backup):
    """Update selected keys only; preserve unrelated settings and original formatting."""
    original = path.read_text() if path.exists() else ''
    lines = original.splitlines(keepends=True)
    remaining = dict(values)
    output = []
    inside = False
    found = False
    for line in lines:
        if line.strip().startswith('['):
            if inside:
                output.extend(f'{key}={value}\n' for key, value in remaining.items())
                remaining.clear()
            inside = line.strip() == f'[{section}]'
            found |= inside
        if inside and '=' in line and not line.lstrip().startswith(('#', ';')):
            key = line.split('=', 1)[0].strip()
            if key in remaining:
                output.append(f'{key}={remaining.pop(key)}\n')
                continue
        output.append(line)
    if remaining:
        if output and not output[-1].endswith('\n'):
            output[-1] += '\n'
        if not found:
            output.append(f'\n[{section}]\n')
        output.extend(f'{key}={value}\n' for key, value in remaining.items())
    updated = ''.join(output)
    if updated == original:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        saved = backup / path.relative_to(home)
        saved.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, saved)
    # Write through an existing user-managed link, retaining its ownership model.
    path.write_text(updated)


def original_icons(home):
    """Remember the original icon theme, never a Maya overlay (no inherit cycles)."""
    state = home / '.local/state/maya-dotfiles/theme-icon-base.json'
    if state.is_file():
        return json.loads(state.read_text())['theme']
    candidates = []
    for filename, section, key in (
        ('.config/gtk-3.0/settings.ini', 'Settings', 'gtk-icon-theme-name'),
        ('.config/qt6ct/qt6ct.conf', 'Appearance', 'icon_theme'),
        ('.config/qt5ct/qt5ct.conf', 'Appearance', 'icon_theme'),
    ):
        parser = configparser.ConfigParser(interpolation=None, strict=False)
        parser.read(home / filename)
        candidates.append(parser.get(section, key, fallback=''))
    if shutil.which('gsettings'):
        try:
            result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', 'icon-theme'],
                                    capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                candidates.append(result.stdout.strip().strip("'"))
        except (OSError, subprocess.TimeoutExpired):
            pass
    fallback = next((value for value in candidates if value and not value.startswith('Maya-Paper-')
                     and not any(c in value for c in '\n\r,[]')), 'Adwaita')
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps({'theme': fallback}) + '\n')
    return fallback


def install_gtk4_import(home, backup):
    path = home / '.config/gtk-4.0/gtk.css'
    start, end = '/* BEGIN MAYA THEME */', '/* END MAYA THEME */'
    content = path.read_text() if path.exists() else ''
    # Imports precede existing rules; keep custom user rules and their precedence.
    block = start + '\n@import url("../maya-theme/current/gtk4.css");\n' + end + '\n'
    if start in content and end in content:
        updated = re.sub(re.escape(start) + r'.*?' + re.escape(end) + r'\n?',
                         lambda _: block, content, flags=re.S)
    else:
        updated = block + content
    if updated != content:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() or path.is_symlink():
            save_existing(path, home, backup)
            # A user's import may point into an installed third-party theme.
            # Materialize the amended stylesheet without editing that target.
            if path.is_symlink():
                path.unlink()
        path.write_text(updated)



def toolkits(home, selected, backup):
    dark = selected == 'dark'
    config = home / '.config'
    warnings = []
    gtk_name = 'Maya-Paper-' + selected.title()
    icon_name = gtk_name
    icon_fallback = original_icons(home)
    for variant in ('Light', 'Dark'):
        write_icon_index(home, 'Maya-Paper-' + variant, icon_fallback, backup)
    theme_roots = [home / '.themes', home / '.local/share/themes', Path('/usr/local/share/themes'), Path('/usr/share/themes')]
    gtk_exists = any((root / gtk_name).is_dir() for root in theme_roots)
    if gtk_exists:
        for version in ('gtk-3.0', 'gtk-4.0'):
            patch_ini(config / version / 'settings.ini', 'Settings',
                      {'gtk-theme-name': gtk_name, 'gtk-icon-theme-name': icon_name,
                       'gtk-application-prefer-dark-theme': '1' if dark else '0'}, home, backup)
        install_gtk4_import(home, backup)
    else:
        warnings.append(f'GTK theme {gtk_name} unavailable; existing GTK theme preserved')
    # Libadwaita and apps using the settings portal follow the system preference.
    if shutil.which('gsettings'):
        state = home / '.local/state/maya-dotfiles/theme-system-backup.json'
        if not state.exists():
            state.parent.mkdir(parents=True, exist_ok=True)
            saved = {}
            for key in ('gtk-theme', 'color-scheme', 'icon-theme'):
                try:
                    result = subprocess.run(['gsettings', 'get', 'org.gnome.desktop.interface', key], capture_output=True, text=True, timeout=3)
                    if result.returncode == 0:
                        saved[key] = result.stdout.strip()
                except (OSError, subprocess.TimeoutExpired):
                    pass
            state.write_text(json.dumps(saved, indent=2) + '\n')
        if gtk_exists:
            run(['gsettings', 'set', 'org.gnome.desktop.interface', 'gtk-theme', gtk_name])
            run(['gsettings', 'set', 'org.gnome.desktop.interface', 'icon-theme', icon_name])
        if not run(['gsettings', 'set', 'org.gnome.desktop.interface', 'color-scheme', 'prefer-dark' if dark else 'prefer-light']):
            warnings.append('Desktop color-scheme preference could not be updated')
    for version in ('qt5ct', 'qt6ct'):
        scheme = config / version / 'colors/Maya-Paper.conf'
        if scheme.is_file():
            patch_ini(config / version / (version + '.conf'), 'Appearance',
                      {'custom_palette': 'true', 'color_scheme_path': str(scheme),
                       'style': 'Fusion', 'icon_theme': icon_name}, home, backup)
        else:
            warnings.append(f'{version} Maya palette unavailable; existing palette preserved')
    return warnings


def signal_owned(name, sig):
    # Exact executable names, restricted to this user; never kill/restart apps.
    run(['pkill', '-' + sig, '-u', str(os.getuid()), '-x', name])


def refresh(home):
    if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
        run(['hyprctl', 'reload'])
    if shutil.which('dbus-update-activation-environment'):
        run(['dbus-update-activation-environment', '--systemd',
             'QT_STYLE_OVERRIDE=', 'QT_QPA_PLATFORMTHEME=qt5ct'])
    signal_owned('kitty', 'USR1')
    # SIGUSR2 is a config reload in the tested btop 1.4.7+; do not risk
    # terminating an older build that lacks that signal handler.
    try:
        version = subprocess.run(['btop', '--version'], capture_output=True, text=True, timeout=3)
        number = re.search(r'(\d+)\.(\d+)\.(\d+)', version.stdout)
        if number and tuple(map(int, number.groups())) >= (1, 4, 7):
            signal_owned('btop', 'USR2')
    except (OSError, subprocess.TimeoutExpired):
        pass
    run(['swaync-client', '-R'])
    run(['swaync-client', '-rs'])
    if shutil.which('tmux') and run(['tmux', 'has-session']):
        run(['tmux', 'source-file', str(home / '.tmux.conf')])
    if (home / '.local/bin/maya-lock').is_file():
        # This updates only the lockscreen cache, never the desktop image.
        run([str(home / '.local/bin/maya-lock'), '--prepare'])
    # Waybar's reload_style_on_change watches this file and re-reads palette.css.
    # Do not send SIGUSR2: Waybar 0.15 aborts in its Hyprland IPC destructor
    # when Client::reset() tears down module child processes.
    style = home / '.config/waybar/style.css'
    try:
        os.utime(style, None)
    except OSError:
        pass
