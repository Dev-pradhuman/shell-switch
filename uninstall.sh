#!/usr/bin/env bash
# ==============================================================================
# Desktop Shell Switcher Uninstaller
# ==============================================================================

set -euo pipefail

BIN_DIR="${HOME}/.local/bin"
DESKTOP_DIR="${HOME}/.local/share/applications"

echo "Uninstalling Desktop Shell Switcher..."

rm -f "${BIN_DIR}/shell-switch"
rm -f "${BIN_DIR}/desktop-shell-app"
rm -f "${DESKTOP_DIR}/desktop-shell-switcher.desktop"

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "${DESKTOP_DIR}" >/dev/null 2>&1 || true
fi

echo "✔ Binaries and desktop entries removed."
echo "Note: Your shell configurations in ~/.config/desktop-shells/ were preserved."
