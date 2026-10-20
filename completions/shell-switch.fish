# Fish completion for shell-switch

function __fish_shell_switch_profiles
    set -l pdir "$HOME/.config/desktop-shells"
    if test -d "$pdir"
        find "$pdir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null
    end
end

function __fish_shell_switch_rices
    echo -e "caelestia\tQuickshell dynamic colors & drawers\nhyde\tHyDE Project modular Waybar rice\ndms\tDankMaterialShell Material 3 dock\nend4\tend-4 Material You Quickshell ii\nend4-pc\tMaterial 3 Expressive Quickshell\nml4w\tML4W modular Hyprland desktop\n44dots\t44 Dots Arch Waybar & SwayNC"
end

# Commands
# Commands for both rice and shell-switch
for cmd in shell-switch rice
    complete -c $cmd -f
    complete -c $cmd -n "__fish_use_subcommand" -a list -d "List available shell profiles"
    complete -c $cmd -n "__fish_use_subcommand" -a ls -d "List available shell profiles"
    complete -c $cmd -n "__fish_use_subcommand" -a current -d "Show active shell and keybinds"
    complete -c $cmd -n "__fish_use_subcommand" -a keybinds -d "View or switch Hyprland keybinds profile"
    complete -c $cmd -n "__fish_use_subcommand" -a default -d "View or set default shell & keybinds"
    complete -c $cmd -n "__fish_use_subcommand" -a set-default -d "Set default shell & keybinds"
    complete -c $cmd -n "__fish_use_subcommand" -a launcher -d "Launch active desktop app launcher"
    complete -c $cmd -n "__fish_use_subcommand" -a sidebar -d "Toggle active desktop notification sidebar"
    complete -c $cmd -n "__fish_use_subcommand" -a get -d "Explore and install popular desktop rices"
    complete -c $cmd -n "__fish_use_subcommand" -a backup -d "Snapshot active desktop configuration"
    complete -c $cmd -n "__fish_use_subcommand" -a clone -d "Clone GitHub dotfiles repository"
    complete -c $cmd -n "__fish_use_subcommand" -a add -d "Create new shell profile template"
    complete -c $cmd -n "__fish_use_subcommand" -a remove -d "Delete installed profile"
    complete -c $cmd -n "__fish_use_subcommand" -a rm -d "Delete installed profile"
    complete -c $cmd -n "__fish_use_subcommand" -a custom -d "Open user overlay rules (~/.config/desktop-shells/user-custom.conf)"
    complete -c $cmd -n "__fish_use_subcommand" -a doctor -d "Run diagnostic health check on environment or profile"
    complete -c $cmd -n "__fish_use_subcommand" -a wallpaper -d "Set and persist wallpaper across active and future shells"
    complete -c $cmd -n "__fish_use_subcommand" -a theme -d "Set or toggle global GTK/Matugen/shell color mode"
    complete -c $cmd -n "__fish_use_subcommand" -a export -d "Export active or named shell profile to tar.gz bundle"
    complete -c $cmd -n "__fish_use_subcommand" -a gui -d "Open Libadwaita GUI app"
    complete -c $cmd -n "__fish_use_subcommand" -a menu -d "Open Rofi/Fuzzel switcher"
    complete -c $cmd -n "__fish_use_subcommand" -a help -d "Show help"

    # Dynamic Profile Completion for top-level argument
    complete -c $cmd -n "__fish_use_subcommand" -a "(__fish_shell_switch_profiles)" -d "Switch to profile"

    # Subcommand arguments
    complete -c $cmd -n "__fish_seen_subcommand_from get" -a "(__fish_shell_switch_rices)"
    complete -c $cmd -n "__fish_seen_subcommand_from keybinds" -a "(__fish_shell_switch_profiles) match default" -d "Keybinds profile"
    complete -c $cmd -n "__fish_seen_subcommand_from default set-default" -a "(__fish_shell_switch_profiles)" -d "Default profile"
    complete -c $cmd -n "__fish_seen_subcommand_from doctor" -a "(__fish_shell_switch_profiles)" -d "Profile to diagnose"
    complete -c $cmd -n "__fish_seen_subcommand_from export" -a "(__fish_shell_switch_profiles)" -d "Profile to export"
    complete -c $cmd -n "__fish_seen_subcommand_from theme" -a "dark light toggle" -d "Theme mode"
    complete -c $cmd -n "__fish_seen_subcommand_from remove rm delete" -a "(__fish_shell_switch_profiles)" -d "Profile to delete"
end


