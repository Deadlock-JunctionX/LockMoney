#!/usr/bin/env bash

set -e

alembic upgrade head
gunicorn app:app
