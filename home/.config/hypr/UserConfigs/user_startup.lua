-- Startup runs only at login, never on config reload.
hl.on("hyprland.start", function()
  local base = (os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/"
  local function script(relative, args)
    local path = base .. relative
    local f = io.open(path, "r")
    if f then f:close(); hl.exec_cmd(string.format("%q", path) .. (args or "")) end
  end
  hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP QT_STYLE_OVERRIDE QT_QPA_PLATFORMTHEME")
  hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY XDG_CURRENT_DESKTOP QT_STYLE_OVERRIDE QT_QPA_PLATFORMTHEME")
  script("initial-boot.sh")
  script("scripts/WallpaperDaemon.sh")
  script("scripts/Polkit.sh")
  script("scripts/PortalHyprland.sh")
  script("scripts/Hyprsunset.sh", " init")
  script("scripts/Dropterminal.sh", " --startup kitty")
  script("scripts/KeybindsLayoutInit.sh")
  -- One service owns Waybar, including KooL refreshes through its alias.
  hl.exec_cmd('systemctl --user start maya-waybar.service || "$HOME/.local/bin/maya-waybar"')
  for _, command in ipairs({"nm-applet", "swaync", "hypridle", "blueman-applet",
                             "wl-paste --type text --watch cliphist store",
                             "wl-paste --type image --watch cliphist store"}) do
    hl.exec_cmd(command)
  end
  local overview = io.open(base .. "scripts/OverviewToggle.sh", "r")
  if overview then overview:close(); hl.exec_cmd("qs -c overview") end
  hl.exec_cmd("vesktop")
  hl.exec_cmd("Telegram")
  hl.exec_cmd("zen-browser", { workspace = "1 silent" })
  hl.exec_cmd("kitty", { workspace = "2 silent" })
end)
