# Maya dotfiles

**Neovim config: [Maya Neovim](https://github.com/unkindypie/maya-nvim/)**

Paper colors, pastels and soft pink highlights for Waybar, Kitty, btop, tmux and Zsh.
**Light** is the default; **Dark** uses warm charcoal and cream with the same styles.
Works with KooL Fedora Hyprland; the main desktop components also work without KooL.

![Maya desktop with the pastel Waybar and cream notebook Kitty terminals](assets/screenshots/maya-desktop.png)

## Install

Works well on top of [Fedora Hyprland](https://github.com/LinuxBeginnings/Fedora-Hyprland), but should work on other wayland installation:

```sh
cd ~/.maya-dotfiles
python3 install.py
```

The installer backs up replaced files and asks whether to install Maya Neovim.
Use `--with-mvim` or `--without-mvim` to choose explicitly. Maya Neovim has its
own dependency installer, which may ask for sudo or additional choices.

Missing Oh My Zsh and tmux plugins download at the revisions in dependencies.json.
Existing installations and local changes are preserved. A fresh install needs
internet; use `--skip-dependencies` for an offline install with dependencies ready. Add
`--no-theme-apply` to link profiles without changing toolkit preferences or
reloading running apps.

Install the following dependencies first. These are the versions installed on the
reference Fedora desktop on **2026-10-18**, not enforced minimum versions.

**Core tools and desktop:**

- Git **2.56.0**
- Python **3.14.8**
- Zsh **5.9**
- Kitty **0.47.1**
- tmux **3.7c**
- Waybar **0.15.0** (Fedora build `0.15.0^2.git1684389`)
- fzf **0.74.4**
- Hyprland **0.56.2** — the reference Wayland desktop for the included Lua config.
- Nerd Fonts — bundled Fantasque Sans Mono from Nerd Fonts **3.3.0** and
  JetBrains Mono from Nerd Fonts **3.4.0**; no separate font download needed.

**Launcher and bar controls:**

- Rofi **2.0.0**, with Wayland support (`rofi` on this Fedora setup;
  some distributions name the Wayland package `rofi-wayland`).
- brightnessctl **0.5.1**
- WirePlumber **0.5.18** (provides `wpctl`)
- pavucontrol **6.2**
- nm-connection-editor **1.36.0**
- playerctl **2.4.1**

**Screen locking:**

- hyprlock **0.9.6**
- hypridle **0.1.8**

**Optional integrations:**

- qt5ct **1.9** / qt6ct **0.11** — platform integration for Maya Qt app palettes
  (install the tool needed by your apps).
- SwayNC / SwayNotificationCenter **0.12.6** — notification center.
- lsd **1.2.0** — styled directory listings.
- fastfetch **2.68.1** — terminal system information.
- btop **1.4.7** — system monitor with the included high-contrast paper theme.
- hyprshot **1.3.0** and Swappy **1.5.1** — required for the screenshot and
  annotation shortcuts.

The installer’s Git-based dependencies are pinned separately by commit in
[`dependencies.json`](dependencies.json). Existing installations are preserved.

## Light and Dark

Click the `day`/`night` button in Waybar, or run:

```sh
maya-theme light
maya-theme dark
maya-theme toggle
maya-theme status
```

Your choice persists across login and reinstall. Theme changes preserve the wallpaper
and let mvim follow the selected Light/Dark variant while keeping its colorscheme
in its separate repository. Thunar and other GTK/Qt apps use generated Maya
paper/pastel themes and matching folder icons. The system color preference follows
the selection; some apps need reopening. Vencord/Vesktop system24 themes also
follow the selected mode through QuickCSS. See [theme details](docs/themes.md).

## Edit your configs

Installed configs are linked to `home/`, so edits stay in sync with this repo.
See the [configuration guide](docs/configuration.md) for file locations,
customization, shortcuts, and reload instructions.

## KooL integration and protection

Waybar optionally shows KooL's help, Hyprland layout, settings and blue-light filter buttons when
their scripts and applications exist. Otherwise they hide. The network button
opens NetworkManager's GUI. Original KooL Waybar files are archived in reference/.

`maya-waybar.service` runs the bar; `waybar.service` aliases it so KooL startup
and refresh use the same instance. Systemd also applies `waybar.service.d`
drop-ins to the aliased target, so the installer archives any legacy `ExecStart`
override and conflicting `waybar-watchdog.service` instead of silently launching
KooL's bar. The installer and link recovery also patch KooL’s dropdown discovery
to match only its dedicated terminal class, preventing it from hiding another app
during login. KooL's launchers pass `~/.config/hypr/UserConfigs/kitty.conf`
explicitly; that file is replaced with a small include of `~/.config/kitty/kitty.conf`
so KooL's Catppuccin include cannot override Maya's colors and notebook background.
Original scripts and configs are backed up; upstream source trees are not stored
here.

`maya-dotfiles.path` repairs replaced
Kitty, Waybar, Rofi, Wofi, SwayNC and Hyprland user-config symlinks. Vendor writes _through_ a symlink
also change the repo: inspect `git diff` after theme tools. Keep this repo in
place. Backups live in `~/.local/state/maya-dotfiles/backups/`.

```sh
# Disable the managed bar and link recovery:
systemctl --user disable --now maya-dotfiles.path maya-waybar.service
```

Without systemd, install with `--no-services` and start
`~/.local/bin/maya-waybar` from Hyprland. Automatic recovery requires systemd.
Disable other Waybar launchers if they create duplicate bars.

## Checks

```sh
python3 tests/check.py
python3 tests/check-dependencies.py
python3 tests/check-palette.py
python3 tests/check-themes.py
python3 tests/check-mvim-theme.py
python3 tests/check-vencord-theme.py
git diff --check
```

See ATTRIBUTION.md for asset sources and licenses.

## Shared colors

[`color-palette/palette.json`](color-palette/palette.json) defines named `light` and
`dark` profiles and shared app mappings. The current Light colors are retained.
Generated profiles share layouts and are selected through the local
`~/.config/maya-theme/current` link; switching does not rewrite tracked files.

```sh
python3 scripts/generate-palette.py
python3 scripts/generate-palette.py --check
python3 scripts/generate-palette.py --audit
```

The generator checks both profiles for invalid, duplicate and unreviewed similar
colors. App-specific near-color exceptions are documented per profile. It supplies
Waybar, Wofi, Rofi, SwayNC, Hyprlock, Hyprland, btop, Kitty, shell colors and tmux.
Shared Wofi and GTK styles and the original folder SVG live in `styles/`; the
generator supplies their profile colors. Qt palettes are generated by color role. Other component styles remain directly editable in `home/`.
After editing palette values, regenerate and run `maya-theme apply` to reload.
See the [theme guide](docs/themes.md) for toolkit integration and reload limits.

## License

Original Maya code and configuration are licensed under
[GPL-3.0-or-later](LICENSE). Third-party files and assets retain their own licenses;
see [licensing details](docs/licensing.md) and [attributions](ATTRIBUTION.md).
