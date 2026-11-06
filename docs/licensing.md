# Licensing

## Project license

Copyright (C) 2026 unkindypie, for original Maya contributions.

Original Maya code and configuration may be redistributed and modified under
GNU GPL version 3 or, at your option, any later version
(`GPL-3.0-or-later`). The complete license is in [LICENSE](../LICENSE).
It is provided without warranty, including warranties of merchantability or
fitness for a particular purpose.

This default does not replace third-party copyright or license notices.
Upstream authors retain copyright in their work. In particular, a later-version
grant for our contributions does not extend to upstream GPLv3-only material.

## Why GPL rather than MIT?

The repository contains adapted KooL Hyprland configs, its Lua keybinding helper,
Waybar reference files, and a Rofi theme derived from KooL Style 4 / adi1090x.
KooL files carry `GPL-3.0-or-later` headers. Both
[Fedora-Hyprland](https://github.com/LinuxBeginnings/Fedora-Hyprland/blob/main/LICENSE.md)
and [Hyprland-Dots](https://github.com/LinuxBeginnings/Hyprland-Dots/blob/main/LICENSE.md)
include GPLv3. The [adi1090x Rofi license](https://github.com/adi1090x/rofi/blob/master/LICENSE)
is GPLv3; we do not assume an additional later-version grant for its layout.

GPL-covered adaptations cannot simply be redistributed as MIT-only.
Independent original files could be licensed under MIT separately, but that would
not change the licenses of the copied material. A GPL default keeps our code's
licensing consistent with its sources. Merely running GPL software does not
require using GPL for every configuration: the copied and adapted content is the
reason here. See [GPLv3 section 5](https://www.gnu.org/licenses/gpl-3.0.html#section5)
and the [GNU compatibility FAQ](https://www.gnu.org/licenses/gpl-faq.html#WhatDoesCompatMean).

## Third-party material

- KooL-derived configs and helpers, plus `reference/waybar-kool/`: retain their
  GPL notices. Maya modifications include personal hotkeys, startup/workspace
  rules, appearance and Lua integration; development dates are recorded in Git.
- `home/.config/rofi/themes/maya-paper.rasi`: GPLv3-derived layout; preserve its
  KooL and adi1090x credits.
- `scripts/rofi_extensions.py` builds rofi-calc (MIT) and rofi-universal (MIT)
  from pinned upstream revisions; compiled plugins, the rofi-universal launcher
  and the qalc binary are user-local build artifacts, not repository assets.
  See ATTRIBUTION.md.
- `home/.config/kitty/kitty-themes/`: retain the included
  [MIT license](../home/.config/kitty/kitty-themes/LICENSE.md) and author notices.
- Bundled Fantasque Sans Mono and JetBrains Mono fonts: retain each family's
  `OFL.txt` (SIL Open Font License 1.1).
- Notebook and Lined Paper textures and their adaptations: retain
  [CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0/) and attribution.
  They are separate assets, not relicensed as GPL. See
  [ATTRIBUTION.md](../ATTRIBUTION.md) for authors, sources and modifications.
- The Sobole Zsh theme retains its WTFPL notice; other third-party themes retain
  their upstream notices. Dependencies downloaded by the installer keep their
  upstream licenses and pinned revisions in `dependencies.json`.
- system24 and midnight-discord theme artifacts in `assets/themes/` remain MIT,
  with refact0r’s full copyright/license notices included in their folders and
  in the assembled local themes. Maya’s integration does not relicense them as GPL.
- Screenshots illustrate the desktop; third-party content depicted in them is
  not granted a new software license by this repository's default notice.

Keep the applicable license texts and attribution when redistributing these
materials. This records the sources checked for this repository, rather than
claiming that every bundled asset has a single license.

[Back to README](../README.md)
