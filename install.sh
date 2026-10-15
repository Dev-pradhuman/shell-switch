#!/usr/bin/env bash
# ==============================================================================
# Desktop Shell Switcher Installer
# ==============================================================================

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[1;32m"
CYAN="\033[1;36m"
YELLOW="\033[1;33m"
RED="\033[1;31m"
RESET="\033[0m"

BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"
PROFILES_DIR="${HOME}/.config/desktop-shells"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "\n${BOLD}${CYAN}=== Installing Desktop Shell Switcher ===${RESET}\n"

# 1. Ensure target directories exist
mkdir -p "${BIN_DIR}" "${DESKTOP_DIR}" "${PROFILES_DIR}"

# 2. Check dependencies
echo -e "${BOLD}Checking dependencies...${RESET}"
MISSING_DEPS=()
for cmd in python3 git hyprctl; do
    if ! command -v "${cmd}" >/dev/null 2>&1; then
        MISSING_DEPS+=("${cmd}")
    fi
done

if [[ ${#MISSING_DEPS[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Notice: The following optional/required utilities were not found:${RESET}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "  - ${dep}"
    done
fi

# Check Python Libadwaita / GTK4
if ! python3 -c "import gi; gi.require_version('Gtk', '4.0'); gi.require_version('Adw', '1')" >/dev/null 2>&1; then
    echo -e "${YELLOW}Warning: PyGObject with Gtk4 and Libadwaita is required for the GUI application.${RESET}"
    echo "  On Arch Linux: sudo pacman -S python-gobject gtk4 libadwaita"
    echo "  On Fedora:     sudo dnf install python3-gobject gtk4 libadwaita"
    echo "  On Debian/Ubuntu: sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1"
fi

# 3. Copy binaries
echo -e "\n${BOLD}Installing CLI and GUI binaries to ${BIN_DIR}...${RESET}"
cp -f "${SCRIPT_DIR}/bin/shell-switch" "${BIN_DIR}/shell-switch"
cp -f "${SCRIPT_DIR}/bin/desktop-shell-app.py" "${BIN_DIR}/desktop-shell-app"
chmod +x "${BIN_DIR}/shell-switch" "${BIN_DIR}/desktop-shell-app"

# 4. Copy desktop entry
echo -e "${BOLD}Installing desktop entry to ${DESKTOP_DIR}...${RESET}"
cp -f "${SCRIPT_DIR}/desktop/desktop-shell-switcher.desktop" "${DESKTOP_DIR}/desktop-shell-switcher.desktop"
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

# 5. Populate example profiles if profiles directory is empty
if [[ ! -f "${PROFILES_DIR}/current" ]]; then
    if [[ -d "${SCRIPT_DIR}/example-profiles" ]]; then
        cp -rn "${SCRIPT_DIR}/example-profiles/"* "${PROFILES_DIR}/" 2>/dev/null || true
    fi
    echo "default" > "${PROFILES_DIR}/current"
fi

# 6. Check PATH
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
    echo -e "${YELLOW}Notice: ${BIN_DIR} is not in your PATH.${RESET}"
    echo "Add the following to your ~/.bashrc or ~/.zshrc:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

echo -e "\n${BOLD}${GREEN}✔ Installation complete!${RESET}\n"
echo -e "You can now run:"
echo -e "  ${CYAN}shell-switch${RESET}        - Open interactive GUI switcher"
echo -e "  ${CYAN}shell-switch list${RESET}   - List available shells in terminal"
echo -e "  ${CYAN}shell-switch <name>${RESET} - Switch instantly to a shell profile"
echo -e ""
echo -e "${BOLD}Recommended Hyprland Keybind:${RESET}"
echo -e "Add this to your ${CYAN}~/.config/hypr/hyprland.conf${RESET}:"
echo -e "  ${GREEN}bind = SUPER CONTROL, S, exec, desktop-shell-app${RESET}\n"
