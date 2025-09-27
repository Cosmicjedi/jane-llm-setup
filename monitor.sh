#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

clear

while true; do
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           vLLM + Open WebUI Status Monitor                  ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Show date/time
    echo -e "${YELLOW}📅 $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
    
    # GPU Status
    echo -e "${GREEN}🎮 GPU Status:${NC}"
    if command -v nvidia-smi &> /dev/null; then
        nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits | \
        while IFS=',' read -r name mem_used mem_total gpu_util temp; do
            echo "  GPU: $name"
            echo "  Memory: ${mem_used}MB / ${mem_total}MB ($(( mem_used * 100 / mem_total ))%)"
            echo "  GPU Utilization: ${gpu_util}%"
            echo "  Temperature: ${temp}°C"
        done
    else
        echo "  GPU monitoring not available"
    fi
    echo ""
    
    # Container Status
    echo -e "${GREEN}📦 Container Status:${NC}"
    docker-compose ps --format "table {{.Name}}\t{{.Status}}\t{{.State}}" 2>/dev/null | tail -n +2 | \
    while IFS=$'\t' read -r name status state; do
        if [[ $state == *"running"* ]]; then
            echo -e "  ✅ $name: ${GREEN}$status${NC}"
        else
            echo -e "  ❌ $name: ${RED}$status${NC}"
        fi
    done
    echo ""
    
    # Service Health Checks
    echo -e "${GREEN}🏥 Service Health:${NC}"
    
    # Check vLLM
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  ✅ vLLM API: ${GREEN}Healthy${NC}"
        # Get model info
        if [ -f .env ]; then
            source .env
            MODEL_INFO=$(curl -s http://localhost:8000/v1/models -H "Authorization: Bearer $VLLM_API_KEY" 2>/dev/null | grep -oP '"id":"\K[^"]*' | head -1)
            if [ ! -z "$MODEL_INFO" ]; then
                echo "     Model: $MODEL_INFO"
            fi
        fi
    else
        echo -e "  ❌ vLLM API: ${RED}Not responding${NC}"
    fi
    
    # Check Open WebUI
    if curl -s -f http://localhost:3000 > /dev/null 2>&1; then
        echo -e "  ✅ Open WebUI: ${GREEN}Accessible${NC}"
    else
        echo -e "  ❌ Open WebUI: ${RED}Not responding${NC}"
    fi
    echo ""
    
    # Resource Usage
    echo -e "${GREEN}💻 Resource Usage:${NC}"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null | tail -n +2 | \
    while IFS=$'\t' read -r container cpu mem; do
        echo "  $container:"
        echo "    CPU: $cpu"
        echo "    Memory: $mem"
    done
    echo ""
    
    # Quick Links
    echo -e "${BLUE}🔗 Quick Links:${NC}"
    echo "  Open WebUI: http://localhost:3000"
    echo "  vLLM API: http://localhost:8000/docs"
    echo ""
    
    echo -e "${YELLOW}Press Ctrl+C to exit | Refreshing in 5 seconds...${NC}"
    sleep 5
done