# Maintainer: Pradhuman <https://github.com/Dev-pradhuman>
_pkgname=shell-switch
pkgname=shell-switch-git
pkgver=1.0.0
pkgrel=1
pkgdesc="Lightning-fast Desktop Shell & Rice Switcher for Hyprland with Libadwaita GUI & CLI"
arch=('any')
url="https://github.com/Dev-pradhuman/shell-switch"
license=('MIT')
depends=(
    'bash'
    'python'
    'python-gobject'
    'gtk4'
    'libadwaita'
)
optdepends=(
    'hyprland: Wayland compositor support'
    'waybar: Modular desktop status bar'
    'quickshell: Next-gen QtQuick desktop shell engine'
    'rofi-wayland: Quick dmenu launcher fallback'
    'swaynotificationcenter: Notification center'
    'libnotify: Desktop switch notification banners'
    'git: One-click cloning of online rice setups'
)
provides=("${_pkgname}")
conflicts=("${_pkgname}")
source=("git+${url}.git")
sha256sums=('SKIP')

pkgver() {
    cd "${srcdir}/${_pkgname}"
    git describe --long --tags --always 2>/dev/null | sed 's/^v//;s/\([^-]*-g\)/r\1/;s/-/./g' || printf "1.0.0"
}

package() {
    cd "${srcdir}/${_pkgname}"

    # Install executable binaries
    install -Dm755 "bin/shell-switch" "${pkgdir}/usr/bin/shell-switch"
    install -Dm755 "bin/desktop-shell-app.py" "${pkgdir}/usr/bin/desktop-shell-app"

    # Install desktop entry
    install -Dm644 "desktop/desktop-shell-switcher.desktop" "${pkgdir}/usr/share/applications/desktop-shell-switcher.desktop"

    # Install shell tab completions
    install -Dm644 "completions/shell-switch.bash" "${pkgdir}/usr/share/bash-completion/completions/shell-switch"
    install -Dm644 "completions/_shell-switch" "${pkgdir}/usr/share/zsh/site-functions/_shell-switch"
    install -Dm644 "completions/shell-switch.fish" "${pkgdir}/usr/share/fish/vendor_completions.d/shell-switch.fish"

    # Install example rice profiles
    install -dm755 "${pkgdir}/usr/share/${_pkgname}/example-profiles"
    cp -r example-profiles/* "${pkgdir}/usr/share/${_pkgname}/example-profiles/"

    # Install documentation and license
    install -Dm644 "README.md" "${pkgdir}/usr/share/doc/${_pkgname}/README.md"
    install -Dm644 "LICENSE" "${pkgdir}/usr/share/licenses/${pkgname}/LICENSE"
}
