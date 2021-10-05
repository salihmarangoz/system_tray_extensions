#!/bin/bash
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
echo "SCRIPT_DIR=$SCRIPT_DIR"
source "$SCRIPT_DIR"/ste_env/bin/activate
python3 "$SCRIPT_DIR"/app.py # | tee "$SCRIPT_DIR"/app.log


