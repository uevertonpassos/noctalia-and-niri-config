# Frozen Oh My Zsh snapshot, with the custom Kali Neon theme.
export ZSH="$HOME/.local/share/hacker-neon/oh-my-zsh"
export ZSH_CUSTOM="$HOME/.config/oh-my-zsh/custom"
export ZSH_CACHE_DIR="$HOME/.cache/oh-my-zsh"
ZSH_THEME="hacker-neon"
plugins=(git fzf extract)

# Keep this snapshot stable; update the repository deliberately.
zstyle ':omz:update' mode disabled
DISABLE_AUTO_TITLE="true"
ENABLE_CORRECTION="false"
HISTFILE="$HOME/.zsh_history"
HISTSIZE=50000
SAVEHIST=50000
source "$ZSH/oh-my-zsh.sh"

setopt HIST_IGNORE_SPACE HIST_IGNORE_ALL_DUPS SHARE_HISTORY
typeset -U path PATH
path=("$HOME/.local/bin" "$HOME/.cargo/bin" $path)
bindkey -e

if (( $+commands[eza] )); then
    alias ls='eza --color=auto --group-directories-first --icons=auto'
    alias ll='eza -al --color=auto --group-directories-first --icons=auto'
    alias la='eza -a --color=auto --group-directories-first --icons=auto'
    alias lt='eza --tree --level=2 --color=auto --icons=auto'
fi
alias ..='cd ..'
alias ...='cd ../..'
alias c='clear'
alias monitor='btop'
alias update='sudo pacman -Syu'
alias jctl='journalctl -p 3 -xb'

ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#66856e'
source "$HOME/.local/share/hacker-neon/zsh/zsh-autosuggestions/zsh-autosuggestions.zsh"
source "$HOME/.local/share/hacker-neon/zsh/zsh-history-substring-search/zsh-history-substring-search.zsh"
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

typeset -A ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[command]='fg=#39ff14,bold'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=#39ff14'
ZSH_HIGHLIGHT_STYLES[alias]='fg=#39ff14'
ZSH_HIGHLIGHT_STYLES[function]='fg=#39ff14'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#ff6b81,bold'
ZSH_HIGHLIGHT_STYLES[path]='fg=#00e6a0,underline'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#a8ff60'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#a8ff60'
ZSH_HIGHLIGHT_STYLES[comment]='fg=#66856e'
# Syntax highlighting must be loaded after other line-editor plugins.
source "$HOME/.local/share/hacker-neon/zsh/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh"
