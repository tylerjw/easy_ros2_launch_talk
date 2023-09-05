#!/usr/bin/env bash

inotifywait -q -m -e close_write easy-launch.py |
while read -r filename event; do
  ./easy-launch.py
done
