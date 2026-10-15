#!/usr/bin/env bash
# ==============================================================================
# HyDE Project Rice Adapter
# Modular desktop with Waybar, Rofi & dynamic themes
# https://github.com/HyDE-Project/HyDE
# ==============================================================================

NAME="HyDE Rice"
DESCRIPTION="HyDE Project modular desktop with Waybar, Rofi & dynamic themes"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/repo/Configs/.config/hypr"
    ["waybar"]="$PROFILE_DIR/repo/Configs/.config/waybar"
    ["rofi"]="$PROFILE_DIR/repo/Configs/.config/rofi"
    ["swaync"]="$PROFILE_DIR/repo/Configs/.config/swaync"
    ["dunst"]="$PROFILE_DIR/repo/Configs/.config/dunst"
)

start_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x dms 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true

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
