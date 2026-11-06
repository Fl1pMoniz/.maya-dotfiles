#!/usr/bin/env python3
"""Check Rofi search modes, pinned extension metadata and launcher syntax."""
from pathlib import Path
import json
import os
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
web = root / 'home/.config/rofi/scripts/maya-web-search.py'
wrapper = root / 'home/.local/bin/maya-search'
universal_wrapper = root / 'home/.local/bin/maya-universal'
manifest = json.loads((root / 'dependencies.json').read_text())
calc = manifest['rofi_extensions']['rofi-calc']
universal = manifest['rofi_extensions']['rofi-universal']
assert re.fullmatch(r'[0-9a-f]{40}', calc['commit'])
assert calc['plugin'] == 'libcalc.so'
assert re.fullmatch(r'[0-9a-f]{40}', universal['commit'])
assert universal['plugin'] == 'libuniversal.so'
assert universal['launcher'] == 'data/rofi-universal'

config = json.loads((root / 'home/.config/rofi/web-search.json').read_text())
assert config['search_engine'] == 'google'
assert config['browser'] == 'xdg-open'

theme = (root / 'home/.config/rofi/themes/maya-paper.rasi').read_text()
assert 'display-calc:' in theme and 'display-web:' in theme
assert 'display-universal:' in theme
for keyboard in ('home/.config/hypr/UserConfigs/user_keybinds.lua',
                 'home/.config/hypr/UserConfigs/UserKeybinds.conf'):
    text = (root / keyboard).read_text()
    assert 'maya-universal' in text
    assert 'maya-search' in text
subprocess.run(['bash', '-n', str(wrapper)], check=True)
assert 'ROFI_UNIVERSAL_EXTRA_MODI' in universal_wrapper.read_text()
subprocess.run(['bash', '-n', str(universal_wrapper)], check=True)
for source in (web, root / 'scripts/rofi_extensions.py'):
    compile(source.read_text(), str(source), 'exec')


def run(retv, *args, info=''):
    env = dict(os.environ, ROFI_RETV=str(retv), MAYA_WEB_DRY_RUN='1')
    if info:
        env['ROFI_INFO'] = info
    return subprocess.check_output(
        [sys.executable, str(web), *args], env=env, text=True)


assert 'Type a query and press Enter' in run(0)
assert run(2, 'hello world').strip() == 'https://www.google.com/search?q=hello+world'
assert run(2, '!w arch linux').strip() == (
    'https://en.wikipedia.org/w/index.php?search=arch+linux')
assert run(2, 'https://example.org/a').strip() == 'https://example.org/a'
assert run(1, 'ignored', info='url\x1fhttps://example.org').strip() == 'https://example.org'
print('Rofi calculator metadata, web search modes and launcher checks passed')
