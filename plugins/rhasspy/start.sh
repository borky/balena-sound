#!/usr/bin/env bash

if [[ -n "$SOUND_DISABLE_RHASSPY" ]]; then
  echo "RHASSPY is disabled, exiting..."
  exit 0
fi

RHASSPY_PROFILE=${RHASSPY_PROFILE:-"en"}

while [[ "$(curl --silent --head --output /dev/null --write-out '%{http_code}' --max-time 2000 'http://localhost:3000/audio')" != "200" ]]; do sleep 5; echo "Waiting for audioblock to start..."; done


if [[ -n "$RESPEAKER_LED_CONTROL_ENABLED" ]]; then
  echo "Starting RHASSPY plugin..."
  exec rhasspy -p $RHASSPY_PROFILE >/dev/null &

  while [[ "$(python3 -m rhasspyclient version)" == "" ]]; do sleep 10; echo "Waiting for rhasspy to start..."; done

  echo "Starting pixel ring control..."
  exec python3 /usr/src/pixel_ring_control.py
else
  echo "Starting RHASSPY plugin..."
  exec rhasspy -p $RHASSPY_PROFILE >/dev/null
fi