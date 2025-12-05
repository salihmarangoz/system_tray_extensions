#!/bin/bash
SCRIPT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
VENV_DIR="$SCRIPT_DIR"/ste_env/bin/activate
LOGFILE="$SCRIPT_DIR"/app.log
echo "SCRIPT_DIR=$SCRIPT_DIR"
echo "VENV_DIR=$SCRIPT_DIR"
echo "LOGFILE=$LOGFILE"

source $VENV_DIR

rm "$LOGFILE" # todo: cyclic log, maybe?

return_42_to_enter_loop() { return 42; }
return_42_to_enter_loop
while  [ "$?" -eq "42" ]
do
    python3 "$SCRIPT_DIR"/app.py
done
