#!/bin/bash
# Simple wrapper script to run the stock analyzer

cd "$(dirname "$0")"
python main.py "$@"
