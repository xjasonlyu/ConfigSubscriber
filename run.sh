#!/bin/sh

_check_status() {
    if [[ $1 -ne 0 ]]; then
        echo $2 && exit 1
    fi
}

which flask > /dev/null || _check_status $? "flask is required!"
which gunicorn > /dev/null || _check_status $? "gunicorn is required!"

# listen port
HOST="127.0.0.1"
PORT=9000
LOG_FILE="-"

# Development use only.
_debug() {
    FLASK_APP=subscribe FLASK_DEBUG=1 flask run --host $HOST --port $PORT
}

_start() {
    gunicorn -w 3 -b $HOST:$PORT --access-logfile $LOG_FILE subscribe:app
}

# case
case $1 in
    debug)
    _debug
    ;;
    *)
    _start
    ;;
esac
