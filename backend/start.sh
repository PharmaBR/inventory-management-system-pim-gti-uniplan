#!/bin/bash
cd "$(dirname "$0")"
export PYTHONPATH="$(pwd):$PYTHONPATH"
exec /Users/pharmabio/code/github_speckit/teste_speckit/.venv/bin/python -m uvicorn src.api.main:app --reload --port 8000
