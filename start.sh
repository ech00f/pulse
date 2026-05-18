#!/bin/bash
cd "$(dirname "$0")"
export PORT="${PORT:-5000}"
python3 -m venv venv 2>/dev/null || true
source venv/bin/activate
pip install -q -r requirements.txt
python main.py
