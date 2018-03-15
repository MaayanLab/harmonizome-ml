#!/usr/bin/env sh

cd /app
npm install
pip install -r app/requirements.txt

exec "$@"
