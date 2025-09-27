# LLM Setup - vLLM + Open WebUI

Production-ready Docker Compose setup for running local LLMs with vLLM and Open WebUI.

## Features

- **vLLM** for high-performance inference with FP8 quantization
- **Open WebUI** for user-friendly interface
- **Nginx** reverse proxy with SSL/TLS
- **Security hardening** with rate limiting and API authentication
- **Optional Cloudflare Tunnel** for zero-trust access
- Optimized for **RTX 4090** with FP8 tensor cores

## System Requirements

- Ubuntu 22.04/24.04 LTS (recommended)
- NVIDIA GPU with FP8 support (RTX 4090 or similar)
- 32GB+ system RAM
- Docker with NVIDIA Container Toolkit
- 50GB+ free disk space

## Quick Start

### 1. Prerequisites

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt update && sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Setup

```bash
# Clone the repository
git clone https://github.com/Cosmicjedi/llm-setup.git
cd llm-setup

# Run setup script with your domain
chmod +x setup.sh
./setup.sh your-domain.com

# Pull Docker images
docker-compose pull
```

### 3. Configuration

Edit `.env` file to customize:
- Model selection (default: Qwen/Qwen2.5-14B-Instruct)
- API keys
- Hugging Face token (for gated models)
- WebUI settings

### 4. Deploy

```bash
# Production deployment with SSL
docker-compose up -d

# Development mode (with local ports exposed)
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# With Cloudflare Tunnel (most secure)
docker-compose --profile cloudflare up -d
```

## Available Models

Optimized for FP8 quantization on RTX 4090:

| Model | VRAM Usage | Speed | Context |
|-------|------------|-------|----------|
| Qwen2.5-14B-Instruct | ~14GB | 70-90 t/s | 16K |
| Llama-3.2-11B-Vision | ~11GB | 80-100 t/s | 128K |
| Mistral-Small-22B | ~16GB | 50-65 t/s | 32K |

## Security Features

- ✅ API key authentication
- ✅ Rate limiting (nginx)
- ✅ SSL/TLS encryption
- ✅ Network isolation
- ✅ Security headers
- ✅ User signup disabled by default
- ✅ Optional Cloudflare Tunnel

## Monitoring

```bash
# View logs
docker-compose logs -f vllm
docker-compose logs -f open-webui

# Monitor GPU usage
watch -n 1 nvidia-smi

# Check service health
curl http://localhost:8000/health
```

## SSL Certificate Renewal

Add to crontab for automatic renewal:
```bash
0 0 * * 0 certbot renew --quiet && docker-compose restart nginx
```

## Troubleshooting

### GPU not detected
```bash
# Verify NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi
```

### Out of memory
- Reduce `--max-model-len` in docker-compose.yml
- Lower `--gpu-memory-utilization` to 0.9
- Use smaller model or stronger quantization

### Performance issues
- Ensure GPU is in maximum performance mode
- Check thermal throttling with `nvidia-smi`
- Verify FP8 is being used (check vLLM logs)

## Advanced Configuration

### Custom Models

Edit vLLM command in docker-compose.yml:
```yaml
command: >
  --model your-model/name
  --dtype float8  # or auto, float16, bfloat16
  --max-model-len 8192
  # Add more vLLM options as needed
```

### Firewall Setup

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

## Contributing

Feel free to open issues or submit PRs for improvements!

## License

MIT
