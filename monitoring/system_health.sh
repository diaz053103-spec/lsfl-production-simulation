#!/bin/bash

LOG_DIR="$(dirname "$0")/logs"
LOG_FILE="$LOG_DIR/system-health.log"

mkdir -p "$LOG_DIR"

{
echo "========================================"
echo " LSFL PRODUCTION HEALTH CHECK"
echo " $(date)"
echo "========================================"
echo ""

echo "[1] Customer Portal"

HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)

if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "STATUS: HEALTHY"
    echo "HTTP:   $HTTP_STATUS"
else
    echo "STATUS: UNHEALTHY"
    echo "HTTP:   $HTTP_STATUS"
fi

echo ""
echo "[2] Docker Container"

CONTAINER_STATUS=$(docker inspect --format='{{.State.Status}}' lsfl-customer-portal 2>/dev/null)

if [ "$CONTAINER_STATUS" = "running" ]; then
    echo "STATUS: RUNNING"
else
    echo "STATUS: $CONTAINER_STATUS"
fi

echo ""
echo "[3] Container Health"

HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' lsfl-customer-portal 2>/dev/null)

echo "HEALTH: $HEALTH_STATUS"

echo ""
echo "[4] Host Uptime"

uptime

echo ""
echo "[5] Disk Usage"

df -h /

echo ""
echo "========================================"
echo " Monitoring check completed"
echo "========================================"
echo ""

} | tee -a "$LOG_FILE"
