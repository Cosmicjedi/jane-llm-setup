#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 vLLM + Open WebUI Setup${NC}"
echo "=================================="

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check for Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose first"
    exit 1
fi

# Check for NVIDIA GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo -e "${YELLOW}⚠️  Warning: NVIDIA driver not detected!${NC}"
    echo "Make sure you have NVIDIA drivers installed for GPU support"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for NVIDIA Container Toolkit
if ! docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
    echo -e "${RED}❌ NVIDIA Container Toolkit not configured properly!${NC}"
    echo "Please install NVIDIA Container Toolkit:"
    echo "  https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env file...${NC}"
    
    # Generate secure API keys
    VLLM_KEY=$(openssl rand -hex 32)
    WEBUI_KEY=$(openssl rand -hex 32)
    
    cat > .env <<EOF
# vLLM Configuration
MODEL_NAME=Qwen/Qwen2.5-14B-Instruct
MAX_MODEL_LEN=16384
GPU_MEMORY_UTILIZATION=0.90
DTYPE=auto

# Generated API Keys (SAVE THESE!)
VLLM_API_KEY=$VLLM_KEY
WEBUI_SECRET_KEY=$WEBUI_KEY

# Open WebUI Settings
ENABLE_SIGNUP=false
DEFAULT_USER_ROLE=pending
ENABLE_COMMUNITY_SHARING=false

# Optional: Hugging Face token for gated models
HUGGING_FACE_TOKEN=
EOF
    
    echo -e "${GREEN}✅ Created .env file with secure keys${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Save these API keys:${NC}"
    echo "  VLLM API Key: $VLLM_KEY"
    echo ""
else
    echo -e "${GREEN}✅ Using existing .env file${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p models open-webui-data

# Pull latest images
echo -e "${YELLOW}🐳 Pulling latest Docker images...${NC}"
docker-compose pull

# Start services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be ready...${NC}"
sleep 5

# Check service status
echo -e "${GREEN}📊 Service Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "📍 Access points:"
echo "  - Open WebUI: http://localhost:3000"
echo "  - vLLM API: http://localhost:8000"
echo ""
echo "📝 Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart services: docker-compose restart"
echo "  - Check GPU usage: nvidia-smi"
echo ""
echo -e "${YELLOW}Note: First run will download the model (~30GB), this may take a while.${NC}"