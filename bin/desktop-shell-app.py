#!/usr/bin/env python3
"""
Desktop Shell & Rice Switcher GUI
A modern, native Libadwaita / GTK4 application for managing and switching Hyprland desktop shells.
Features live search, 1-click rice explore store, active bar indicators, and keyboard navigation.
"""

import os
import sys
import subprocess
import threading
import shutil
from pathlib import Path

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gdk, Adw, GLib, Gio, Pango

PROFILES_DIR = Path.home() / ".config" / "desktop-shells"
CURRENT_FILE = PROFILES_DIR / "current"
CURRENT_KEYBINDS_FILE = PROFILES_DIR / "current_keybinds"
DEFAULT_SHELL_FILE = PROFILES_DIR / "default_shell"
DEFAULT_KEYBINDS_FILE = PROFILES_DIR / "default_keybinds"
PROJECT_DIR = Path(__file__).resolve().parent.parent
SWITCHER_BIN = PROJECT_DIR / "bin" / "shell-switch"
if not SWITCHER_BIN.exists():
    SWITCHER_BIN = Path.home() / ".local" / "bin" / "shell-switch"

CUSTOM_CSS = """
.rice-card {
    background-color: alpha(@card_bg_color, 0.95);
    border: 1px solid alpha(@borders, 0.4);
    border-radius: 16px;
    padding: 16px;
    transition: all 200ms ease;
}

.rice-card:hover {
    border-color: alpha(@accent_color, 0.5);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.rice-card-active {
    border: 2px solid @accent_color;
    background-color: alpha(@accent_bg_color, 0.12);
    box-shadow: 0 4px 20px alpha(@accent_color, 0.2);
}

.badge-active {
    background-color: @success_color;
    color: white;
    font-weight: 700;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 9999px;
}

.badge-installed {
    background-color: alpha(@accent_color, 0.2);
    color: @accent_color;
    font-weight: 700;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 9999px;
}

.badge-keybinds {
    background-color: alpha(@accent_color, 0.25);
    color: @accent_color;
    font-weight: 700;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 9999px;
    border: 1px solid alpha(@accent_color, 0.4);
}

.badge-default {
    background-color: alpha(#e5a50a, 0.2);
    color: #f6d32d;
    font-weight: 700;
    font-size: 11px;
    padding: 4px 12px;
    border-radius: 9999px;
}


.tag-chip {
    background-color: alpha(@theme_fg_color, 0.08);
    color: alpha(@theme_fg_color, 0.85);
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 6px;
}

.tag-bar {
    background-color: alpha(@accent_color, 0.15);
    color: @accent_color;
    font-size: 11px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 6px;
}

.card-title {
    font-weight: 800;
    font-size: 17px;
}

.card-desc {
    color: alpha(@theme_fg_color, 0.7);
    font-size: 13px;
}

.preview-image {
    border-radius: 12px;
}

.search-bar-box {
    margin-bottom: 12px;
}
"""

RICE_CATALOG = [
    {
        "id": "caelestia",
        "name": "Caelestia Shell",
        "desc": "Quickshell desktop shell with dynamic Material You colors, drawers, widgets & animations",
        "repo": "https://github.com/caelestia-dots/caelestia",
        "bar": "Quickshell",
        "icon": "preferences-desktop-theme",
        "tags": ["Quickshell", "Dynamic Theme", "Drawers", "Hyprland"],
        "preview": "assets/preview-44dots.png",
    },
    {
        "id": "hyde",
        "name": "HyDE Rice",
        "desc": "Modular HyDE Project Hyprland rice with Waybar, dynamic themes, Rofi, SwayNC & Dunst",
        "repo": "https://github.com/HyDE-Project/HyDE",
        "bar": "Waybar",
        "icon": "preferences-desktop-theme",
        "tags": ["Waybar", "Rofi", "SwayNC", "Hyprland"],
        "preview": "assets/preview-hyde.png",
    },
    {
        "id": "dms",
        "name": "DankMaterialShell",
        "desc": "Material 3 desktop shell built on Quickshell with dynamic theming, bottom dock & widgets",
        "repo": "https://github.com/AvengeMedia/DankMaterialShell",
        "bar": "Quickshell",
        "icon": "preferences-desktop-theme",
        "tags": ["Quickshell", "Material 3", "Desktop Dock", "Hyprland"],
        "preview": None,
    },
    {
        "id": "end4",
        "name": "end-4 Dots",
        "desc": "Material You desktop rice with Quickshell 'ii' suite, Matugen dynamic colors & Fuzzel launcher",
        "repo": "https://github.com/end-4/dots-hyprland",
        "bar": "Quickshell (ii)",
        "icon": "preferences-desktop-theme",
        "tags": ["Quickshell (ii)", "Material You", "Matugen", "Hyprland"],
        "preview": None,
    },
    {
        "id": "end4-pc",
        "name": "end4-pC (Material 3)",
        "desc": "Material 3 Expressive desktop fork with Quickshell, presets gallery, dynamic theming & dock",
        "repo": "https://github.com/pctrade/end4-pC",
        "bar": "Quickshell",
        "icon": "preferences-desktop-theme",
        "tags": ["Quickshell", "Material 3", "Presets Gallery", "Hyprland"],
        "preview": "assets/preview-end4-pc.png",
    },
    {
        "id": "ml4w",
        "name": "ML4W Dotfiles",
        "desc": "MyLinuxForWork modular Hyprland desktop with Waybar themes, settings app & Rofi",
        "repo": "https://github.com/mylinuxforwork/dotfiles",
        "bar": "Waybar",
        "icon": "preferences-desktop-theme",
        "tags": ["Waybar", "Rofi", "Settings App", "Hyprland"],
        "preview": "assets/preview-ml4w.png",
    },
    {
        "id": "44dots",
        "name": "44 Dots",
        "desc": "sr-44 clean Arch Linux & Hyprland rice with custom Waybar styles, SwayNC & Rofi",
        "repo": "https://github.com/44kash/dotfiles",
        "bar": "Waybar",
        "icon": "view-app-grid",
        "tags": ["Waybar", "SwayNC", "Rofi", "Hyprland"],
        "preview": "assets/preview-44dots.png",
    },
]


def load_profile_meta(profile_dir: Path):
    """Parses profile.sh metadata in a safe shell subshell."""
    profile_sh = profile_dir / "profile.sh"
    meta = {
        "id": profile_dir.name,
        "name": profile_dir.name,
        "description": "Custom desktop setup",
        "icon": "preferences-desktop-theme",
        "configs": [],
        "preview": None,
        "bar": None,
    }

    if not profile_sh.exists():
        return meta

    cmd = f"""
    source "{profile_sh}" 2>/dev/null || true
    echo "NAME=$NAME"
    echo "DESCRIPTION=$DESCRIPTION"
    echo "ICON=$ICON"
    if declare -p CONFIG_MAP >/dev/null 2>&1; then
        for k in "${{!CONFIG_MAP[@]}}"; do
            echo "CONFIG=$k"
        done
    fi
    """
    try:
        res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, timeout=3)
        for line in res.stdout.splitlines():
            if line.startswith("NAME="):
                val = line[5:].strip()
                if val:
                    meta["name"] = val
            elif line.startswith("DESCRIPTION="):
                val = line[12:].strip()
                if val:
                    meta["description"] = val
            elif line.startswith("ICON="):
                val = line[5:].strip()
                if val:
                    meta["icon"] = val
            elif line.startswith("CONFIG="):
                cfg = line[7:].strip()
                if cfg:
                    meta["configs"].append(cfg)
    except Exception as e:
        print(f"Error parsing {profile_sh}: {e}", file=sys.stderr)

    # Determine bar daemon
    if "quickshell" in meta["configs"] or (profile_dir / "quickshell").exists() or (profile_dir / "repo" / "quickshell").exists():
        meta["bar"] = "Quickshell"
    elif "waybar" in meta["configs"] or (profile_dir / "waybar").exists() or (profile_dir / "repo" / "waybar").exists():
        meta["bar"] = "Waybar"
    elif "dms" in meta["configs"]:
        meta["bar"] = "Quickshell"

    # Check for preview image
    for img_candidate in [
        profile_dir / "preview.png",
        profile_dir / "preview.jpg",
        PROJECT_DIR / f"assets/preview-{profile_dir.name}.png",
        profile_dir / "repo" / "screenshots" / "1.png",
        profile_dir / "repo" / "screenshots" / "hyprland-3.png",
        profile_dir / "repo" / "screenshots" / "hypland.png",
    ]:
        if img_candidate.exists():
            meta["preview"] = str(img_candidate.resolve())
            break

    return meta


class AddShellDialog(Adw.Window):
    """Modal dialog for cloning from Git or adding a local shell."""

    def __init__(self, parent_window, on_added_callback):
        super().__init__(modal=True, transient_for=parent_window)
        self.set_title("Add New Desktop Shell")
        self.set_default_size(520, 380)
        self.on_added_callback = on_added_callback

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_margin_top(20)
        content.set_margin_bottom(20)
        content.set_margin_start(24)
        content.set_margin_end(24)

        header = Adw.HeaderBar()
        self.set_title("Add Shell Profile")

        # Tab Switcher: Clone Git vs Blank Template
        stack = Adw.ViewStack()

        # Page 1: Git Clone
        page_git = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_git.set_margin_top(12)

        git_group = Adw.PreferencesGroup(title="Clone from GitHub Repository")
        self.url_entry = Adw.EntryRow(title="Git URL (HTTPS)")
        self.url_entry.set_text("https://github.com/")
        git_group.add(self.url_entry)

        self.name_entry = Adw.EntryRow(title="Profile Name (Optional)")
        git_group.add(self.name_entry)
        page_git.append(git_group)

        self.clone_btn = Gtk.Button(label="Clone and Create Profile", css_classes=["suggested-action", "pill"])
        self.clone_btn.connect("clicked", self.on_clone_clicked)
        page_git.append(self.clone_btn)

        # Page 2: Blank Template
        page_blank = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_blank.set_margin_top(12)

        blank_group = Adw.PreferencesGroup(title="Create Blank Shell Profile")
        self.blank_name = Adw.EntryRow(title="New Profile Identifier")
        self.blank_name.set_text("my-custom-rice")
        blank_group.add(self.blank_name)
        page_blank.append(blank_group)

        self.blank_btn = Gtk.Button(label="Generate Template", css_classes=["suggested-action", "pill"])
        self.blank_btn.connect("clicked", self.on_blank_clicked)
        page_blank.append(self.blank_btn)

        stack.add_titled(page_git, "git", "Clone from Git")
        stack.add_titled(page_blank, "blank", "New Template")

        view_switcher = Adw.ViewSwitcher(stack=stack, policy=Adw.ViewSwitcherPolicy.WIDE)

        content.append(view_switcher)
        content.append(stack)

        # Status spinner
        self.spinner = Gtk.Spinner()
        self.status_lbl = Gtk.Label(label="", css_classes=["card-desc"])
        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        status_box.append(self.spinner)
        status_box.append(self.status_lbl)
        content.append(status_box)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.append(header)
        main_box.append(content)
        self.set_content(main_box)

    def on_clone_clicked(self, btn):
        url = self.url_entry.get_text().strip()
        custom_name = self.name_entry.get_text().strip()

        if not url or url == "https://github.com/":
            self.status_lbl.set_text("Please enter a valid Git URL.")
            return

        self.spinner.start()
        self.clone_btn.set_sensitive(False)
        self.status_lbl.set_text(f"Cloning {url}...")

        def worker():
            cmd = [str(SWITCHER_BIN), "clone", url]
            if custom_name:
                cmd.append(custom_name)
            res = subprocess.run(cmd, capture_output=True, text=True)

            def done():
                self.spinner.stop()
                self.clone_btn.set_sensitive(True)
                if res.returncode == 0:
                    self.on_added_callback()
                    self.close()
                else:
                    self.status_lbl.set_text(f"Error: {res.stderr or 'Clone failed'}")

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def on_blank_clicked(self, btn):
        name = self.blank_name.get_text().strip()
        if not name:
            self.status_lbl.set_text("Please specify a name.")
            return

        res = subprocess.run([str(SWITCHER_BIN), "add", name], capture_output=True, text=True)
        if res.returncode == 0:
            self.on_added_callback()
            self.close()
        else:
            self.status_lbl.set_text(f"Error: {res.stderr or 'Failed to create'}")


class ShellSwitcherWindow(Adw.ApplicationWindow):
    """Main Application Window with Tabbed View and Live Search."""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Desktop Shell Switcher")
        self.set_default_size(860, 780)

        # Keyboard Navigation controller
        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.add_controller(key_controller)

        # Toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()

        # Main Layout Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header Bar
        header = Adw.HeaderBar()

        # View Stack & Switcher Title (Installed vs Explore)
        self.view_stack = Adw.ViewStack()

        self.switcher_title = Adw.ViewSwitcherTitle()
        self.switcher_title.set_stack(self.view_stack)
        self.switcher_title.set_title("Desktop Shell Switcher")
        self.switcher_title.set_subtitle(f"Active: {self.get_current_shell()}")
        header.set_title_widget(self.switcher_title)

        # Add / Clone Button
        add_btn = Gtk.Button(icon_name="list-add-symbolic", tooltip_text="Add / Clone New Shell")
        add_btn.connect("clicked", self.on_add_clicked)
        header.pack_start(add_btn)

        # Snapshot / Backup Button
        backup_btn = Gtk.Button(icon_name="document-save-symbolic", tooltip_text="Snapshot Active Desktop Config (Backup)")
        backup_btn.connect("clicked", self.on_backup_clicked)
        header.pack_start(backup_btn)

        # Dark / Light Theme Toggle Button
        current_theme = "dark"
        theme_file = PROFILES_DIR / "current_theme"
        if theme_file.exists():
            current_theme = theme_file.read_text().strip().lower()
        is_dark = (current_theme == "dark")
        self.theme_btn = Gtk.Button(
            icon_name="weather-clear-night-symbolic" if is_dark else "weather-clear-symbolic",
            tooltip_text=f"Theme: {current_theme.capitalize()} (Click to toggle)",
        )
        self.theme_btn.connect("clicked", self.on_theme_toggle_clicked)
        header.pack_end(self.theme_btn)

        # Refresh Button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text="Refresh List (Ctrl+R)")
        refresh_btn.connect("clicked", lambda b: self.refresh_all())
        header.pack_end(refresh_btn)

        main_box.append(header)

        # =====================================================================
        # Page 1: Installed Profiles
        # =====================================================================
        installed_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        installed_scrolled = Gtk.ScrolledWindow()
        installed_scrolled.set_vexpand(True)
        installed_scrolled.set_hexpand(True)

        installed_clamp = Adw.Clamp()
        installed_clamp.set_maximum_size(820)
        installed_clamp.set_tightening_threshold(600)
        installed_clamp.set_margin_top(16)
        installed_clamp.set_margin_bottom(24)
        installed_clamp.set_margin_start(20)
        installed_clamp.set_margin_end(20)

        installed_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)

        # Live Search Entry
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search installed desktop shells (Ctrl+F)...")
        self.search_entry.connect("search-changed", self.on_search_changed)
        installed_container.append(self.search_entry)

        # Cards Box
        self.cards_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        installed_container.append(self.cards_box)

        installed_clamp.set_child(installed_container)
        installed_scrolled.set_child(installed_clamp)
        installed_box.append(installed_scrolled)

        page_installed = self.view_stack.add_titled(installed_box, "installed", "Installed")
        page_installed.set_icon_name("view-app-grid-symbolic")

        # =====================================================================
        # Page 2: Explore Rice Catalog
        # =====================================================================
        explore_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        explore_scrolled = Gtk.ScrolledWindow()
        explore_scrolled.set_vexpand(True)
        explore_scrolled.set_hexpand(True)

        explore_clamp = Adw.Clamp()
        explore_clamp.set_maximum_size(820)
        explore_clamp.set_tightening_threshold(600)
        explore_clamp.set_margin_top(16)
        explore_clamp.set_margin_bottom(24)
        explore_clamp.set_margin_start(20)
        explore_clamp.set_margin_end(20)

        self.explore_cards_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        explore_clamp.set_child(self.explore_cards_box)
        explore_scrolled.set_child(explore_clamp)
        explore_box.append(explore_scrolled)

        page_explore = self.view_stack.add_titled(explore_box, "explore", "Explore Rices")
        page_explore.set_icon_name("starred-symbolic")

        main_box.append(self.view_stack)
        self.toast_overlay.set_child(main_box)
        self.set_content(self.toast_overlay)

        # State tracking
        self.all_profile_cards = []

        # Load shell profiles & catalog
        self.refresh_all()

    def on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.close()
            return True
        elif keyval == Gdk.KEY_f and (state & Gdk.ModifierType.CONTROL_MASK):
            self.view_stack.set_visible_child_name("installed")
            self.search_entry.grab_focus()
            return True
        elif keyval == Gdk.KEY_r and (state & Gdk.ModifierType.CONTROL_MASK):
            self.refresh_all()
            return True
        return False

    def on_theme_toggle_clicked(self, btn):
        def worker():
            res = subprocess.run([str(SWITCHER_BIN), "theme", "toggle"], capture_output=True, text=True)

            def done():
                current_theme = "dark"
                theme_file = PROFILES_DIR / "current_theme"
                if theme_file.exists():
                    current_theme = theme_file.read_text().strip().lower()

                is_dark = (current_theme == "dark")
                self.theme_btn.set_icon_name("weather-clear-night-symbolic" if is_dark else "weather-clear-symbolic")
                self.theme_btn.set_tooltip_text(f"Theme: {current_theme.capitalize()} (Click to toggle)")

                style_mgr = Adw.StyleManager.get_default()
                style_mgr.set_color_scheme(Adw.ColorScheme.FORCE_DARK if is_dark else Adw.ColorScheme.FORCE_LIGHT)

                self.toast_overlay.add_toast(Adw.Toast.new(f"Switched theme to: {current_theme.capitalize()}"))

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def get_current_shell(self):
        if CURRENT_FILE.exists():
            return CURRENT_FILE.read_text().strip()
        return self.get_default_shell()

    def get_current_keybinds(self):
        if CURRENT_KEYBINDS_FILE.exists():
            return CURRENT_KEYBINDS_FILE.read_text().strip()
        return self.get_default_keybinds()

    def get_default_shell(self):
        if DEFAULT_SHELL_FILE.exists():
            return DEFAULT_SHELL_FILE.read_text().strip()
        return "caelestia"

    def get_default_keybinds(self):
        if DEFAULT_KEYBINDS_FILE.exists():
            return DEFAULT_KEYBINDS_FILE.read_text().strip()
        return self.get_default_shell()

    def refresh_all(self):
        self.refresh_profiles()
        self.refresh_explore()

    def refresh_profiles(self):
        while child := self.cards_box.get_first_child():
            self.cards_box.remove(child)

        self.all_profile_cards.clear()

        current = self.get_current_shell()
        current_kb = self.get_current_keybinds()
        self.switcher_title.set_subtitle(f"Active Shell: {current}  •  Keybinds: {current_kb}")

        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        profiles = []
        for pdir in sorted(PROFILES_DIR.iterdir()):
            if pdir.is_dir():
                profiles.append(load_profile_meta(pdir))

        if not profiles:
            empty_lbl = Gtk.Label(
                label="No desktop shells found.\nClick the '+' button to add or clone one!",
                justify=Gtk.Justification.CENTER,
                css_classes=["title-3", "card-desc"],
            )
            empty_lbl.set_margin_top(60)
            self.cards_box.append(empty_lbl)
            return

        # Render Active Profile First, then remaining
        profiles.sort(key=lambda p: (p["id"] != current, p["name"].lower()))
        all_pids = [p["id"] for p in profiles]

        for meta in profiles:
            card = self.create_profile_card(meta, is_active=(meta["id"] == current), all_profile_ids=all_pids)
            self.all_profile_cards.append({
                "widget": card,
                "meta": meta,
                "search_text": f"{meta['id']} {meta['name']} {meta['description']} {' '.join(meta.get('configs', []))}".lower(),
            })
            self.cards_box.append(card)

        # Apply current search filter
        self.on_search_changed(self.search_entry)

    def on_search_changed(self, entry):
        query = entry.get_text().strip().lower()
        visible_count = 0

        for item in self.all_profile_cards:
            matches = not query or (query in item["search_text"])
            item["widget"].set_visible(matches)
            if matches:
                visible_count += 1

    def create_profile_card(self, meta, is_active: bool, all_profile_ids: list = None):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card_classes = ["rice-card"]
        if is_active:
            card_classes.append("rice-card-active")
        card.set_css_classes(card_classes)

        # Optional preview banner
        if meta.get("preview") and os.path.exists(meta["preview"]):
            try:
                picture = Gtk.Picture.new_for_filename(meta["preview"])
                picture.set_content_fit(Gtk.ContentFit.COVER)
                picture.set_size_request(-1, 160)
                picture.set_css_classes(["preview-image"])
                card.append(picture)
            except Exception as e:
                print(f"Error loading preview image: {e}")

        # Header Row: Icon + Title/ID + Active Badge / Switch Button
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)

        icon_img = Gtk.Image.new_from_icon_name(meta["icon"])
        icon_img.set_pixel_size(36)
        top_row.append(icon_img)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label(label=meta["name"], css_classes=["card-title"], xalign=0)
        id_lbl = Gtk.Label(label=f"ID: {meta['id']}", css_classes=["card-desc"], xalign=0)
        title_box.append(title_lbl)
        title_box.append(id_lbl)
        top_row.append(title_box)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top_row.append(spacer)

        is_kb_active = (meta["id"] == self.get_current_keybinds())
        is_default = (meta["id"] == self.get_default_shell())

        # Keybind profile dropdown selector
        kb_options = ["Match Shell", "Default"]
        if all_profile_ids:
            for pid in all_profile_ids:
                if pid not in ("match", "default") and pid not in kb_options:
                    kb_options.append(pid)

        kb_dropdown = Gtk.DropDown.new_from_strings(kb_options)
        kb_dropdown.set_valign(Gtk.Align.CENTER)
        kb_dropdown.set_tooltip_text(f"Keybinds profile to pair with {meta['name']}")

        cur_kb = self.get_current_keybinds()
        if is_active and cur_kb in kb_options:
            kb_dropdown.set_selected(kb_options.index(cur_kb))
        else:
            kb_dropdown.set_selected(0)

        def get_selected_kb():
            item = kb_dropdown.get_selected_item()
            txt = item.get_string() if item else "Match Shell"
            if txt == "Match Shell":
                return "match"
            elif txt == "Default":
                return "default"
            return txt

        top_row.append(kb_dropdown)

        if is_active:
            active_badge = Gtk.Label(label="● Active Shell", css_classes=["badge-active"])
            top_row.append(active_badge)

            reload_btn = Gtk.Button(label="Reload", tooltip_text="Restart current shell with selected keybinds")
            reload_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_switch_clicked(mid, keybinds=get_selected_kb(), force=True))
            top_row.append(reload_btn)
        else:
            switch_btn = Gtk.Button(label="Switch to this Shell", css_classes=["suggested-action", "pill"])
            switch_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_switch_clicked(mid, keybinds=get_selected_kb()))
            top_row.append(switch_btn)

        if is_kb_active:
            kb_badge = Gtk.Label(label="󰌌 Keybinds Active", css_classes=["badge-keybinds"])
            top_row.append(kb_badge)

        if is_default:
            def_badge = Gtk.Label(label="★ Default", css_classes=["badge-default"])
            top_row.append(def_badge)

        card.append(top_row)

        # Description
        desc_lbl = Gtk.Label(label=meta["description"], css_classes=["card-desc"], wrap=True, xalign=0)
        card.append(desc_lbl)

        # Tags & Actions Row
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Bar Daemon Tag (Quickshell vs Waybar)
        if meta.get("bar"):
            bar_chip = Gtk.Label(label=f"󰍹 {meta['bar']}", css_classes=["tag-bar"])
            bottom_row.append(bar_chip)

        # Config tags
        tags = list(meta.get("configs", []))
        if "hypr" not in tags and (PROFILES_DIR / meta["id"] / "hypr").exists():
            tags.append("hypr")

        icon_map = {
            "hypr": "󰨇 Hyprland",
            "quickshell": "󰅀 Quickshell",
            "waybar": "󰍹 Waybar",
            "swaync": "󰂚 Swaync",
            "rofi": "󰀻 Rofi",
            "fuzzel": "󰀻 Fuzzel",
        }

        for t in tags:
            tag_label = icon_map.get(t, t.capitalize())
            chip = Gtk.Label(label=tag_label, css_classes=["tag-chip"])
            bottom_row.append(chip)

        b_spacer = Gtk.Box()
        b_spacer.set_hexpand(True)
        bottom_row.append(b_spacer)

        # Keybinds button
        kb_btn = Gtk.Button(
            icon_name="input-keyboard-symbolic",
            tooltip_text=f"Use '{meta['name']}' keybinds across all rices",
        )
        if is_kb_active:
            kb_btn.add_css_class("suggested-action")
        kb_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_keybinds_clicked(mid))
        bottom_row.append(kb_btn)

        # Default shell button
        def_btn = Gtk.Button(
            icon_name="starred-symbolic" if is_default else "non-starred-symbolic",
            tooltip_text=f"Set '{meta['name']}' as default shell & keybinds",
        )
        def_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_set_default_clicked(mid))
        bottom_row.append(def_btn)

        # Folder button
        folder_btn = Gtk.Button(icon_name="folder-symbolic", tooltip_text="Open Profile Directory")
        folder_btn.connect("clicked", lambda b, mid=meta["id"]: self.open_folder(mid))
        bottom_row.append(folder_btn)

        # Delete button (only if not active)
        if not is_active:
            del_btn = Gtk.Button(icon_name="user-trash-symbolic", tooltip_text="Delete Profile")
            del_btn.set_css_classes(["destructive-action"])
            del_btn.connect("clicked", lambda b, mid=meta["id"], mname=meta["name"]: self.confirm_delete(mid, mname))
            bottom_row.append(del_btn)

        card.append(bottom_row)
        return card


    def refresh_explore(self):
        while child := self.explore_cards_box.get_first_child():
            self.explore_cards_box.remove(child)

        header_lbl = Gtk.Label(
            label="Explore Popular Hyprland Desktop Rices",
            css_classes=["title-2"],
            xalign=0,
        )
        sub_lbl = Gtk.Label(
            label="1-Click install curated dotfiles adapters directly into your switcher.",
            css_classes=["card-desc"],
            xalign=0,
        )
        self.explore_cards_box.append(header_lbl)
        self.explore_cards_box.append(sub_lbl)

        current = self.get_current_shell()

        for rice in RICE_CATALOG:
            card = self.create_explore_card(rice, current)
            self.explore_cards_box.append(card)

    def create_explore_card(self, rice, current: str):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        card.set_css_classes(["rice-card"])

        rice_id = rice["id"]
        is_installed = (PROFILES_DIR / rice_id).exists()
        is_active = (rice_id == current)

        # Preview Banner
        preview_path = PROJECT_DIR / f"assets/preview-{rice_id}.png"
        if not preview_path.exists() and (PROFILES_DIR / rice_id / "preview.png").exists():
            preview_path = PROFILES_DIR / rice_id / "preview.png"

        if preview_path.exists():
            try:
                picture = Gtk.Picture.new_for_filename(str(preview_path))
                picture.set_content_fit(Gtk.ContentFit.COVER)
                picture.set_size_request(-1, 150)
                picture.set_css_classes(["preview-image"])
                card.append(picture)
            except Exception as e:
                print(f"Error loading preview: {e}")

        # Top row
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        icon_img = Gtk.Image.new_from_icon_name(rice["icon"])
        icon_img.set_pixel_size(36)
        top_row.append(icon_img)

        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        title_lbl = Gtk.Label(label=rice["name"], css_classes=["card-title"], xalign=0)
        repo_lbl = Gtk.LinkButton(label=rice["repo"], uri=rice["repo"])
        repo_lbl.set_halign(Gtk.Align.START)
        title_box.append(title_lbl)
        title_box.append(repo_lbl)
        top_row.append(title_box)

        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top_row.append(spacer)

        if is_active:
            top_row.append(Gtk.Label(label="● Active", css_classes=["badge-active"]))
        elif is_installed:
            top_row.append(Gtk.Label(label="✔ Installed", css_classes=["badge-installed"]))
            switch_btn = Gtk.Button(label="Switch", css_classes=["suggested-action", "pill"])
            switch_btn.connect("clicked", lambda b, mid=rice_id: self.on_switch_clicked(mid))
            top_row.append(switch_btn)
        else:
            get_btn = Gtk.Button(label="Get Rice", css_classes=["suggested-action", "pill"])
            get_btn.connect("clicked", lambda b, mid=rice_id, btn=get_btn: self.on_install_rice(mid, btn))
            top_row.append(get_btn)

        card.append(top_row)

        desc_lbl = Gtk.Label(label=rice["desc"], css_classes=["card-desc"], wrap=True, xalign=0)
        card.append(desc_lbl)

        # Tags row
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        bar_chip = Gtk.Label(label=f"󰍹 {rice['bar']}", css_classes=["tag-bar"])
        bottom_row.append(bar_chip)

        for t in rice.get("tags", []):
            chip = Gtk.Label(label=t, css_classes=["tag-chip"])
            bottom_row.append(chip)

        card.append(bottom_row)
        return card

    def on_install_rice(self, rice_id: str, button: Gtk.Button):
        button.set_sensitive(False)
        button.set_label("Installing...")

        toast = Adw.Toast.new(f"Downloading and configuring '{rice_id}'...")
        toast.set_timeout(5)
        self.toast_overlay.add_toast(toast)

        def worker():
            cmd = [str(SWITCHER_BIN), "get", rice_id]
            res = subprocess.run(cmd, capture_output=True, text=True)

            def update_ui():
                if res.returncode == 0:
                    success_toast = Adw.Toast.new(f"Successfully installed '{rice_id}'!")
                    success_toast.set_timeout(4)
                    self.toast_overlay.add_toast(success_toast)
                else:
                    err_toast = Adw.Toast.new(f"Install failed: {res.stderr or 'Error'}")
                    self.toast_overlay.add_toast(err_toast)
                self.refresh_all()

            GLib.idle_add(update_ui)

        threading.Thread(target=worker, daemon=True).start()

    def on_backup_clicked(self, btn):
        toast = Adw.Toast.new("Creating desktop configuration snapshot...")
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        def worker():
            res = subprocess.run([str(SWITCHER_BIN), "backup"], capture_output=True, text=True)

            def done():
                if res.returncode == 0:
                    self.toast_overlay.add_toast(Adw.Toast.new("Snapshot created successfully!"))
                else:
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Backup failed: {res.stderr}"))
                self.refresh_profiles()

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def on_switch_clicked(self, profile_id: str, keybinds: str = None, force: bool = False):
        msg = f"Switching to '{profile_id}'"
        if keybinds and keybinds != "match":
            msg += f" (keybinds: {keybinds})"
        msg += "..."
        toast = Adw.Toast.new(msg)
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        # Auto-Preview (grim): when profile lacks preview, snapshot after bar renders
        profile_dir = PROFILES_DIR / profile_id
        if not (profile_dir / "preview.png").exists() and not (profile_dir / "preview.jpg").exists():
            subprocess.Popen(
                f'(sleep 2.0 && grim "{profile_dir}/preview.png") &',
                shell=True,
            )

        def run_switch():
            cmd = [str(SWITCHER_BIN), profile_id]
            if keybinds and keybinds != "match":
                cmd.append(keybinds)
            elif keybinds == "match":
                cmd.append(profile_id)
            if force:
                cmd.append("--force")
            res = subprocess.run(cmd, capture_output=True, text=True)

            def update_ui():
                if res.returncode == 0:
                    success_toast = Adw.Toast.new(f"Successfully activated: {profile_id}!")
                    success_toast.set_timeout(4)
                    self.toast_overlay.add_toast(success_toast)
                else:
                    err_toast = Adw.Toast.new(f"Switch error: {res.stderr or 'Failed'}")
                    self.toast_overlay.add_toast(err_toast)
                self.refresh_all()

            GLib.idle_add(update_ui)

        threading.Thread(target=run_switch, daemon=True).start()

    def on_keybinds_clicked(self, profile_id: str):
        toast = Adw.Toast.new(f"Setting keybinds profile to '{profile_id}'...")
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        def worker():
            res = subprocess.run([str(SWITCHER_BIN), "keybinds", profile_id], capture_output=True, text=True)

            def done():
                if res.returncode == 0:
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Keybinds switched to: {profile_id}!"))
                else:
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Error setting keybinds: {res.stderr}"))
                self.refresh_profiles()

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def on_set_default_clicked(self, profile_id: str):
        toast = Adw.Toast.new(f"Setting default desktop to '{profile_id}'...")
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        def worker():
            res = subprocess.run([str(SWITCHER_BIN), "set-default", profile_id], capture_output=True, text=True)

            def done():
                if res.returncode == 0:
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Default shell set to: {profile_id}!"))
                else:
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Error setting default: {res.stderr}"))
                self.refresh_profiles()

            GLib.idle_add(done)

        threading.Thread(target=worker, daemon=True).start()

    def open_folder(self, profile_id: str):
        target = PROFILES_DIR / profile_id
        if target.exists():
            subprocess.Popen(["xdg-open", str(target)])

    def confirm_delete(self, profile_id: str, profile_name: str):
        dialog = Adw.MessageDialog(
            transient_for=self,
            heading=f"Delete '{profile_name}'?",
            body=f"This will permanently delete profile '{profile_id}' from your desktop shells.",
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)

        def on_response(d, response_id):
            if response_id == "delete":
                target = PROFILES_DIR / profile_id
                if target.exists():
                    shutil.rmtree(target, ignore_errors=True)
                    self.toast_overlay.add_toast(Adw.Toast.new(f"Deleted profile: {profile_name}"))
                    self.refresh_all()

        dialog.connect("response", on_response)
        dialog.present()

    def on_add_clicked(self, btn):
        dialog = AddShellDialog(self, on_added_callback=self.refresh_all)
        dialog.present()


class ShellSwitcherApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.pradhuman.DesktopShellSwitcher",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        theme_file = PROFILES_DIR / "current_theme"
        current_theme = "dark"
        if theme_file.exists():
            current_theme = theme_file.read_text().strip().lower()
        if current_theme == "light":
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_LIGHT)
        else:
            Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)

        disp = Gdk.Display.get_default()
        if disp:
            provider = Gtk.CssProvider()
            provider.load_from_data(CUSTOM_CSS.encode("utf-8"))
            Gtk.StyleContext.add_provider_for_display(
                disp, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

        win = self.props.active_window
        if not win:
            win = ShellSwitcherWindow(self)
        win.present()


def main():
    app = ShellSwitcherApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
