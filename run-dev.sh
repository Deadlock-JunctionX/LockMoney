#!/usr/bin/env bash

set -ex

alembic upgrade head
gunicorn --reload app:app
