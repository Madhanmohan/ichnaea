#!/bin/bash
if [ -n "${VENV_BIN}" ]; then
    GUNICORN_BIN=${VENV_BIN}/gunicorn
else
    GUNICORN_BIN=bin/gunicorn
fi

ICHNAEA_CFG=location.ini PYRAMID_RELOAD_TEMPLATES=1 ${GUNICORN_BIN} \
    -b 127.0.0.1:7001 -w 1 -t 600 \
    -c python:ichnaea.webapp.settings ichnaea.webapp.app:wsgi_app
