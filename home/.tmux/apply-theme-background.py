#!/usr/bin/env python3
"""Apply shared Maya palette colors to the same rounded layout in both modes."""
import subprocess
import json
from pathlib import Path

profile = json.loads((Path.home() / ".config/maya-theme/palette.json").read_text())
colors = profile["colors"]


def get(name):
    return subprocess.check_output(["tmux", "show-option", "-gqv", name], text=True).rstrip("\n")

background = colors["novel_selection"]
subprocess.run(["tmux", "set-option", "-g", "status-bg", background], check=True)
for option in ("status-left", "status-right", "window-status-format", "window-status-current-format"):
    value = get(option).replace("bg=#1e1e2e", "bg=" + background)
    # The active tab starts with an empty rounded edge in the bar color.
    value = value.replace("fg=#1e1e2e,bg=" + background,
                          "fg=" + background + ",bg=" + background)
    if option in ("status-left", "status-right"):
        # Warm paper segments, taupe icons, peach while prefix is held.
        value = value.replace("#313244", colors["tmux_fill"])
        value = value.replace("#cdd6f4", colors["novel_ink"])
        value = value.replace("#1e1e2e", colors["novel_ink"])
        value = value.replace("#a6e3a1", colors["tmux_accent"])
        value = value.replace("#f38ba8", colors["tmux_prefix"])
        value = value.replace("#cba6f7", colors["tmux_accent"])
    if option == "window-status-format":
        # Muted paper labels and taupe numbers, with Novel brown text.
        fill = colors["tmux_fill"]
        text = colors["novel_ink"]
        accent = colors["tmux_accent"]
        value = (
            f"#[fg={fill},bg={background},nobold,nounderscore,noitalics]"
            f"#[fg={text},bg={fill}]#W "
            f"#[fg={text},bg={accent},nobold,nounderscore,noitalics] #I"
            f"#[fg={accent},bg={background}] "
        )
    if option == "window-status-current-format":
        # Use palette-selected foreground and number colors for the active tab.
        # Avoid Kitty applying default-background transparency to the label.
        fill = colors["tmux_active_fill"]
        text = colors[profile["tmux_active"]["text"]]
        accent = colors[profile["tmux_active"]["number"]]
        value = (
            f"#[fg={fill},bg={background},nobold,nounderscore,noitalics]"
            f"#[fg={text},bg={fill}]#W#{{?window_zoomed_flag,(),}} "
            f"#[fg={text},bg={accent},nobold,nounderscore,noitalics] #I"
            f"#[fg={accent},bg={background}] "
        )
    subprocess.run(["tmux", "set-option", "-g", option, value], check=True)

# Keep the rounded bar compact, preserving the plugin's shared status structure.
base_format = get('@maya_original_status_format')
if not base_format:
    base_format = get('status-format[0]')
    subprocess.run(['tmux', 'set-option', '-g', '@maya_original_status_format', base_format], check=True)
outer = colors['tmux_outer']
for option, edge in [('status-left', ''), ('status-right', '')]:
    value = get(option)
    cap = f'#[fg={background},bg={outer}]{edge}#[bg={background}]'
    value = cap + value if option == 'status-left' else value + cap
    subprocess.run(['tmux', 'set-option', '-g', option, value], check=True)
subprocess.run(['tmux', 'set-option', '-g', 'status', 'on'], check=True)
subprocess.run(['tmux', 'set-option', '-g', 'status-format[0]', base_format], check=True)

# Catppuccin loads after the theme file, so reset the base styles it sets.
# Without this, status-style keeps Catppuccin's #11111B/#CDD6F4 bar.
for option, value in {
    'status-style': f"fg={colors['novel_ink']},bg={background}",
    'status-left-style': 'default',
    'status-right-style': 'default',
    'window-status-style': 'default',
    'window-status-current-style': 'default',
}.items():
    subprocess.run(['tmux', 'set-option', '-g', option, value], check=True)

# Remaining plugin color roles follow the selected palette, without layout changes.
for option, value in {
    'pane-border-style': f"fg={colors['tmux_aux_surface']}",
    'pane-active-border-style': f"fg={colors['tmux_aux_blue']}",
    'mode-style': f"fg={colors['tmux_aux_pink']},bg={colors['tmux_aux_overlay']},bold",
    'message-style': f"fg={colors['tmux_aux_cyan']},bg={colors['tmux_aux_surface']},align=centre",
    'message-command-style': f"fg={colors['tmux_aux_cyan']},bg={colors['tmux_aux_surface']}",
}.items():
    subprocess.run(['tmux', 'set-option', '-g', option, value], check=True)
