<div align="center">

# ⚡ Desktop Shell Switcher
### Live Hot-Swapping for Hyprland & Wayland Desktop Shells & Rices

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/Platform-Arch%20%7C%20Hyprland%20%7C%20Wayland-brightgreen.svg?style=for-the-badge&logo=archlinux)](https://archlinux.org)
[![UI: Libadwaita / GTK4](https://img.shields.io/badge/UI-Libadwaita%20%2F%20GTK4-blueviolet.svg?style=for-the-badge&logo=gnome)](https://gnome.pages.gitlab.gnome.org/libadwaita/)
[![Bug Fix SLA: < 24 Hours](https://img.shields.io/badge/Bug%20Fixes-Within%2024%20Hours-orange.svg?style=for-the-badge&logo=github)](https://github.com/issues)

<p align="center">
  <b>Switch between completely different desktop rices and shells (Caelestia, DankMaterialShell, HyDE, end-4, ML4W, Waybar, Quickshell) instantly — without logging out, restarting Hyprland, or losing your open windows.</b>
</p>

[Features](#-key-features) • [Installation](#-installation) • [Usage](#-usage) • [Supported Rices](#-supported-rices-out-of-the-box) • [Add Your Own Rice](#-creating-your-own-rice-profile) • [24h Support](#-need-help--24-hour-bug-fix-guarantee)

---

</div>

<p align="center">
  <img src="assets/preview-hyde.png" alt="HyDE Preview" width="48%" style="border-radius: 10px; margin: 4px;" />
  <img src="assets/preview-44dots.png" alt="44 Dots Preview" width="48%" style="border-radius: 10px; margin: 4px;" />
</p>

---

## ✨ Key Features

- 🔄 **Live Hot-Swapping:** Change your entire desktop appearance, panels, widgets, and keybinds on the fly in `< 1 second`.
- 🪟 **Session Preserved:** Your open windows, terminals, workspaces, and running apps remain completely untouched.
- 🎨 **Modern Native GUI:** Built with Libadwaita / GTK4 in dark mode with responsive profile cards, tags, live previews, and reload buttons.
- ⚡ **Snappy Terminal CLI:** Quick switching from the terminal using `shell-switch <name>` with auto-completion and rich status colors.
- 🔗 **Smart Symlink Routing:** Dynamically swaps and manages symlinks for `~/.config/{hypr,waybar,quickshell,rofi,swaync,...}` cleanly without modifying your dotfiles repositories.
- 🚀 **Full Daemon Decoupling:** Uses session process detachment (`setsid`) so bars, daemons, and wallpapers never die unexpectedly.
- 📦 **Git Clone Integration:** Clone any dotfiles repository from GitHub directly inside the GUI or CLI (`shell-switch clone <url>`).

---

## 📸 Screenshots & Showcase

| HyDE Modular Desktop | ML4W Glass Center |
|:---:|:---:|
| <img src="assets/preview-hyde.png" width="400" /> | <img src="assets/preview-ml4w.png" width="400" /> |

| 44 Dots Rice | DankMaterialShell M3 |
|:---:|:---:|
| <img src="assets/preview-44dots.png" width="400" /> | *Quickshell M3 Panels & Control Center* |

---

## 📦 Supported Rices Out-of-the-Box

The switcher includes battle-tested adapters for popular Linux/Hyprland rice setups:

| Rice Profile | Architecture | Components |
| :--- | :--- | :--- |
| **Caelestia** | Quickshell | Dynamic colors, sliding drawers, wallpaper blur |
| **DankMaterialShell (DMS)** | Quickshell + Go daemon | Material 3 panels, dock, control center, audio visualizer |
| **HyDE Project** | Waybar + SwayNC + Rofi | Modular pill/leaf bar, Wallbash color engine, notifications |
| **end-4 (dots-hyprland)** | Quickshell `ii` suite | Material You widgets, background clocks, Fuzzel launcher |
| **ML4W Dotfiles** | Waybar (Glass) + SwayNC | Floating glass top bar, quicklinks, theme switcher |
| **44 Dots** | Waybar + SwayNC | Catppuccin Mocha minimal bar with persistent workspaces |
| **43PR Rice** | Quickshell + Hyprquickpaper | Custom top widget bar, wallpaper switcher |

---

## 🚀 Installation

### Prerequisites

Make sure you have PyGObject and Libadwaita installed:

#### Arch Linux / EndeavourOS:
```bash
sudo pacman -S --needed python-gobject gtk4 libadwaita waybar swaync git
```

#### Fedora:
```bash
sudo dnf install python3-gobject gtk4 libadwaita waybar swaync git
```

#### Ubuntu / Debian (Wayland):
```bash
sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1 waybar swaync git
```

---

### Quick Install

```bash
git clone https://github.com/Dev-pradhuman/shell-switch.git
cd shell-switch
./install.sh
```

The installer installs:
1. `shell-switch` into `~/.local/bin/` (CLI)
2. `desktop-shell-app` into `~/.local/bin/` (GUI)
3. Application launcher icon in your app menu (`desktop-shell-switcher.desktop`)

---

## ⌨️ Hyprland Keybinding

Add this single line to your `~/.config/hypr/hyprland.conf`:

```hyprlang
# Open Desktop Shell Switcher (Super + Ctrl + S)
bind = SUPER CONTROL, S, exec, desktop-shell-app
```

Now press `Super + Ctrl + S` anywhere to bring up the switcher!

---

## 💻 Usage

### 🖥️ GUI Switcher
Launch it from your application menu or run:
```bash
desktop-shell-app
# or
shell-switch gui
```

- Click **"Switch to this Shell"** on any card to activate it.
- Click **"Reload"** to restart the current active shell.
- Click **"+"** in the top header to clone a new dotfiles repo from GitHub.
- Click the **Folder** icon on any card to inspect its config files.

---

### ⌨️ Command Line Interface

```bash
# List all installed shells
shell-switch list

# Show the currently active shell
shell-switch current

# Switch to a shell immediately
shell-switch 44dots
shell-switch dms
shell-switch hyde
shell-switch end4
shell-switch ml4w
shell-switch caelestia

# Force restart the current shell
shell-switch caelestia --force

# Clone a new shell repository from GitHub
shell-switch clone https://github.com/username/my-rice.git my-rice
```

---

## 🛠️ Creating Your Own Rice Profile

Adding a new shell or dotfiles setup is as simple as creating a folder under `~/.config/desktop-shells/<profile-name>/`:

```
~/.config/desktop-shells/my-rice/
├── profile.sh      # Shell profile script (required)
└── preview.png     # Card preview banner (optional)
```

### Example `profile.sh`:

```bash
#!/usr/bin/env bash
NAME="My Custom Rice"
DESCRIPTION="Minimalist Hyprland setup with Waybar and SwayNC"
ICON="preferences-desktop-theme"

# Config folders to symlink into ~/.config/ when active
declare -A CONFIG_MAP=(
    ["hypr"]="$PROFILE_DIR/hypr"
    ["waybar"]="$PROFILE_DIR/waybar"
    ["swaync"]="$PROFILE_DIR/swaync"
)

# Startup Hook (starts your panels/daemons)
start_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
    pkill -x qs 2>/dev/null || true

    sleep 0.3
    setsid waybar >/dev/null 2>&1 &
    setsid swaync >/dev/null 2>&1 &
}

# Cleanup Hook (stops panels when switching away)
stop_shell() {
    pkill -x waybar 2>/dev/null || true
    pkill -x swaync 2>/dev/null || true
}
```

---

## 🚨 Need Help? / 24-Hour Bug Fix Guarantee

> [!IMPORTANT]
> ### ⚡ 24-Hour Bug Fix Guarantee
> If you encounter **any error, crash, missing bar, or compatibility issue** with any desktop shell:
> 1. [Open an Issue here](https://github.com/Dev-pradhuman/shell-switch/issues) with details about your distro and shell.
> 2. **We actively maintain this project and guarantee a response/fix within 24 hours!**

---

## 🤝 Contributing

Contributions are very welcome! If you have a popular rice or dotfile configuration you'd like an out-of-the-box profile adapter for, feel free to open a Pull Request.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">
  <b>Built with ❤️ for the Linux ricing community by <a href="https://github.com/Dev-pradhuman">Dev-pradhuman</a></b>
</div>
