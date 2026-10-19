#!/usr/bin/env python3
"""Restore the frozen desktop without relying on the original username."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

REPO = Path(__file__).resolve().parents[1]
PAYLOAD = REPO / 'home'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    manifest = json.loads((REPO / 'payload-manifest.json').read_text())
    actual = {p.relative_to(PAYLOAD).as_posix() for p in PAYLOAD.rglob('*')
              if p.is_file() or p.is_symlink()}
    if actual != set(manifest):
        raise RuntimeError('O conteúdo de home/ não corresponde ao manifesto.')
    for rel, entry in manifest.items():
        path = PAYLOAD / rel
        if 'symlink' in entry:
            if not path.is_symlink() or os.readlink(path) != entry['symlink']:
                raise RuntimeError('Link alterado: ' + rel)
            if not path.resolve().is_relative_to(PAYLOAD):
                raise RuntimeError('Link fora do pacote: ' + rel)
        elif path.is_symlink() or digest(path) != entry['sha256']:
            raise RuntimeError('Arquivo alterado: ' + rel)
    return manifest


def render(path, target):
    data = path.read_bytes()
    if b'@HOME@' not in data:
        return data
    if path.suffix == '.json':
        def walk(value):
            if isinstance(value, str):
                return value.replace('@HOME@', str(target))
            if isinstance(value, list):
                return [walk(item) for item in value]
            if isinstance(value, dict):
                return {key: walk(item) for key, item in value.items()}
            return value
        return (json.dumps(walk(json.loads(data)), ensure_ascii=False, indent=2) + '\n').encode()
    text = data.decode()
    replacement = str(target)
    if path.suffix in ('.kdl', '.toml', '.desktop'):
        replacement = json.dumps(replacement, ensure_ascii=False)[1:-1]
    return text.replace('@HOME@', replacement).encode()


def check_dependencies():
    missing = [cmd for cmd in ('niri', 'qs', 'alacritty', 'btop', 'zsh') if not shutil.which(cmd)]
    if missing:
        raise RuntimeError('Instale primeiro as dependências: ' + ', '.join(missing) + '\nExecute ./install-deps.sh no CachyOS.')
    modules = {'evdev': 'python-evdev', 'gi': 'python-gobject'}
    missing = [package for module, package in modules.items() if importlib.util.find_spec(module) is None]
    if missing:
        raise RuntimeError('Dependências dos atalhos ausentes: ' + ', '.join(missing) + '\nExecute ./install-deps.sh.')


def validate_niri(stage):
    result = subprocess.run(['niri', 'validate', '--config', str(stage / '.config/niri/config.kdl')],
                            text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError('Seu Niri não aceita esta configuração. Versão de referência: 26.04.\n' + result.stderr)


def ensure_local_parent(path, target):
    # Do not traverse existing dotfile symlinks into other homes or system paths.
    parent = path.parent
    while parent != target:
        if parent.is_symlink():
            raise RuntimeError('Diretório é link simbólico; mova-o antes de restaurar: ' + str(parent))
        if parent.exists() and not parent.is_dir():
            raise RuntimeError('Esperava um diretório: ' + str(parent))
        parent = parent.parent


def install(target, dry_run=False):
    manifest = verify()
    check_dependencies()
    for rel in manifest:
        dest = target / rel
        ensure_local_parent(dest, target)
        if dest.is_dir() and not dest.is_symlink():
            raise RuntimeError('Esperava um arquivo: ' + str(dest))
    with tempfile.TemporaryDirectory(prefix='hacker-neon-stage-') as scratch:
        stage = Path(scratch)
        for rel, entry in manifest.items():
            dest = stage / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            if 'symlink' in entry:
                dest.symlink_to(entry['symlink'])
            else:
                dest.write_bytes(render(PAYLOAD / rel, target))
                dest.chmod(int(entry['mode'], 8))
        validate_niri(stage)
        if dry_run:
            print(f'Validação OK: {len(manifest)} arquivos para {target}. Nada foi alterado.')
            return None
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup = target / '.local/state/hacker-neon/backups' / stamp
        ensure_local_parent(backup / 'files', target)
        backup.mkdir(parents=True, mode=0o700)
        record = {'target': str(target), 'created_at': stamp, 'files': {}}
        # Back up every destination before changing any destination.
        for rel in manifest:
            dest = target / rel
            existed = dest.exists() or dest.is_symlink()
            record['files'][rel] = {'existed': existed}
            if existed:
                saved = backup / 'files' / rel
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(dest, saved, follow_symlinks=False)
        (backup / 'restore-record.json').write_text(json.dumps(record, indent=2) + '\n')
        # Install runtime and assets before configs which trigger a live reload.
        ordering = sorted(manifest, key=lambda s: (s.endswith('settings.json'), s.endswith('shell.qml'), s.startswith('.config/niri'), s))
        for rel in ordering:
            source = stage / rel
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            # A unique temporary name avoids collisions with another installer.
            fd, temporary = tempfile.mkstemp(prefix='.' + dest.name + '.', dir=dest.parent)
            os.close(fd)
            temp = Path(temporary)
            try:
                if source.is_symlink():
                    temp.unlink()
                    temp.symlink_to(os.readlink(source))
                else:
                    shutil.copy2(source, temp)
                os.replace(temp, dest)
            finally:
                if temp.exists() or temp.is_symlink():
                    temp.unlink()
        print(f'Instalados {len(manifest)} arquivos em {target}.')
        print('Backup anterior: ' + str(backup))
        return backup


def activate(target):
    if target != Path.home().resolve():
        print('Pasta alternativa: sessão gráfica atual preservada.')
        return
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f', str(target / '.local/share/fonts/Hacker-Neon')], check=True)
    if os.environ.get('DBUS_SESSION_BUS_ADDRESS'):
        subprocess.run([str(target / '.local/bin/hacker-apply-theme')], check=True)
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        active = subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'niri.service'])
        if active.returncode == 0 and os.access('/dev/uinput', os.R_OK | os.W_OK):
            subprocess.run(['systemctl', '--user', 'restart', 'mx-master-window-scroll.service'], check=True)
    print('Entre novamente na sessão Niri para carregar todo o conjunto.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=Path.home(), help='outra pasta home, útil para teste')
    parser.add_argument('--dry-run', action='store_true', help='validar e listar o total sem escrever na home')
    parser.add_argument('--no-session', action='store_true', help='não aplicar GSettings, cache de fontes nem serviços da sessão')
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Execute como seu usuário normal, sem sudo.')
    target = args.target.expanduser().resolve()
    if target == Path('/'):
        parser.error('O destino deve ser uma pasta home.')
    if '\n' in str(target) or '\r' in str(target):
        parser.error('O caminho não pode conter quebras de linha.')
    try:
        install(target, args.dry_run)
        if not args.dry_run and not args.no_session:
            activate(target)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
