#!/bin/sh
# Docker entrypoint for Antigravity backend.
#
# Runs as root to fix ownership on bind-mounted volumes, then drops
# privileges to appuser before exec-ing the main process.
#
# This resolves PermissionError on /app/logs, /app/artifacts, and similar
# directories that are bind-mounted from the host (where Docker may have
# created them as root).

set -e

# Fix ownership on directories that may be bind-mounted from the host.
# chown only the top-level directory so existing user files are left intact.
for dir in /app/logs /app/drop_zone /app/artifacts /app/data; do
    mkdir -p "$dir" 2>/dev/null || true
    if ! chown appuser:appuser "$dir" 2>/dev/null; then
        echo "WARNING: could not chown $dir — container may lack write permission to this directory" >&2
    fi
done

# Drop from root to appuser and exec the CMD.
exec gosu appuser "$@"
