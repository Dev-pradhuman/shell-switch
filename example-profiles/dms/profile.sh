#!/usr/bin/env bash
# ==============================================================================
# DankMaterialShell (DMS) Rice Adapter
# Material 3 Quickshell desktop shell with dynamic theming & dock
# https://github.com/AvengeMedia/DankMaterialShell
# ==============================================================================

NAME="DankMaterialShell"
DESCRIPTION="Material 3 Quickshell desktop shell with dynamic theming & dock"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["quickshell"]="$PROFILE_DIR/repo/quickshell"
    ["dms"]="$PROFILE_DIR/repo/quickshell"
)

start_shell() {
    systemctl --user stop swaync.service 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x dms 2>/dev/null || true

    sleep 0.3
    if command -v dms >/dev/null 2>&1; then
        setsid dms run -c "$PROFILE_DIR/repo/quickshell" -d >/dev/null 2>&1 &
    elif command -v qs >/dev/null 2>&1; then
        setsid qs -p "$PROFILE_DIR/repo/quickshell" >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -x dms 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
}
