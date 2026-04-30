#!/bin/sh
set -e

if [ ! -f /app/conversation.json ]; then
    echo '{}' > /app/conversation.json
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
