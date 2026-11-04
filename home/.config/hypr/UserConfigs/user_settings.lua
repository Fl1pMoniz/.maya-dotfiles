-- Personal keyboard, monitor and layout settings.
hl.env("LIBVA_DRIVER_NAME", "radeonsi")
-- Let qt5ct/qt6ct apply the generated Maya palette instead of KooL's Kvantum override.
hl.env("QT_STYLE_OVERRIDE", "")
-- qt6ct also advertises the qt5ct key, so both Qt versions can use this value.
hl.env("QT_QPA_PLATFORMTHEME", "qt5ct")
hl.config({
  input = { kb_layout = "pt", kb_options = "" },
  general = { gaps_in = 4, gaps_out = 6 },
  cursor = { no_hardware_cursors = 1 },
})
require((os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")) .. "/hypr/UserConfigs/monitors.lua")

