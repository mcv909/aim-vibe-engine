#!/bin/bash
# AIM Tunnel-Wächter

echo "Starte SSH-Tunnel zu Hetzner..."
while true; do
    # Prüft, ob der Tunnel auf Port 5432 schon belegt ist
    if ! lsof -Pi :5432 -sTCP:LISTEN -t >/dev/null ; then
        echo "Tunnel down - baue neu auf..."
        ssh -N -L 5432:localhost:5432 root@91.98.23.22 &
    fi
    sleep 30
done