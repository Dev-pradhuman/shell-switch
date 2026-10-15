#!/usr/bin/env bash
# ==============================================================================
# Caelestia Shell Profile Adapter
# Dynamic color generation, drawers, quickshell widgets & animations
# https://github.com/caelestia-dots/caelestia
# ==============================================================================

NAME="Caelestia Shell"
DESCRIPTION="Quickshell desktop shell with dynamic colors, drawers & widgets"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/hypr"
    ["caelestia"]="$PROFILE_DIR/caelestia"
    ["quickshell"]="$PROFILE_DIR/quickshell"
)

start_shell() {
    # Stop conflicting desktop shells
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x dms 2>/dev/null || true

    sleep 0.4
    if command -v caelestia >/dev/null 2>&1; then
        setsid caelestia shell -d >/dev/null 2>&1 &
    elif command -v qs >/dev/null 2>&1; then
        setsid qs -c caelestia -n -d >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
}
