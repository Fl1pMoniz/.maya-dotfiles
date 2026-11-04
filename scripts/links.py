"""Shared, non-destructive file-link installation and repair."""
from pathlib import Path
from datetime import datetime
import os, shutil, tempfile


def backup_root(home):
    return home / '.local/state/maya-dotfiles/backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')


def save_existing(dst, home, backup):
    saved = backup / dst.relative_to(home)
    saved.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_dir() and not dst.is_symlink():
        shutil.move(str(dst), str(saved))
    elif dst.is_symlink():
        saved.symlink_to(os.readlink(dst))
    else:
        shutil.copy2(dst, saved)
        if dst.name == '.zshrc':
            saved.chmod(0o600)


def ensure_link(src, dst, home, backup):
    if dst.is_symlink() and dst.resolve() == src.resolve():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        save_existing(dst, home, backup)
    # Atomic replacement prevents readers seeing a partially installed file.
    with tempfile.TemporaryDirectory(prefix='.maya-link-', dir=dst.parent) as tmp:
        link = Path(tmp) / 'link'
        link.symlink_to(src.resolve())
        os.replace(link, dst)
    return True


def ensure_managed(root, home, backup, aliases):
    """Replace every Maya-managed path with its repo link, backing up old files.

    This is intentionally content-agnostic: a KooL file, a distro default, a
    vendor-generated file or a user's hand-written config is all replaced by the
    Maya version at the same path. Correct links are left untouched.
    """
    waybar_changed = False
    for src in (root / 'home').rglob('*'):
        if not src.is_file():
            continue
        rel = str(src.relative_to(root / 'home'))
        if rel in aliases:
            continue
        changed = ensure_link(src, home / rel, home, backup)
        waybar_changed |= changed and rel.startswith('.config/waybar/')
    for src in (root / 'color-palette').iterdir():
        if not src.is_file():
            continue
        if '.config/maya-theme/' + src.name in aliases:
            continue
        ensure_link(src, home / '.config/maya-theme' / src.name, home, backup)
    return waybar_changed


def ensure_alias(src, dst, home, backup):
    """Link to a path without resolving its mode-selection symlink."""
    src = Path(src).absolute()
    if dst.is_symlink() and os.readlink(dst) == str(src):
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        save_existing(dst, home, backup)
    with tempfile.TemporaryDirectory(prefix='.maya-link-', dir=dst.parent) as tmp:
        link = Path(tmp) / 'link'
        link.symlink_to(src)
        os.replace(link, dst)
    return True
