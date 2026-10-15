#!/usr/bin/env bash
# ==============================================================================
# end-4 Dots (illogical-impulse) Rice Adapter
# Material You desktop with Quickshell 'ii' suite & Fuzzel
# https://github.com/end-4/dots-hyprland
# ==============================================================================

NAME="end-4 Dots"
DESCRIPTION="end-4 Material You desktop with Quickshell 'ii' suite & Fuzzel"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/repo/dots/.config/hypr"
    ["quickshell"]="$PROFILE_DIR/repo/dots/.config/quickshell"
    ["fuzzel"]="$PROFILE_DIR/repo/dots/.config/fuzzel"
    ["matugen"]="$PROFILE_DIR/repo/dots/.config/matugen"
)

start_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x dms 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true

    sleep 0.3
    if command -v qs >/dev/null 2>&1; then
        setsid qs -c ii >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -f "qs -c ii" 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
}
