#!/usr/bin/env bash

if [[ -n "$SOUND_DISABLE_RHASSPY" ]]; then
  echo "RHASSPY is disabled, exiting..."
  exit 0
fi

RHASSPY_PROFILE=${RHASSPY_PROFILE:-"en"}

while [[ "$(curl --silent --head --output /dev/null --write-out '%{http_code}' --max-time 2000 'http://localhost:3000/audio')" != "200" ]]; do sleep 5; echo "Waiting for audioblock to start..."; done

echo "Starting RHASSPY plugin..."

exec rhasspy -p $RHASSPY_PROFILE