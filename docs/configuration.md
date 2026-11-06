# Edit your configs

Installed files are symlinks into `home/`: editing either location changes the
same file. Reload the application afterward. Run the installer to link new files.
Every managed path is forced to the Maya version: an existing KooL, distro,
vendor or custom file is backed up and replaced, not just a file that looks like
KooL's.

- **Kitty:** `~/.config/kitty/kitty.conf`; paper texture/tint in
  `~/.local/share/kitty-personal/notebook.conf`. The custom Novel theme and notebook
  texture are tracked in this repo. Its Light cream and Dark charcoal backgrounds are `novel_paper` in
  each profile in `color-palette/palette.json`; edit the palette and regenerate.
  KooL launchers pass `~/.config/hypr/UserConfigs/kitty.conf` explicitly, so that
  file is kept as an include of the real Maya config instead of a Catppuccin theme.
- **Wofi:** `~/.config/wofi/config`; edit the shared stylesheet in `styles/wofi.css`
  and regenerate both profiles with `python3 scripts/generate-palette.py`: paper panels, a pink search
  strip, beveled rows and crisp offset shadows. Preview with `wofi --show drun`.
  This is an optional alternative; Super+D uses the familiar Rofi launcher.
- **Rofi:** `~/.config/rofi/themes/maya-paper.rasi` keeps KooL Style 4’s layout
  with a slim classic-macOS-style frame, cat icon, right-hand rose dot,
  paper surfaces and dusty pink selections.
  **Super+D** runs `~/.local/bin/maya-universal`, a wrapper around
  `rofi-universal`. It keeps the regular tabs: **universal** (the default),
  apps, files, term, window, calc and web. The unified tab provides applications,
  files, native calculations, inline currency conversion, web search, dictionary,
  GitHub, weather and bookmarks in one field. Its calculator and percentages work
  offline; currency uses cached Frankfurter reference rates; neither needs qalc.
  Enter copies calculations and currency results. The wrapper adds the Maya web
  tab; calc appears when the pinned `rofi-calc` extension is installed. The
  launcher uses the Maya Rofi theme and optional
  `~/.config/rofi-universal/config.ini` settings.
  **Super+Space** runs `~/.local/bin/maya-search`, the separate apps/files/term/
  window launcher with qalc-backed **calc** and **web** tabs. Its web tab
  supports URLs, leading bangs (`!g`, `!ddg`, `!w`, `!yt`, `!gh`, `!aur`,
  `!maps`, `!define`) and suggestions when the query ends with `!`; edit
  `~/.config/rofi/web-search.json` to change its engine or browser.
  `maya-search calc` and `maya-search web` open dedicated windows.
  The installer builds the pinned rofi-universal and optional rofi-calc sources
  from `dependencies.json`; missing optional extension dependencies only produce
  warnings. Maya's launchers have no KooL or Wallust dependency; KooL’s separate
  menus keep their own themes.
- **Emoji picker (KooL):** **Super+M** opens the Rofi emoji picker.
- **Wallpaper (KooL):** press **Super+W** to open the wallpaper picker. It reads
  `~/Pictures/wallpapers/` (including subfolders), or `wallpapers/` inside your
  XDG Pictures directory if customized. Add images there to list them in the picker.
- **Lock/idle:** `~/.config/hypr/hyprlock.conf` and `hypridle.conf`. A layered 90s-style dialog,
  beveled pink title bar and blurred current wallpaper; **Super+B** or `~/.local/bin/maya-lock` locks.
  Wallpaper follows awww/swww, Waypaper, then KooL’s cache, with plain paper as
  fallback. Private wallpaper images stay outside Git. The idle warning remains
  at 9 minutes and locking at 10; display-off/suspend stay disabled. The included Lua startup
  config starts hypridle. Restart hypridle
  after changing idle settings. Weather has its own bottom-left card; battery and
  uptime share a bottom-right card. Both have pastel title strips and crisp offset shadows. The login dialog has
  a backing sheet, recessed clock display and soft pink password field. Long weather text wraps to fit. Weather
  refreshes in the background using KooL’s existing provider when present;
  otherwise wttr.in uses your approximate IP location. Cached weather stays
  available offline and is marked when stale. No location/cache data is committed.
- **SwayNC:** `~/.config/swaync/`: opaque paper cards, a cat title strip,
  rose controls and beveled borders. Reload with `swaync-client -R` and
  `swaync-client -rs`. Quick actions retain KooL integrations; locking uses Maya lock.
- **Waybar:** `~/.config/waybar/config` and `style.css`. When KooL’s layout scripts
  and their dependencies are installed, the layout icon beside `?` opens its
  Hyprland layout menu (Dwindle, Scrolling, Monocle, Master); right-click cycles layouts. The current keyboard
  layout with a flag (`🇺🇸 us` / `🇺🇦 ua`) appears just to the right of the date, updating directly
  from Hyprland’s layout-change events. Click the flag or press Alt+Shift to cycle layouts globally across all keyboards
  and windows; the indicator refreshes immediately
  after the switch takes effect. Per-window layout restoration is disabled.
  Non-country layouts show a globe. SwayNC suppresses KooL’s layout-change popups.
- **btop:** `~/.config/btop/btop.conf` selects the repo’s `maya-paper` theme.
  Ink and rose/sage/lavender graphs follow the shared Light/Dark palette.
  CPU/GPU information stays at the top, with memory, network and processes below.
  Terminal background is preserved; process-list fading is disabled for readability.
  Theme colors are generated from the `btop` mapping in `color-palette/palette.json`.
  The theme switch reloads btop 1.4.7+ live; reopen older versions after palette changes.
- **tmux:** `~/.tmux.conf`; colors follow `maya-theme` with the same rounded
  single-row bar in both modes. Ctrl-b r reloads config without changing the mode.
- **Zsh:** `~/.config/zsh/shared.zsh`. The local `~/.zshrc` loads this plus private
  `secrets.zsh` and machine-specific `local.zsh` in the same directory.
  Secrets stay outside Git with permissions 600. Recognized credential
  assignments are migrated during installation; move multiline secrets manually.
- **Maya Neovim:** `~/.config/mvim/init.lua` is a personal override, not a complete
  Neovim distribution. Its `theme_background` follows the global Light/Dark switch
  at startup and live, while the editor’s colorscheme stays separate. Install [Maya Neovim](https://github.com/unkindypie/maya-nvim/) to use it.
- **Screenshots:** Hyprshot captures into Swappy for highlighting and annotation.
  Super+S selects a region; existing Print shortcuts also open the editor.
  Nothing is saved automatically. In Swappy use Ctrl+C to copy, Ctrl+S to save,
  or Escape to discard. Requires `hyprshot` and `swappy`.
- **Hyprland:** `~/.config/hypr/hyprland.lua` is the active entry point.
  It loads installed KooL Lua modules when available, then our native Lua
  `UserConfigs/user_*.lua` overrides. Without KooL it provides basic terminal,
  close-window and workspace bindings before loading the personal settings.
  `user_startup.lua` launches Vesktop, Telegram, Chrome with its last session on
  workspace 1, and one Kitty on workspace 2. Startup runs only at login.
  Vesktop opens on workspace 3; later Kitty windows stay on the current workspace.
  Edit `user_keybinds.lua` for shortcuts, `user_window_rules.lua` for workspace
  assignments, `user_settings.lua` for input settings, and `monitors.lua` for displays.
  Personal settings retain this laptop’s monitor and keyboard choices.
  Some shortcuts require KooL scripts, Chrome, Thunar or hyprshot.
  Appearance is in `user_decorations.lua`, animation timing in `user_animations.lua`:
  uniform 3px pastel borders, fixed gradient directions, layered brown shadows,
  and no inactive dimming. Windows fade over 600 ms from 90% compositor opacity
  when unfocused to fully solid when focused. Kitty supplies an opaque background and Hyprland animates its opacity,
  so focus changes have no abrupt app-alpha switch. Unfocused windows retain
  background blur at size 8/3 passes.
  Reload with `hyprctl reload`. Shared colors come from the palette generator,
  independently of Wallust. See [Light/Dark theming](themes.md).

The old `.conf` Hyprland files remain as rollback references; the Lua entry point
never sources them. Hyprlock and Hypridle still use their own `.conf` formats.
Hyprland 0.56 supports switching an existing session with `hyprctl reload full-reset`
after installing the Lua entry point. Normal edits only need `hyprctl reload`.
For rollback, remove the installed `hyprland.lua` symlink and run
`hyprctl reload full-reset` to use the preserved `hyprland.conf` again. Disable
`maya-dotfiles.path` first so link recovery does not restore the Lua entry point.
Back up custom configs before installation; the installer also backs up files it replaces.

[Back to README](../README.md)
