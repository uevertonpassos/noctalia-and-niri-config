#!/usr/bin/env python3
"""Read-only keyboard reference, matching the local Niri bindings."""
import curses

GROUPS = [
 ('01 // APLICATIVOS',[
  ('Super + T','Terminal na pasta selecionada / sob o mouse'),('Super + W','Buscar aplicativos'),
  ('Super + B','Firefox'),('Super + E','Arquivos'),('Super + M','Monitor de sistema'),
  ('Super + F1','Este painel de atalhos'),('Super + L','Bloquear a tela'),
  ('Super + Shift + Q','Menu de sessão')]),
 ('02 // JANELAS',[
  ('Super + setas','Mudar o foco'),('Super + Ctrl + setas','Mover janelas / colunas'),
  ('Super + Q','Fechar janela'),('Super + F','Tela cheia'),
  ('Super + Ctrl + F','Expandir coluna'),('Super + C','Centralizar coluna'),
  ('Super + - / =','Diminuir / aumentar largura'),('Super + Shift + - / =','Diminuir / aumentar altura'),
  ('Super + Shift + T','Alternar janela flutuante'),('Super + Shift + W','Alternar coluna com abas'),
  ('Super + O','Visão geral')]),
 ('03 // ÁREAS DE TRABALHO',[
  ('Super + 1 / 2 / 3','TERM / WEB / CODE'),('Super + 4 … 9','Ir à área numerada'),
  ('Super + Ctrl + 1 … 9','Enviar coluna para outra área'),('Super + Tab','Voltar à área anterior'),
  ('Super + roda do mouse','Trocar área de trabalho'),
  ('Super + Shift + setas','Focar outro monitor'),
  ('Super + Ctrl + Shift + setas','Mover coluna para outro monitor')]),
 ('04 // CAPTURAS E SISTEMA',[
  ('Ctrl + Shift + 1','Capturar seleção'),('Ctrl + Shift + 2','Capturar tela'),
  ('Ctrl + Shift + 3','Capturar janela'),('Super + Shift + P','Apagar os monitores'),
  ('Super + Escape','Alternar bloqueio de atalhos por apps'),
  ('Super + Shift + Escape','Painel nativo de atalhos'),
  ('Ctrl + Alt + Delete','Diálogo para sair do Niri')]),
 ('05 // MX MASTER 3S',[
  ('Roda lateral','Janela à esquerda / direita'),
  ('Botão traseiro / dianteiro','Desktop anterior / próximo'),
  ('Botão da base do polegar','Codex na pasta selecionada / atual')]),
]

def main(screen):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,10 if curses.COLORS>=16 else curses.COLOR_GREEN,-1)
    curses.init_pair(2,7,-1)
    curses.init_pair(3,8 if curses.COLORS>=16 else curses.COLOR_GREEN,-1)
    screen.keypad(True)
    rows=[]
    for title,items in GROUPS:
        rows.extend([(title,'',True)]+[(k,v,False) for k,v in items]+[('','',False)])
    offset=0
    def write(y,x,text,pair=2,bold=False):
        height,width=screen.getmaxyx()
        if 0<=y<height and 0<=x<width-1:
            screen.addnstr(y,x,text,max(0,width-x-1),curses.color_pair(pair)|(curses.A_BOLD if bold else 0))
    while True:
        screen.erase();h,w=screen.getmaxyx();page=max(1,h-9)
        offset=max(0,min(offset,max(0,len(rows)-page)))
        write(1,3,'>_ ATALHOS // NIRI',1,True)
        write(2,3,'Super = tecla Windows  •  Referência do seu desktop',3)
        write(3,3,'─'*max(0,w-7),1)
        split=min(39,max(22,w//2))
        for i,(key,description,header) in enumerate(rows[offset:offset+page]):
            y=5+i
            if header:write(y,3,key,1,True)
            else:
                write(y,4,key[:split-5],1)
                write(y,split,description,2)
        write(h-3,3,'─'*max(0,w-7),3)
        write(h-2,3,'↑ ↓ / j k rolar   PgUp PgDn página   Esc / q fechar',3)
        if w>76:write(h-2,w-14,f'{offset+1:02d}/{len(rows):02d}',1)
        screen.refresh();key=screen.getch()
        if key in (27,ord('q'),ord('Q')):break
        if key in (curses.KEY_DOWN,ord('j')):offset+=1
        if key in (curses.KEY_UP,ord('k')):offset-=1
        if key in (curses.KEY_NPAGE,ord(' ')):offset+=page
        if key==curses.KEY_PPAGE:offset-=page
        if key==curses.KEY_HOME:offset=0
        if key==curses.KEY_END:offset=len(rows)

if __name__=='__main__':
    try:curses.wrapper(main)
    except KeyboardInterrupt:pass
