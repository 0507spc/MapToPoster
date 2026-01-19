#!/usr/bin/env bash
set -euo pipefail

# Ensure repo is present (for safety, re-clone if missing)
if [ ! -d "/home/python/app/maptoposter" ]; then
  #git clone https://github.com/originalankur/maptoposter.git /home/python/app/maptoposter
  echo "Repository not found! Exiting."
  exit 1
fi

cd /home/python/app

exec uvicorn main:app --host 0.0.0.0 --port 8000
