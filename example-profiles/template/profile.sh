#!/usr/bin/env bash
# ==============================================================================
# Shell Profile Template
# ==============================================================================
NAME="My Custom Rice"
DESCRIPTION="Minimalist Hyprland setup with custom bar and notifications"
ICON="preferences-desktop-theme"

# Symlinks to create in ~/.config/ when this shell is activated
declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/hypr"
    ["waybar"]="$PROFILE_DIR/waybar"
    ["swaync"]="$PROFILE_DIR/swaync"
)

# Lifecycle Hook: Called when activating this shell
start_shell() {
    # 1. Stop any previous bars/shells
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x qs 2>/dev/null || true

    sleep 0.3

    # 2. Launch your bar and services (use setsid to daemonize cleanly)
    setsid waybar >/dev/null 2>&1 &
    setsid swaync >/dev/null 2>&1 &
}

# Lifecycle Hook: Called when switching away to another shell
stop_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
}
