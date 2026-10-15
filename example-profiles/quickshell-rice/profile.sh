#!/usr/bin/env bash
NAME="Quickshell Rice"
DESCRIPTION="Modern desktop shell built with Quickshell (Qt6 QML)"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/hypr"
    ["quickshell"]="$PROFILE_DIR/quickshell"
)

start_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x qs 2>/dev/null || true

    sleep 0.3
    setsid qs >/dev/null 2>&1 &
}

stop_shell() {
    pkill -x qs 2>/dev/null || true
}
