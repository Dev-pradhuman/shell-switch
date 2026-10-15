# Bash completion for shell-switch

_shell_switch_completions() {
    local cur prev words cword
    _init_completion || return

    local commands="list ls current get backup clone add remove delete rm gui menu help"
    local rices="caelestia hyde dms end4 ml4w 44dots"

    local profiles_dir="${HOME}/.config/desktop-shells"
    local profiles=""
    if [[ -d "${profiles_dir}" ]]; then
        profiles="$(find "${profiles_dir}" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null)"
    fi

    if [[ ${cword} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands} ${profiles}" -- "${cur}") )
        return 0
    fi

    case "${prev}" in
        get)
            COMPREPLY=( $(compgen -W "${rices}" -- "${cur}") )
            return 0
            ;;
        remove|rm|delete)
            COMPREPLY=( $(compgen -W "${profiles}" -- "${cur}") )
            return 0
            ;;
        clone|add|backup)
            # File or URL completion
            return 0
            ;;
        *)
            ;;
    esac
}

complete -F _shell_switch_completions shell-switch
