#!/usr/bin/env bash
# ==============================================================================
# end4-pC Rice Adapter
# Material 3 Expressive desktop fork with Quickshell, presets & dynamic theming
# https://github.com/pctrade/end4-pC
# ==============================================================================

NAME="end4-pC"
DESCRIPTION="Material 3 Expressive desktop with Quickshell & community presets gallery"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["quickshell"]="$PROFILE_DIR/repo"
)

start_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x dms 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -f "qs -c ii" 2>/dev/null || true
    pkill -x qs 2>/dev/null || true

    # Ensure Quickshell can resolve both -c end4-pC and default path
    if [[ -d "$PROFILE_DIR/repo" && ! -e "$PROFILE_DIR/repo/end4-pC" ]]; then
        ln -sfn . "$PROFILE_DIR/repo/end4-pC" 2>/dev/null || true
    fi

    sleep 0.3
    if command -v qs >/dev/null 2>&1; then
        setsid qs -c end4-pC >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -f "qs -c end4-pC" 2>/dev/null || true
    pkill -x qs 2>/dev/null || true
}
