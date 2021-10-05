#!/bin/bash
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
source "$SCRIPT_DIR"/ste_env/bin/activate
python3 "$SCRIPT_DIR"/app.py # | tee "$SCRIPT_DIR"/app.log


