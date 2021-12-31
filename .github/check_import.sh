#!/bin/bash
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
VENV_DIR="$SCRIPT_DIR"/../ste_env/bin/activate
echo "SCRIPT_DIR=$SCRIPT_DIR"
echo "VENV_DIR=$SCRIPT_DIR"

source $VENV_DIR

python3 "$SCRIPT_DIR"/check_import.py
