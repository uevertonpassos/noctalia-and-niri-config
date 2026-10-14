# Kali-inspired neon prompt: real user, host, directory, Git and exit status.
setopt PROMPT_SUBST
ZSH_THEME_GIT_PROMPT_PREFIX='%F{#8cad94}-[git:'
ZSH_THEME_GIT_PROMPT_SUFFIX='%F{#8cad94}]%f'
ZSH_THEME_GIT_PROMPT_CLEAN='%F{#00e676}'
ZSH_THEME_GIT_PROMPT_DIRTY='%F{#e5e875}*'
PROMPT=$'%F{#39ff14}┌──(%(!.%F{#ff6b81}.%F{#c7f7cf})%n㉿%m%F{#39ff14})-[%F{#00e676}%~%F{#39ff14}]%f$(git_prompt_info)\n%F{#39ff14}└─%(?.%F{#39ff14}.%F{#ff6b81})%(!.#.$)%f '
RPROMPT='%(?..%F{#ff6b81}exit:%? %f)%F{#66856e}%D{%H:%M}%f'
