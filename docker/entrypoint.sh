#!/bin/sh
set -eu
mkdir -p /run/sshd /run/podcast-supervisor /var/lib/podcast-ssh
# Do not recursively chown a host library. A bind mount must already be writable.
if ! gosu podcast test -w /app/output; then
    echo "Output directory is not writable by podcast. Set PODCAST_UID/PODCAST_GID build args to the host owner or adjust the directory permissions." >&2
    exit 1
fi
if [ "${ENABLE_SFTP:-0}" = "1" ]; then
    test -s /run/secrets/sftp_authorized_keys || {
        echo "SFTP requires a public key at /run/secrets/sftp_authorized_keys" >&2
        exit 1
    }
    install -m 600 /run/secrets/sftp_authorized_keys /etc/ssh/podcast_authorized_keys
    # Unlock the account for public-key authentication; passwords are disabled.
    usermod -p '*' podcast
    if [ ! -f /var/lib/podcast-ssh/ssh_host_ed25519_key ]; then
        ssh-keygen -q -t ed25519 -N '' -f /var/lib/podcast-ssh/ssh_host_ed25519_key
    fi
    /usr/sbin/sshd -t
    cat > /run/podcast-supervisor/sftp.conf <<'EOF'
[program:sftp]
command=/usr/sbin/sshd -D -e
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
EOF
else
    rm -f /run/podcast-supervisor/sftp.conf
fi
exec /usr/bin/supervisord -c /etc/supervisor/podcast.conf
