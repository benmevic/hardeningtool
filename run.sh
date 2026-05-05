#!/bin/bash

echo "╔══════════════════════════════════════════╗"
echo "║   BlueTeam Hardener - Kurulum Scripti   ║"
echo "╚══════════════════════════════════════════╝"

echo "[*] Bağımlılıklar kuruluyor..."
pip3 install -r requirements.txt

echo "[*] Kurulum tamamlandı."
echo "[*] Sunucu başlatılıyor: http://0.0.0.0:5000"
echo "[!] Ctrl+C ile durdurun"
echo ""

python3 app.py
