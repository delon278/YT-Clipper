#!/bin/bash
# YTClipper - Instalador y lanzador automático
# Compatble con Mac y Linux

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'
BOLD='\033[1m'

echo ""
echo -e "${CYAN}${BOLD}╔════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║       🎬  YTClipper            ║${NC}"
echo -e "${CYAN}${BOLD}╚════════════════════════════════╝${NC}"
echo ""

# Detect OS
OS="$(uname -s)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Check Python
echo -e "${YELLOW}Verificando dependencias...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}❌ Python3 no encontrado.${NC}"
    if [[ "$OS" == "Darwin" ]]; then
        echo "Instala Python desde https://www.python.org o con: brew install python"
    else
        echo "Instala con: sudo apt install python3 python3-pip"
    fi
    exit 1
fi
echo -e "${GREEN}✓ Python3 encontrado${NC}"

# Check/install pip dependencies
echo -e "${YELLOW}Instalando librerías Python...${NC}"
python3 -m pip install --quiet --upgrade pip 2>/dev/null || true
python3 -m pip install --quiet flask yt-dlp 2>/dev/null
echo -e "${GREEN}✓ Flask y yt-dlp instalados${NC}"

# Check ffmpeg
if ! command -v ffmpeg &>/dev/null; then
    echo -e "${YELLOW}⚠️  ffmpeg no encontrado. La función de clipear no funcionará.${NC}"
    if [[ "$OS" == "Darwin" ]]; then
        echo -e "   Instala con: ${CYAN}brew install ffmpeg${NC}"
    else
        echo -e "   Instala con: ${CYAN}sudo apt install ffmpeg${NC}"
    fi
    echo ""
else
    echo -e "${GREEN}✓ ffmpeg encontrado${NC}"
fi

echo ""
echo -e "${GREEN}${BOLD}✅ Todo listo. Iniciando YTClipper...${NC}"
echo ""
echo -e "📁 Descargas: ${CYAN}~/YTClipper/downloads/${NC}"
echo -e "✂️  Clips:     ${CYAN}~/YTClipper/clips/${NC}"
echo ""
echo -e "${BOLD}🌐 Abriendo en tu navegador: http://localhost:5050${NC}"
echo -e "   (Presiona Ctrl+C para detener)"
echo ""

# Open browser after a short delay
(sleep 2 && (
    if [[ "$OS" == "Darwin" ]]; then open "http://localhost:5050"
    elif command -v xdg-open &>/dev/null; then xdg-open "http://localhost:5050"
    fi
)) &

# Run the app
cd "$SCRIPT_DIR"
python3 app.py
