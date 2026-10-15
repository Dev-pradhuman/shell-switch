#!/usr/bin/env bash
# ==============================================================================
# 43PR Rice Adapter
# 43PR Quickshell desktop setup with custom top bar, settings & hyprquickpaper
# ==============================================================================

NAME="43PR Rice"
DESCRIPTION="43PR Quickshell desktop setup with custom top bar, settings & hyprquickpaper"
ICON="preferences-desktop-wallpaper"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/repo/hypr"
    ["quickshell"]="$PROFILE_DIR/repo/quickshell"
    ["43pr"]="$PROFILE_DIR/repo/43pr"
)

start_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x dms 2>/dev/null || true

    sleep 0.5
    if command -v qs >/dev/null 2>&1; then
        setsid qs >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
}
