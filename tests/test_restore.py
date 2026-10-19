import importlib.util
import json
import os
import runpy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


restore = load('restore', 'restore.py')
browsers = load('browsers', 'browser-theme.py')


class RestoreTests(unittest.TestCase):
    def test_full_restore_portable_paths_and_backups(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'another user'
            old = target / '.config/niri/config.kdl'
            old.parent.mkdir(parents=True)
            old.write_text('// original configuration\n')
            unrelated = target / '.config/unrelated-app/settings'
            unrelated.parent.mkdir(parents=True)
            unrelated.write_text('keep me')
            backup = restore.install(target)
            self.assertEqual((backup / 'files/.config/niri/config.kdl').read_text(), '// original configuration\n')
            self.assertEqual(unrelated.read_text(), 'keep me')
            settings = json.loads((target / '.config/noctalia/settings.json').read_text())
            self.assertEqual(settings['wallpaper']['directory'], str(target / 'Pictures/Wallpapers/Hacker-Neon'))
            cache = json.loads((target / '.cache/noctalia/wallpapers.json').read_text())
            self.assertTrue(Path(cache['defaultWallpaper']).is_file())
            self.assertEqual((target / '.local/share/icons/Hacker-Neon-Cursors/cursors/left_ptr').resolve().name, 'default')
            self.assertTrue(os.access(target / '.local/bin/hacker-shortcuts', os.X_OK))
            self.assertIn(str(target), (target / '.config/niri/cfg/keybinds.kdl').read_text())
            self.assertEqual(settings['idle']['suspendTimeout'], 0)
            self.assertEqual(settings['idle']['screenOffTimeout'], 600)
            self.assertEqual(settings['idle']['lockTimeout'], 660)
            service = target / '.config/systemd/user/mx-master-window-scroll.service'
            enabled = target / '.config/systemd/user/graphical-session.target.wants/mx-master-window-scroll.service'
            self.assertEqual(enabled.resolve(), service)
            self.assertIn('"%h/.local/bin/mx-master-window-scroll.py"', service.read_text())
            for name in ('Abrir no Codex', 'Abrir terminal aqui'):
                script = target / '.local/share/nautilus/scripts' / name
                self.assertTrue(os.access(script, os.X_OK))
                self.assertIn('"$HOME/.local/bin/', script.read_text())
            with patch.object(Path, 'home', return_value=target):
                codex = runpy.run_path(str(target / '.local/bin/codex-mouse-launcher.py'))
                terminal = runpy.run_path(str(target / '.local/bin/terminal-context-launcher.py'))
            project = target / 'projeto com espaços ç $()'
            project.mkdir()
            env = {'NAUTILUS_SCRIPT_SELECTED_URIS': project.as_uri(),
                   'NAUTILUS_SCRIPT_CURRENT_URI': target.as_uri()}
            self.assertEqual(codex['nautilus_directory'](env), project)
            self.assertEqual(terminal['HELPERS']['nautilus_directory'](env), project)
            with patch('shutil.which', return_value='/usr/bin/codex'):
                command = codex['terminal_command'](project)
            self.assertEqual(command[-4:], ['-e', '/usr/bin/codex', '--cd', str(project)])
            with patch('shutil.which', return_value=None):
                with self.assertRaisesRegex(ValueError, 'Instale o Codex'):
                    codex['terminal_command'](project)
            with patch('subprocess.Popen') as popen:
                terminal['launch'](project)
                self.assertEqual(popen.call_args.args[0], ['/usr/bin/alacritty', '--working-directory', str(project)])
            for path in target.rglob('*'):
                if path.is_file() and not path.is_symlink() and 'backups' not in path.parts:
                    data = path.read_bytes()
                    self.assertNotIn(b'@HOME@', data, str(path))
                    self.assertNotIn(b'/home/uev/', data, str(path))
            again = restore.install(target)
            self.assertNotEqual(backup, again)
            self.assertEqual((again / 'files/.config/niri/config.kdl').read_bytes(), old.read_bytes())

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'new-home'
            restore.install(target, dry_run=True)
            self.assertFalse(target.exists())

    def test_reject_external_directory_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'home'
            outside = Path(temp) / 'outside'
            target.mkdir(); outside.mkdir()
            (target / '.config').symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, 'link simbólico'):
                restore.install(target)
            self.assertEqual(list(outside.iterdir()), [])

    def test_browser_merge_keeps_profile_data(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp)
            root = target / '.config/BraveSoftware/Brave-Browser'
            prefs = root / 'Default/Preferences'
            prefs.parent.mkdir(parents=True)
            original = {'profile': {'name': 'Test'}, 'session': {'restore_on_startup': 1},
                        'extensions': {'settings': {'example': {'enabled': True}}}}
            prefs.write_text(json.dumps(original));prefs.chmod(0o600)
            ff = target / '.mozilla/firefox'
            profile = ff / 'sample.default'
            (profile / 'chrome').mkdir(parents=True)
            (ff / 'profiles.ini').write_text('[Profile0]\nPath=sample.default\nIsRelative=1\n')
            (profile / 'chrome/userChrome.css').write_text('/* existing CSS */\n')
            (profile / 'user.js').write_text('user_pref("example.preference", 42);\n')
            browsers.apply(target)
            content = json.loads(prefs.read_text())
            self.assertEqual(content['profile'], original['profile'])
            self.assertEqual(content['session'], original['session'])
            self.assertEqual(content['extensions']['settings'], original['extensions']['settings'])
            self.assertTrue(content['brave']['darker_mode'])
            self.assertEqual(prefs.stat().st_mode & 0o777, 0o600)
            browsers.apply(target)
            self.assertEqual((profile / 'chrome/userChrome.css').read_text().count('@import'), 1)
            self.assertEqual((profile / 'user.js').read_text().count('toolkit.legacy'), 1)
            self.assertIn('example.preference', (profile / 'user.js').read_text())
            before = prefs.read_bytes()
            (root / 'SingletonLock').symlink_to('host-123')
            with self.assertRaisesRegex(RuntimeError, 'Feche'):
                browsers.apply(target)
            self.assertEqual(before, prefs.read_bytes())


if __name__ == '__main__':
    unittest.main()
