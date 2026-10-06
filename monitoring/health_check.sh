#!/bin/bash

URL="http://localhost:8080"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$URL")

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "LSFL Customer Portal: HEALTHY (HTTP $HTTP_STATUS)"
    exit 0
else
    echo "LSFL Customer Portal: UNHEALTHY (HTTP $HTTP_STATUS)"
    exit 1
fi
