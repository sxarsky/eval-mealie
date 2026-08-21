#!/usr/bin/env bash
# Returns a Mealie bearer access token for the eval admin user.
# Polls /api/app/about until ready (mirrors target_ready_check_command), then fetches
# the token from POST /api/auth/token. Default creds from mealie/core/settings/settings.py.
set -euo pipefail
deadline=$(( $(date +%s) + 300 ))
until curl -sf http://localhost:9000/api/app/about &>/dev/null; do
  if [[ $(date +%s) -ge $deadline ]]; then
    echo "ERROR: Mealie health check timed out after 300s" >&2
    exit 1
  fi
  sleep 5
done
USER="${MEALIE_ADMIN_EMAIL:-changeme@example.com}"
PASS="${MEALIE_ADMIN_PASSWORD:-MyPassword}"
curl -sf -X POST http://localhost:9000/api/auth/token \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "username=$USER" --data-urlencode "password=$PASS" \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])"
