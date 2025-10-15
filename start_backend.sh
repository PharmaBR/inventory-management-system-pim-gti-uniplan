#!/bin/bash
cd backend
source venv/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
uvicorn src.api.main:app --host 127.0.0.1 --port 8000 --reload
