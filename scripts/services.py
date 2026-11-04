"""Archive user units that would override the managed Maya Waybar."""
from pathlib import Path
import shutil

from links import save_existing


def _overrides_execstart(directory):
    """Return True when a drop-in directory contains an ExecStart override."""
    if not directory.is_dir():
        return False
    for conf in directory.glob('*.conf'):
        try:
            lines = conf.read_text().splitlines()
        except OSError:
            continue
        if any(line.lstrip().startswith('ExecStart') for line in lines):
            return True
    return False


def _archive(path, home, backup, archived):
    if not (path.exists() or path.is_symlink()):
        return
    save_existing(path, home, backup)
    if path.is_dir() and not path.is_symlink():
        # save_existing moves directories; remove anything it could not move.
        if path.exists():
            shutil.rmtree(path)
    elif path.exists() or path.is_symlink():
        path.unlink()
    archived.append(path)


def archive_conflicts(home, backup, units):
    """Move conflicting Waybar drop-ins/watchdogs into the install backup.

    waybar.service is installed as an alias of maya-waybar.service. Systemd also
    applies waybar.service.d drop-ins to the alias target, so a legacy ExecStart
    override silently launches KooL's bar from ~/.config/hypr/waybar instead of
    Maya's config from ~/.config/waybar. Separate watchdog units can also race
    the managed bar, so archive those too. Harmless drop-ins are preserved.
    """
    units = Path(units)
    if not units.is_dir():
        return []
    archived = []
    dropin = units / 'waybar.service.d'
    if (dropin.exists() or dropin.is_symlink()) and _overrides_execstart(dropin):
        _archive(dropin, home, backup, archived)
    name = 'waybar-watchdog.service'
    candidates = [units / name]
    candidates += list(units.glob(f'*.wants/{name}'))
    candidates += list(units.glob(f'*.requires/{name}'))
    for path in candidates:
        _archive(path, home, backup, archived)
    return archived
