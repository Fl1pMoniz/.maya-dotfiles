#!/usr/bin/env python3
"""Exercise installation and restoration in an empty home, plus config syntax."""
from pathlib import Path
import os, subprocess, tempfile, json, shutil
source_root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='maya-dotfiles-test-') as d:
    root = Path(d) / 'checkout'
    shutil.copytree(source_root, root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
    target = Path(d) / 'user'
    target.mkdir()
    env = dict(os.environ, HOME=str(target))
    def run(*args):
        if len(args) > 1 and args[1] == str(root / 'install.py'):
            args = (*args, '--skip-dependencies', '--no-theme-apply')
        subprocess.run(args, env=env, check=True, stdout=subprocess.DEVNULL)
    (target / '.zshrc').write_text('export EXAMPLE_API_TOKEN="test-only-credential"\n')
    run('python3', str(root / 'install.py'), '--no-services', '--without-mvim')
    # Validate the standalone Lua entry point without relying on installed KooL.
    if shutil.which('Hyprland'):
        validation_env = dict(env, XDG_CONFIG_HOME=str(target / '.config'))
        validation = subprocess.run(
            ['Hyprland', '--verify-config', '-c', str(target / '.config/hypr/hyprland.lua')],
            env=validation_env, text=True, capture_output=True)
        assert validation.returncode == 0 and 'config ok' in validation.stdout, validation.stdout + validation.stderr
    assert (target / '.config/hypr/hyprland.lua').is_symlink()
    secret = target / '.config/zsh/secrets.zsh'
    assert 'test-only-credential' in secret.read_text()
    assert secret.stat().st_mode & 0o777 == 0o600
    assert 'test-only-credential' not in (target / '.zshrc').read_text()
    for name in ['.config/kitty/kitty.conf', '.config/waybar/config', '.config/mvim/init.lua', '.tmux.conf']:
        assert (target / name).is_symlink()
        assert (target / name).resolve() == root / 'home' / name
        assert (target / name).read_bytes() == (root / 'home' / name).read_bytes()
    import sys
    sys.path.insert(0, str(root / 'scripts'))
    from themes import ALIASES
    from services import archive_conflicts
    units = target / '.config/systemd/user'
    (units / 'waybar.service.d').mkdir(parents=True)
    (units / 'waybar.service.d/override.conf').write_text(
        '[Service]\nExecStart=/usr/bin/waybar -c %h/.config/hypr/waybar/config\n')
    (units / 'waybar-watchdog.service').write_text('[Service]\nExecStart=/bin/true\n')
    wants = units / 'graphical-session.target.wants'
    wants.mkdir()
    (wants / 'waybar-watchdog.service').symlink_to(units / 'waybar-watchdog.service')
    service_backup = target / '.local/state/service-backup'
    conflicts = archive_conflicts(target, service_backup, units)
    assert conflicts
    assert not (units / 'waybar.service.d').exists()
    assert (service_backup / '.config/systemd/user/waybar.service.d/override.conf').is_file()
    assert not (units / 'waybar-watchdog.service').exists()
    assert not (wants / 'waybar-watchdog.service').exists()
    assert (service_backup / '.config/systemd/user/graphical-session.target.wants/waybar-watchdog.service').is_symlink()
    # A drop-in that does not replace ExecStart is harmless and must survive.
    (units / 'waybar.service.d').mkdir()
    (units / 'waybar.service.d/env.conf').write_text('[Service]\nEnvironment=MAYA_TEST=1\n')
    assert archive_conflicts(target, service_backup, units) == []
    assert (units / 'waybar.service.d/env.conf').is_file()
    from kool import KITTY_STUB
    kool_kitty = target / '.config/hypr/UserConfigs/kitty.conf'
    kool_kitty.write_text(
        'include ~/.config/hypr/UserConfigs/kitty-themes/Catppuccin-Mocha.conf\n')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert kool_kitty.read_text() == KITTY_STUB
    assert (target / '.config/kitty/kitty.conf').is_symlink()
    for src in (root / 'color-palette').iterdir():
        installed = target / '.config/maya-theme' / src.name
        assert installed.is_symlink()
        if '.config/maya-theme/' + src.name not in ALIASES:
            assert installed.resolve() == src
    palette_link = target / '.config/maya-theme/palette.json'
    palette_link.unlink()
    palette_link.write_text('{}')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert palette_link.resolve() == root / 'color-palette/profiles/light/palette.json'
    entry = target / '.config/hypr/hyprland.lua'
    entry.unlink()
    entry.write_text('-- vendor replacement')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert entry.resolve() == root / 'home/.config/hypr/hyprland.lua'
    # Simulate KooL replacing a managed entry point with a symlink.
    config = target / '.config/waybar/config'
    config.unlink()
    vendor = target / 'vendor-config'; vendor.write_text('{}')
    config.symlink_to(vendor)
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert config.is_symlink()
    assert config.resolve() == root / "home/.config/waybar/config"
    assert config.read_bytes() == (root / 'home/.config/waybar/config').read_bytes()
    assert vendor.read_text() == '{}'
    # Editing an installed config must change the checkout, not get copied back.
    style = target / '.config/waybar/style.css'
    style.write_text(style.read_text() + '\n/* live edit */\n')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert '/* live edit */' in (root / 'home/.config/waybar/style.css').read_text()
    # Whole-directory replacements are also repaired without writing vendor files.
    bar = target / '.config/waybar'
    bar.rename(target / 'old-waybar')
    bar.mkdir()
    (bar / 'config').write_text('{}')
    run('python3', str(root / 'scripts/restore-managed.py'))
    assert (bar / 'config').resolve() == root / 'home/.config/waybar/config'
    assert not (target / '.zshrc').is_symlink()
    assert (target / '.config/zsh/shared.zsh').is_symlink()
    run('python3', str(root / 'install.py'), '--no-services')
    # Reuse a fake existing checkout: optional path must invoke it once, then
    # restore the personal override without recursive dotfiles installation.
    editor = target / 'maya-nvim'
    (editor / '.git').mkdir(parents=True)
    installer = editor / 'install.sh'
    installer.write_text('#!/bin/sh\nprintf called >> "$HOME/editor-called"\nprintf upstream > "$HOME/.config/mvim/replacement"; mv "$HOME/.config/mvim/replacement" "$HOME/.config/mvim/init.lua"\n')
    installer.chmod(0o755)
    run('python3', str(root / 'install.py'), '--no-services', '--with-mvim')
    assert (target / 'editor-called').read_text() == 'called'
    assert (target / '.config/mvim/init.lua').read_bytes() == (root / 'home/.config/mvim/init.lua').read_bytes()
root = source_root
json.loads((root / 'home/.config/waybar/config').read_text())
for name in ['bootstrap-mvim.sh', 'home/.local/bin/maya-bar-action', 'home/.local/bin/maya-waybar', 'home/.local/bin/maya-git-status', 'home/scripts/tmux-sessionizer', 'home/scripts/tmux-sessionpicker']:
    subprocess.run(['bash', '-n', str(root / name)], check=True)
subprocess.run(['zsh', '-n', str(root / 'home/.config/zsh/shared.zsh')], check=True)
print('Fresh-home install, credential preservation, optional editor, recovery and syntax checks passed')
