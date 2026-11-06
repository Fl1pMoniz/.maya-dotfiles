# Asset and configuration sources

Third-party notices below take precedence over the project default license.
See [licensing details](docs/licensing.md) for scope and upstream references.

- Notebook: HQvectors; Lined Paper: Are Sundnes. Downloaded from
  https://www.transparenttextures.com/notebook.html and
  https://www.transparenttextures.com/lined-paper.html . Transparent Textures /
  Subtle Patterns assets are CC BY-SA 3.0:
  https://creativecommons.org/licenses/by-sa/3.0/ . Resized Lined Paper versions
  are distributed under the same license with attribution to Are Sundnes.
- notebook-strong.png is an AI-generated variant made using Notebook as a
  reference. Kept as an unused alternative, with source attribution as above.
- Kitty themes originally installed from https://github.com/dexpota/kitty-themes
  (MIT); theme-specific authors/comments retained. Novel is a port of the Mac
  Terminal theme. See home/.config/kitty/kitty-themes/LICENSE.md.
- reference/waybar-kool: LinuxBeginnings KooL Dots,
  https://github.com/LinuxBeginnings/Hyprland-Dots (GPL-3.0-or-later).
- Oh My Zsh, Zsh and tmux plugin sources are downloaded by the dependency
  installer with their upstream licenses. URLs and revisions are in
  dependencies.json. Some tmux bindings originated in KooL. Sobole custom theme:
  https://github.com/sobolevn/sobole-zsh-theme (WTFPL, retained in file header).
- Fonts: Fantasque Sans Mono and JetBrains Mono Nerd Font distributions;
  bundled original license files accompany the font families.

- Hyprland UserConfigs and the Lua keybinding helper retain LinuxBeginnings /
  KooL GPL-3.0-or-later headers, with personal settings and hotkey modifications.

- Maya Paper Rofi theme adapts LinuxBeginnings KooL Style 4, credited to
  https://github.com/adi1090x/rofi . Its upstream LICENSE grants GPL version 3;
  no later-version grant is assumed for that source. Original headers and layout
  credit retained. See https://github.com/adi1090x/rofi/blob/master/LICENSE .

- rofi-calc by svenstaro: https://github.com/svenstaro/rofi-calc at
  `42e67748c7a647526a5d35b0bdf7adcd1f9c3025`, MIT. The installer builds it from
  source with the revision in dependencies.json; its source tree is not stored
  in this repository. qalc comes from Qalculate!, GPL-2.0-or-later.
- Maya's Rofi web-search interaction follows pdonadeo/rofi-web-search
  (https://github.com/pdonadeo/rofi-web-search, MIT); the mode script is a
  local implementation for Maya's browser and engine configuration.
- rofi-universal by Fl1pMoniz: https://github.com/Fl1pMoniz/rofi-universal at
  `8ce807e1f56ee1004a361981a926d7173c55ab37`, MIT. The installer builds the
  plugin and launcher from the pinned revision; its source tree is not stored in
  this repository. Currency reference data is fetched from Frankfurter.

- Maya GTK overrides and pastel folder SVG artwork in `styles/` are original
  project assets under GPL-3.0-or-later. GTK uses its installed Adwaita foundation;
  its upstream source is not copied into this repository.

- system24 by refact0r: https://github.com/refact0r/system24 at
  `35a069674115e9676316e4c0ad6aad7089436be2`, MIT. Includes its built stylesheet
  and original Dark/Light option files in `assets/themes/system24/`.
- midnight-discord by refact0r (system24's foundation):
  https://github.com/refact0r/midnight-discord at
  `8598b2d540c51b5ab06364818b405bd5c66e2509`, MIT. Its built stylesheet is in
  `assets/themes/midnight-discord/`. Each folder retains upstream's full LICENSE.
  Maya combines these artifacts locally, removes remote theme imports, pins
  optional upstream asset URLs, and applies the chosen system24 color variables
  through a marked QuickCSS block. Optional Google web-font imports are retained.
