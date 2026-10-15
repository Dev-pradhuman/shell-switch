#!/usr/bin/env bash
# ==============================================================================
# 44 Dots Rice Adapter
# Clean Arch Linux & Hyprland setup with Waybar, SwayNC & Rofi
# https://github.com/44kash/dotfiles
# ==============================================================================

NAME="44 Dots"
DESCRIPTION="sr-44 Arch/Hyprland rice with Waybar, SwayNC & Rofi"
ICON="view-app-grid"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/repo/hypr"
    ["waybar"]="$PROFILE_DIR/repo/waybar"
    ["swaync"]="$PROFILE_DIR/repo/swaync"
    ["rofi"]="$PROFILE_DIR/repo/rofi"
)

start_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x dms 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x hyprpaper 2>/dev/null || true

    sleep 0.3
    if command -v waybar >/dev/null 2>&1; then
        setsid waybar >/dev/null 2>&1 &
    fi
    if command -v swaync >/dev/null 2>&1; then
        setsid swaync >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
}
