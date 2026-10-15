#!/usr/bin/env python3
"""
Desktop Shell & Rice Switcher GUI
A modern, native Libadwaita / GTK4 application for managing and switching Hyprland desktop shells.
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

.tag-chip {
    background-color: alpha(@theme_fg_color, 0.08);
    color: alpha(@theme_fg_color, 0.85);
    font-size: 11px;
    font-weight: 600;
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
"""


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

    # Check for preview image
    for img_candidate in [
        profile_dir / "preview.png",
        profile_dir / "preview.jpg",
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

        header = Gtk.Label(
            label="Import Dotfiles or Create a New Rice",
            css_classes=["title-3"],
            xalign=0,
        )
        content.append(header)

        desc = Gtk.Label(
            label="Clone any Hyprland or Wayland dotfiles repository directly from GitHub, or initialize an empty template.",
            css_classes=["card-desc"],
            wrap=True,
            xalign=0,
        )
        content.append(desc)

        # Form Group
        pref_group = Adw.PreferencesGroup()

        # URL Entry
        self.url_row = Adw.EntryRow(title="GitHub / Git URL")
        self.url_row.set_text("https://github.com/")
        pref_group.add(self.url_row)

        # Name Entry
        self.name_row = Adw.EntryRow(title="Profile Name (Optional)")
        pref_group.add(self.name_row)

        content.append(pref_group)

        # Status & Spinner
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.status_box.set_halign(Gtk.Align.CENTER)
        self.spinner = Gtk.Spinner()
        self.status_label = Gtk.Label(label="", css_classes=["card-desc"])
        self.status_box.append(self.spinner)
        self.status_box.append(self.status_label)
        content.append(self.status_box)

        # Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect("clicked", lambda b: self.close())
        btn_box.append(cancel_btn)

        self.clone_btn = Gtk.Button(label="Clone & Add Shell", css_classes=["suggested-action", "pill"])
        self.clone_btn.connect("clicked", self.on_clone_clicked)
        btn_box.append(self.clone_btn)

        content.append(btn_box)
        self.set_content(content)

    def on_clone_clicked(self, btn):
        url = self.url_row.get_text().strip()
        name = self.name_row.get_text().strip()

        if not url or url == "https://github.com/":
            self.status_label.set_text("Please enter a valid Git URL.")
            return

        self.clone_btn.set_sensitive(False)
        self.spinner.start()
        self.status_label.set_text("Cloning repository in background...")

        def run_clone():
            cmd = [str(SWITCHER_BIN), "clone", url]
            if name:
                cmd.append(name)
            res = subprocess.run(cmd, capture_output=True, text=True)

            def done():
                self.spinner.stop()
                if res.returncode == 0:
                    self.on_added_callback()
                    self.close()
                else:
                    self.clone_btn.set_sensitive(True)
                    err_msg = res.stderr or res.stdout or "Failed to clone repository."
                    self.status_label.set_text(f"Error: {err_msg[:60]}")

            GLib.idle_add(done)

        threading.Thread(target=run_clone, daemon=True).start()


class ShellSwitcherWindow(Adw.ApplicationWindow):
    """Main Application Window."""

    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Desktop Shell Switcher")
        self.set_default_size(840, 750)

        # Toast overlay for notifications
        self.toast_overlay = Adw.ToastOverlay()

        # Main Layout Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header Bar
        header = Adw.HeaderBar()
        self.title_widget = Adw.WindowTitle(
            title="Desktop Shell Switcher",
            subtitle=f"Active: {self.get_current_shell()}",
        )
        header.set_title_widget(self.title_widget)

        # Add / Clone Button
        add_btn = Gtk.Button(icon_name="list-add-symbolic", tooltip_text="Add / Clone New Shell")
        add_btn.connect("clicked", self.on_add_clicked)
        header.pack_start(add_btn)

        # Refresh Button
        refresh_btn = Gtk.Button(icon_name="view-refresh-symbolic", tooltip_text="Refresh List")
        refresh_btn.connect("clicked", lambda b: self.refresh_profiles())
        header.pack_end(refresh_btn)

        main_box.append(header)

        # Scrolled content area
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_hexpand(True)

        clamp = Adw.Clamp()
        clamp.set_maximum_size(800)
        clamp.set_tightening_threshold(600)
        clamp.set_margin_top(20)
        clamp.set_margin_bottom(24)
        clamp.set_margin_start(20)
        clamp.set_margin_end(20)

        self.cards_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        clamp.set_child(self.cards_box)
        scrolled.set_child(clamp)

        main_box.append(scrolled)
        self.toast_overlay.set_child(main_box)
        self.set_content(self.toast_overlay)

        # Load shell profiles
        self.refresh_profiles()

    def get_current_shell(self):
        if CURRENT_FILE.exists():
            return CURRENT_FILE.read_text().strip()
        return "caelestia"

    def refresh_profiles(self):
        # Clear existing cards
        while child := self.cards_box.get_first_child():
            self.cards_box.remove(child)

        current = self.get_current_shell()
        self.title_widget.set_subtitle(f"Active: {current}")

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

        for meta in profiles:
            card = self.create_profile_card(meta, is_active=(meta["id"] == current))
            self.cards_box.append(card)

    def create_profile_card(self, meta, is_active: bool):
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

        # Push action to right
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        top_row.append(spacer)

        if is_active:
            active_badge = Gtk.Label(label="● Active Shell", css_classes=["badge-active"])
            top_row.append(active_badge)

            reload_btn = Gtk.Button(label="Reload", tooltip_text="Restart current shell")
            reload_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_switch_clicked(mid, force=True))
            top_row.append(reload_btn)
        else:
            switch_btn = Gtk.Button(label="Switch to this Shell", css_classes=["suggested-action", "pill"])
            switch_btn.connect("clicked", lambda b, mid=meta["id"]: self.on_switch_clicked(mid))
            top_row.append(switch_btn)

        card.append(top_row)

        # Description
        desc_lbl = Gtk.Label(label=meta["description"], css_classes=["card-desc"], wrap=True, xalign=0)
        card.append(desc_lbl)

        # Tags & Actions Row
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Tags
        tags = meta.get("configs", [])
        if "hypr" not in tags and (PROFILES_DIR / meta["id"] / "hypr").exists():
            tags.append("hypr")

        icon_map = {
            "hypr": "󰨇 Hyprland",
            "quickshell": "󰅀 Quickshell",
            "waybar": "󰍹 Waybar",
            "swaync": "󰂚 Swaync",
            "rofi": "󰀻 Rofi",
        }

        for t in tags:
            tag_label = icon_map.get(t, t.capitalize())
            chip = Gtk.Label(label=tag_label, css_classes=["tag-chip"])
            bottom_row.append(chip)

        b_spacer = Gtk.Box()
        b_spacer.set_hexpand(True)
        bottom_row.append(b_spacer)

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

    def on_switch_clicked(self, profile_id: str, force: bool = False):
        toast = Adw.Toast.new(f"Switching to '{profile_id}'...")
        toast.set_timeout(2)
        self.toast_overlay.add_toast(toast)

        def run_switch():
            cmd = [str(SWITCHER_BIN), profile_id]
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
                self.refresh_profiles()

            GLib.idle_add(update_ui)

        threading.Thread(target=run_switch, daemon=True).start()

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
                    self.refresh_profiles()

        dialog.connect("response", on_response)
        dialog.present()

    def on_add_clicked(self, btn):
        dialog = AddShellDialog(self, on_added_callback=self.refresh_profiles)
        dialog.present()


class ShellSwitcherApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.pradhuman.DesktopShellSwitcher",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )

    def do_activate(self):
        # Force dark mode
        Adw.StyleManager.get_default().set_color_scheme(Adw.ColorScheme.FORCE_DARK)

        # Load Custom CSS
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
