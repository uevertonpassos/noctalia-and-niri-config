#!/usr/bin/env python3
"""Rebuild the manifest after intentionally editing home/."""
import hashlib
import json
import os
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
payload = repo / 'home'
manifest = {}
for path in sorted(payload.rglob('*')):
    if '__pycache__' in path.parts:
        raise SystemExit('Remova __pycache__ de home/ antes de atualizar o manifesto.')
    rel = path.relative_to(payload).as_posix()
    if path.is_symlink():
        if not path.resolve().is_relative_to(payload):
            raise SystemExit('Link fora do pacote: ' + rel)
        manifest[rel] = {'symlink': os.readlink(path)}
    elif path.is_file():
        manifest[rel] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                         'mode': oct(path.stat().st_mode & 0o777)}
(repo / 'payload-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print(f'Manifesto atualizado: {len(manifest)} arquivos.')
