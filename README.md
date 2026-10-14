# Noctalia + Niri — Hacker Neon

Backup restaurável do desktop de Ueverton Passos, capturado em **14/10/2026**: preto, verde neon `#39ff14`, wallpaper tech, terminal inspirado no Kali e tela de bloqueio Matrix.

Este repositório inclui o **Noctalia personalizado completo**, porque copiar somente `settings.json` não recupera as mudanças feitas no launcher, nas notificações, no menu de sessão e na tela de bloqueio.

## Restaurar após reinstalar o sistema

No **CachyOS**, entre no usuário que usará o desktop e execute:

```bash
git clone git@github.com:uevertonpassos/noctalia-and-niri-config.git
cd noctalia-and-niri-config
./install-deps.sh
./install.sh
```

Se ainda não configurou sua chave SSH no sistema novo, clone por HTTPS:

```bash
git clone https://github.com/uevertonpassos/noctalia-and-niri-config.git
```

Depois, encerre a sessão e escolha **Niri** na tela de login. Execute `./install.sh` **sem sudo**; somente a instalação dos pacotes usa sudo. O script não altera o shell de login: o Alacritty já abre o Zsh com Oh My Zsh.

O instalador adapta os caminhos para a sua home, copia as fontes e o wallpaper, valida a configuração com o Niri instalado e salva os arquivos anteriores em:

```text
~/.local/state/hacker-neon/backups/<data-hora>/
```

Para conferir antes de instalar:

```bash
./install.sh --dry-run
```

Para gerar as configurações em outra pasta sem alterar sua sessão:

```bash
./install.sh --target /tmp/minha-config-restaurada --no-session
```

Os arquivos de `home/` são modelos com o marcador `@HOME@`. Use o instalador para convertê-los em caminhos válidos; não copie os modelos diretamente sobre a home.

## O que está incluído

| Parte | Configuração |
| --- | --- |
| Noctalia | Barra superior verde, relógio monoespaçado, CPU/RAM/rede, dock desativado, menus e notificações |
| Niri | Bordas verdes, espaçamento, transparência/blur, workspaces TERM/WEB/CODE e atalhos |
| Tela de bloqueio | Chuva Matrix, cores e componentes personalizados; autenticação original preservada |
| Terminal | Alacritty, Zsh, cópia do Oh My Zsh, prompt Kali Neon e plugins de sugestões/histórico/sintaxe |
| Monitor | btop com o tema Hacker Neon |
| Ícones e cursor | Pastas verdes e cursores neon com quatro tamanhos e animação de espera |
| Fontes | MesloLGS Nerd Font e Adwaita, com suas licenças |
| Wallpaper | O mesmo PNG usado no desktop original, sem edição |
| Aplicativos | Estilos GTK/Qt e scripts para reaplicar o tema nos navegadores |

![Ícones e cursores incluídos](docs/icons-and-cursors.png)

## Atalhos principais

`Super` é a tecla Windows.

| Atalho | Ação |
| --- | --- |
| Super + T | Terminal Kali Neon |
| Super + W | Launcher do Noctalia |
| Super + B | Firefox, como na configuração original |
| Super + E | Arquivos / Nautilus |
| Super + M | Monitor btop |
| Super + F1 | Painel completo de atalhos |
| Super + L | Bloquear a tela |
| Super + Shift + Q | Menu de sessão |
| Super + 1 / 2 / 3 | TERM / WEB / CODE |
| Super + Ctrl + 1 / 2 / 3 | Mover a coluna para outra área |
| Super + O | Visão geral |

## Brave, Chromium e Firefox

Após reinstalar cada navegador, abra-o uma vez para criar o perfil e feche todas as suas janelas. Depois execute:

```bash
python3 scripts/browser-theme.py
```

O script aplica as cores escuras/verdes aos perfis locais existentes, incluindo o modo mais escuro do Brave e o CSS do Firefox. Preserva as demais preferências e cria backups em `~/.local/state/hacker-neon/browser-backups/`. Perfis com um arquivo de bloqueio são recusados; feche o navegador e tente novamente.

O repositório contém somente a aparência dos navegadores. Contas, favoritos, histórico, cookies, senhas e extensões instaladas não são exportados. Para esses dados, use a sincronização ou um backup próprio do navegador.

## Compatibilidade e fidelidade

A referência é **CachyOS com Niri 26.04 e noctalia-qs 0.0.12**, usando teclado brasileiro ABNT2. A cópia local do Noctalia identifica-se como **4.7.7**, mesmo que o pacote do sistema tenha outra versão. Essa cópia é instalada em `~/.config/quickshell/noctalia-shell` e tem prioridade sobre o Noctalia do sistema.

As versões detectadas estão em [versions.json](versions.json). O instalador de dependências usa os pacotes disponíveis nos repositórios do CachyOS; ele não congela nem rebaixa o sistema. O runtime, drivers, escala e resolução podem mudar a aparência. Para obter a maior fidelidade, use as versões de referência e a mesma escala. O instalador recusa configurações que o Niri instalado não consiga analisar.

O wallpaper tem um padrão global, então também aparece se o monitor tiver um nome diferente de `eDP-1`. A resolução não é fixada; ajuste `~/.config/niri/cfg/display.kdl` quando necessário. Em outra distribuição, o logotipo da barra acompanha a distribuição.

As fontes, o código personalizado e os assets ficam no repositório, sem depender de downloads futuros desses temas. O plugin Polkit do Noctalia é o único agente iniciado pelo pacote restaurado; o autostart redundante do agente GNOME foi retirado para evitar conflito.

Atualizar manualmente a cópia local do Noctalia pode substituir as personalizações. Mantenha este repositório como referência antes de atualizar.

## Onde editar

| Arquivos | Finalidade |
| --- | --- |
| `home/.config/noctalia/settings.json` | Barra, menus e comportamento |
| `home/.config/noctalia/colors.json` | Paleta ativa |
| `home/.config/noctalia/colorschemes/Noite Serena/` | Paleta persistente |
| `home/.config/quickshell/noctalia-shell/` | Código completo do Noctalia personalizado |
| `home/.config/niri/` | Compositor, atalhos e workspaces |
| `home/.config/alacritty/` e `home/.zshrc` | Terminal e shell |
| `home/.config/oh-my-zsh/custom/themes/` | Prompt Kali Neon |
| `home/.local/share/icons/` | Ícones e cursores |
| `extras/` | Preferências de aparência dos navegadores |

O manifesto SHA-256 detecta arquivos ausentes ou modificados. Depois de editar intencionalmente o conteúdo de `home/`, atualize-o e teste:

```bash
python3 scripts/update-manifest.py
python3 -m unittest discover -s tests -v
./install.sh --dry-run
```

Para recuperar um arquivo anterior, copie-o de `backups/<data-hora>/files/` para o mesmo caminho relativo na sua home. `restore-record.json` informa quais arquivos existiam antes da restauração.

## Créditos

Consulte [THIRD_PARTY.md](THIRD_PARTY.md). As licenças dos componentes redistribuídos acompanham suas cópias. O wallpaper foi preservado do arquivo local escolhido pelo usuário; este repositório não declara autoria sobre ele.
