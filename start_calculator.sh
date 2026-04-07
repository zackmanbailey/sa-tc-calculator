#!/bin/bash
echo ""
echo " ====================================================="
echo "  STRUCTURES AMERICA Material Takeoff Calculator"
echo "  Titan Carports Inc. - Conroe, TX"
echo " ====================================================="
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo " ERROR: Python 3 not found."
    echo " Install: sudo apt install python3 python3-pip"
    exit 1
fi

# Check dependencies
python3 -c "import tornado, openpyxl, reportlab" 2>/dev/null
if [ $? -ne 0 ]; then
    echo " Installing required packages..."
    pip3 install tornado openpyxl reportlab pillow --break-system-packages
    echo ""
fi

echo " Starting calculator at http://localhost:8888"
echo " Press Ctrl+C to stop."
echo ""
cd "$(dirname "$0")"
python3 app.py --port 8888
