"""Generate a Compose override from the host configuration (standard library only)."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = '/srv/sftp/downloads'


def build_override(config_path, local_output=False, sftp_key=None):
    service = {}
    mounts = []
    if local_output:
        config = json.loads(Path(config_path).read_text(encoding='utf-8-sig'))
        output = config.get('output_folder')
        if not isinstance(output, str) or not output.strip():
            raise ValueError('config.json debe definir output_folder como una ruta no vacía.')
        path = Path(output).expanduser()
        if not path.is_absolute():
            path = ROOT / path
        path = path.resolve()
        if not path.is_dir():
            raise ValueError(f'El directorio local no existe: {path}. Créalo antes de continuar.')
        mounts.append({'type': 'bind', 'source': str(path), 'target': TARGET,
                       'bind': {'create_host_path': False}})
    if sftp_key:
        key = Path(sftp_key).expanduser().resolve()
        if not key.is_file():
            raise ValueError(f'No existe la clave pública: {key}')
        contents = key.read_text(encoding='utf-8').strip()
        if 'PRIVATE KEY' in contents or not any(
            line.startswith(('ssh-', 'ecdsa-', 'sk-')) for line in contents.splitlines()
        ):
            raise ValueError('Usa una clave PÚBLICA OpenSSH (.pub), nunca la clave privada.')
        mounts.append({'type': 'bind', 'source': str(key),
                       'target': '/run/secrets/sftp_authorized_keys', 'read_only': True,
                       'bind': {'create_host_path': False}})
        service['environment'] = {'ENABLE_SFTP': '1'}
        service['ports'] = ['127.0.0.1:2222:22']
    if mounts:
        service['volumes'] = mounts
    return {'services': {'podcast-helper': service}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local-output', action='store_true', help='Montar output_folder de config.json.')
    parser.add_argument('--config', type=Path, default=ROOT / 'res/config.json')
    parser.add_argument('--sftp-key', type=Path, help='Clave pública autorizada para SFTP.')
    args = parser.parse_args()
    try:
        override = build_override(args.config, args.local_output, args.sftp_key)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    destination = ROOT / 'docker/compose.local.json'
    destination.write_text(json.dumps(override, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Configuración escrita en {destination}')
    print('docker compose -f docker/compose.yaml -f docker/compose.local.json up --build -d')


if __name__ == '__main__':
    main()
