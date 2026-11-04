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
    ~/.config/hypr/UserConfigs/kitty.conf. KooL updates also add a Catppuccin
    include there, which overrides Maya's paper palette (especially the tab bar
    and borders). Replace that file with a small include of the real config.
    """
    kool = home / '.config/hypr/UserConfigs/kitty.conf'
    maya = home / '.config/kitty/kitty.conf'
    if not maya.is_file() or not (kool.exists() or kool.is_symlink()):
        return False
    try:
        current = kool.read_text()
    except OSError:
        return False
    if current == KITTY_STUB:
        return False
    save_existing(kool, home, backup)
    if kool.is_symlink():
        kool.unlink()
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
