-- Personal shortcuts; legacy .conf is retained only for rollback.
local h = require("lua.user_keybinds_helper")
h.unbind("SUPER", "S")
h.bind("SUPER", "S", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m region"), { description = "" })
-- Replace the KooL master-layout shortcut before assigning Chrome.
h.unbind("SUPER", "I")
h.bind("SUPER", "I", h.dispatch("exec", "google-chrome-stable"), { description = "Open Chrome" })
h.unbind("SUPER", "O")
h.bind("SUPER", "O", h.dispatch("exec", "thunar"), { description = "" })
h.unbind("SUPER SHIFT", "left")
h.unbind("SUPER SHIFT", "right")
h.unbind("SUPER SHIFT", "up")
h.unbind("SUPER SHIFT", "down")
h.unbind("SUPER CTRL", "left")
h.unbind("SUPER CTRL", "right")
h.unbind("SUPER CTRL", "up")
h.unbind("SUPER CTRL", "down")
h.bind("SUPER CTRL", "left", h.dispatch("resizeactive", "-50 0"), { description = "Resize left (-50)" })
h.bind("SUPER CTRL", "right", h.dispatch("resizeactive", "50 0"), { description = "Resize right (+50)" })
h.bind("SUPER CTRL", "up", h.dispatch("resizeactive", "0 -50"), { description = "Resize up (-50)" })
h.bind("SUPER CTRL", "down", h.dispatch("resizeactive", "0 50"), { description = "Resize down (+50)" })
h.bind("SUPER SHIFT", "left", h.dispatch("movewindow", "l"), { description = "Move window left" })
h.bind("SUPER SHIFT", "right", h.dispatch("movewindow", "r"), { description = "Move window right" })
h.bind("SUPER SHIFT", "up", h.dispatch("movewindow", "u"), { description = "Move window up" })
h.bind("SUPER SHIFT", "down", h.dispatch("movewindow", "d"), { description = "Move window down" })
h.bind("SUPER", "J", h.dispatch("layoutmsg", "togglesplit"), { description = "" })
h.unbind("SUPER", "F")
h.bind("SUPER", "F", h.dispatch("fullscreen", ""), { description = "Fullscreen" })
h.bind("SUPER", "V", h.dispatch("togglefloating", ""), { description = "Float current window" })
h.unbind("SUPER", "B")
h.bind("SUPER", "B", h.dispatch("exec", "$HOME/.local/bin/maya-lock"), { description = "Lock screen" })
h.unbind("SUPER", "D")
h.bind("SUPER", "D", h.dispatch("exec", "$HOME/.local/bin/maya-universal"), { description = "Universal search" })
h.unbind("SUPER", "SPACE")
h.bind("SUPER", "SPACE", h.dispatch("exec", "$HOME/.local/bin/maya-search"), { description = "Search, calculate and browse the web" })
h.unbind("ALT SHIFT", "S")
h.bind("ALT SHIFT", "S", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m region"), { description = "Capture and annotate" })
h.unbind("SUPER", "Print")
h.bind("SUPER", "Print", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m output -m active"), { description = "Capture and annotate" })
h.unbind("SUPER SHIFT", "Print")
h.bind("SUPER SHIFT", "Print", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m region"), { description = "Capture and annotate" })
h.unbind("SUPER CTRL", "Print")
h.bind("SUPER CTRL", "Print", h.dispatch("exec", "sleep 5 && $HOME/.local/bin/maya-screenshot -m output -m active"), { description = "Capture and annotate" })
h.unbind("SUPER CTRL SHIFT", "Print")
h.bind("SUPER CTRL SHIFT", "Print", h.dispatch("exec", "sleep 10 && $HOME/.local/bin/maya-screenshot -m output -m active"), { description = "Capture and annotate" })
h.unbind("ALT", "Print")
h.bind("ALT", "Print", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m window -m active"), { description = "Capture and annotate" })
h.unbind("SUPER SHIFT", "S")
h.bind("SUPER SHIFT", "S", h.dispatch("exec", "$HOME/.local/bin/maya-screenshot -m region"), { description = "Capture and annotate" })

-- Global layout switching in either Alt+Shift press order.
-- Remove KooL's per-window handler and its malformed plain-modifier bindings.
for _, key in ipairs({"SHIFT_L", "ALT_L", "Shift_L", "Alt_L"}) do h.unbind("", key) end
h.unbind("ALT_L", "SHIFT_L")
h.unbind("SHIFT_L", "ALT_L")
h.unbind("ALT", "SHIFT_L")
h.unbind("SHIFT", "ALT_L")
for _, chord in ipairs({ {"ALT", "SHIFT_L"}, {"SHIFT", "ALT_L"} }) do
  h.bind(chord[1], chord[2], h.exec_cmd('$HOME/.local/bin/maya-keyboard-layout --next'),
         { locked = true, non_consuming = true, description = "Switch keyboard layout globally" })
end
-- Register workspace number keys and shifted symbols through KooL's helper.
for n = 1, 10 do
  local key = "code:" .. (n + 9)
  for _, mods in ipairs({"SUPER", "SUPER SHIFT", "SUPER CTRL"}) do h.unbind(mods, key) end
  h.bind("SUPER", key, hl.dsp.focus({ workspace = n }))
  h.bind("SUPER SHIFT", key, hl.dsp.window.move({ workspace = n }))
  h.bind("SUPER CTRL", key, hl.dsp.window.move({ workspace = n, follow = false }))
end

-- Emoji picker replaces the default split-ratio shortcut.
h.unbind("SUPER ALT", "E")
h.unbind("SUPER", "M")
h.bind("SUPER", "M", h.exec_cmd('$HOME/.config/hypr/scripts/RofiEmoji.sh'), { description = "Emoji picker" })
