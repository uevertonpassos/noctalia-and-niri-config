#!/usr/bin/env python3
"""Restore appearance keys only; retain existing profiles and user data."""
import argparse
import configparser
import datetime
import json
import os
from pathlib import Path
import shutil
import tempfile

REPO = Path(__file__).resolve().parents[1]


def merge(base, patch):
    for key, value in patch.items():
        if isinstance(value, dict):
            current = base.setdefault(key, {})
            if not isinstance(current, dict):
                raise ValueError('Formato inesperado em ' + key)
            merge(current, value)
        else:
            base[key] = value


def browser_changes(target):
    theme = json.loads((REPO / 'extras/browser-theme.json').read_text())
    changes = {}
    for name in ('BraveSoftware/Brave-Browser', 'chromium'):
        root = target / '.config' / name
        if os.path.lexists(root / 'SingletonLock'):
            raise RuntimeError('Feche o navegador antes de aplicar: ' + name)
        files = sorted(root.glob('*/Preferences'))
        if not files:
            print('Abra o navegador uma vez, feche e rode novamente: ' + name)
        for prefs in files:
            content = json.loads(prefs.read_text())
            patch = theme if name.startswith('Brave') else {key: value for key, value in theme.items() if key != 'brave'}
            merge(content, patch)
            changes[prefs] = json.dumps(content, separators=(',', ':')) + '\n'
    css = (REPO / 'extras/firefox-hacker-neon.css').read_text()
    found = set()
    for root in (target / '.config/mozilla/firefox', target / '.mozilla/firefox'):
        ini = root / 'profiles.ini'
        if not ini.is_file():
            continue
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ini)
        for section in parser.sections():
            if not section.startswith('Profile') or not parser.has_option(section, 'Path'):
                continue
            profile = Path(parser.get(section, 'Path'))
            if parser.getboolean(section, 'IsRelative', fallback=True):
                profile = root / profile
            profile = profile.resolve()
            if not profile.is_relative_to(target):
                raise RuntimeError('Perfil Firefox fora da home: ' + str(profile))
            if profile in found or not profile.is_dir():
                continue
            found.add(profile)
            if os.path.lexists(profile / 'lock'):
                raise RuntimeError('Feche o Firefox antes de aplicar.')
            changes[profile / 'chrome/hacker-neon.css'] = css
            chrome = profile / 'chrome/userChrome.css'
            previous = chrome.read_text() if chrome.exists() else ''
            directive = '@import url("hacker-neon.css");'
            if directive not in previous:
                changes[chrome] = directive + '\n' + previous
            js = profile / 'user.js'
            previous = js.read_text() if js.exists() else ''
            # Remove our old block before appending: latest user.js preference wins.
            line = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'
            changes[js] = previous.replace(line + '\n', '').rstrip() + '\n' + line + '\n'
    if not found:
        print('Abra o Firefox uma vez, feche e rode novamente para aplicar o CSS.')
    return changes


def apply(target):
    # Finish all profile checks before touching any file.
    changes = browser_changes(target)
    if not changes:
        return
    stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup = target / '.local/state/hacker-neon/browser-backups' / stamp
    backup.mkdir(parents=True, mode=0o700)
    for dest, text in changes.items():
        if dest.is_symlink():
            raise RuntimeError('Arquivo é link simbólico: ' + str(dest))
        if not dest.parent.resolve().is_relative_to(target):
            raise RuntimeError('Destino fora da home: ' + str(dest))
    for dest, text in changes.items():
        if dest.exists():
            saved = backup / dest.relative_to(target)
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, saved)
    for dest, text in changes.items():
        dest.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix='.' + dest.name, dir=dest.parent)
        try:
            with os.fdopen(fd, 'w') as stream:
                stream.write(text)
            if dest.exists():
                os.chmod(temporary, dest.stat().st_mode & 0o777)
            os.replace(temporary, dest)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print(f'Tema aplicado em {len(changes)} arquivos. Backup: {backup}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=Path.home())
    args = parser.parse_args()
    if os.geteuid() == 0:
        parser.error('Execute sem sudo.')
    try:
        apply(args.target.expanduser().resolve())
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, str(exc) + '\n')
