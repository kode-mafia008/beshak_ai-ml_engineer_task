#!/bin/bash

# docker compose up -d
uvicorn main:app --host 0.0.0.0 --port 8086 --reload
echo "Beshak Common service started successfully"
# docker logs -f beshak_common