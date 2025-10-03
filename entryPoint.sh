#!/bin/bash

docker compose up -d
echo "Beshak Common service started successfully"
docker logs -f beshak_common