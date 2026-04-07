#!/bin/bash
# ─────────────────────────────────────────────
# Titan Carports + Structures America Calculator
# Double-click this file to launch on Mac
# ─────────────────────────────────────────────

# Move to the folder where this .command file lives
cd "$(dirname "$0")"

echo ""
echo "======================================================"
echo "  SA + TC Calculator  v2.4"
echo "  Starting up..."
echo "======================================================"

# Check Python 3
if ! command -v python3 &>/dev/null; then
    echo ""
    echo "ERROR: python3 not found."
    echo "Please install Python 3 from https://www.python.org"
    echo ""
    read -p "Press Enter to close..."
    exit 1
fi

# Install dependencies if needed (silent if already installed)
echo ""
echo "Checking Python dependencies..."
python3 -m pip install --quiet tornado openpyxl reportlab 2>&1 | grep -v "already satisfied" | grep -v "^$" || true

echo ""
echo "======================================================"
echo "  SA Material Takeoff:   http://localhost:8888/"
echo "  TC Construction Quote: http://localhost:8888/tc"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "======================================================"
echo ""

# Open browser after 2 seconds
(sleep 2 && open "http://localhost:8888/") &

# Start the app
python3 app.py --port 8888
