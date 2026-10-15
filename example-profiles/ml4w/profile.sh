#!/usr/bin/env bash
# ==============================================================================
# MyLinuxForWork (ML4W) Dotfiles Rice Adapter
# Modular Hyprland desktop with Waybar themes & Rofi
# https://github.com/mylinuxforwork/dotfiles
# ==============================================================================

NAME="ML4W Dotfiles"
DESCRIPTION="MyLinuxForWork modular Hyprland desktop with Waybar themes & Rofi"
ICON="preferences-desktop-theme"

declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/repo/dotfiles/.config/hypr"
    ["waybar"]="$PROFILE_DIR/repo/dotfiles/.config/waybar"
    ["rofi"]="$PROFILE_DIR/repo/dotfiles/.config/rofi"
    ["swaync"]="$PROFILE_DIR/repo/dotfiles/.config/swaync"
    ["ml4w"]="$PROFILE_DIR/repo/dotfiles/.config/ml4w"
    ["ml4w-dotfiles-settings"]="$PROFILE_DIR/repo/dotfiles/.config/ml4w-dotfiles-settings"
)

start_shell() {
    pkill -x qs 2>/dev/null || true
    pkill -f "qs -c caelestia" 2>/dev/null || true
    pkill -x dms 2>/dev/null || true
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true

    rm -f "$HOME/.config/ml4w/settings/waybar-disabled" 2>/dev/null || true

    sleep 0.3
    if command -v waybar >/dev/null 2>&1; then
        setsid waybar >/dev/null 2>&1 &
    fi
}

stop_shell() {
    pkill -x waybar 2>/dev/null || true
}
