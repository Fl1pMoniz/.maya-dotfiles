"""Small backed-up compatibility fixes; do not vendor KooL source trees."""
from links import save_existing

KITTY_STUB = (
    "# KooL launchers pass this path explicitly. Maya owns the real Kitty config.\n"
    "# Kept as a small include so KooL launches cannot fall back to Catppuccin.\n"
    "include ~/.config/kitty/kitty.conf\n"
)


def repair_kitty_config(home, backup):
    """Make KooL's explicit kitty --config path load the Maya Kitty config.

    KooL's LaunchTerminal.sh and Dropterminal.sh always pass
    ~/.config/hypr/UserConfigs/kitty.conf. Whatever currently occupies that path
    (a KooL Catppuccin config, a distro default or a hand-written file) is
    backed up and replaced with the Maya include. When a KooL launcher exists
    but the file does not, create the include so KooL cannot fall back to a
    different config.
    """
    kool = home / '.config/hypr/UserConfigs/kitty.conf'
    maya = home / '.config/kitty/kitty.conf'
    if not maya.is_file():
        return False
    launcher = home / '.config/hypr/scripts/LaunchTerminal.sh'
    dropdown = home / '.config/hypr/scripts/Dropterminal.sh'
    if not (kool.exists() or kool.is_symlink()):
        if not (launcher.exists() or dropdown.exists()):
            return False
        kool.parent.mkdir(parents=True, exist_ok=True)
        kool.write_text(KITTY_STUB)
        return True
    try:
        current = kool.read_text()
    except OSError:
        # A directory or unreadable file is still a conflicting config.
        current = None
    if current == KITTY_STUB:
        return False
    save_existing(kool, home, backup)
    if kool.is_symlink():
        kool.unlink()
    elif kool.is_dir():
        import shutil
        shutil.rmtree(kool)
    kool.write_text(KITTY_STUB)
    return True


def repair_dropdown(home, backup):
    script = home / '.config/hypr/scripts/Dropterminal.sh'
    if not script.is_file():
        return False
    original = script.read_text()
    # KooL's fallback takes ANY newly mapped window during concurrent startup.
    # Restrict its before/after comparison to the dropdown's dedicated class.
    updated = original.replace(
        "jq -r '.[].address'",
        "jq -r --arg CLASS \"$DROPDOWN_KITTY_CLASS\" "
        "'.[] | select(.class == $CLASS or .initialClass == $CLASS) | .address'",
    )
    if updated == original:
        return False
    save_existing(script, home, backup)
    script.write_text(updated)
    return True
