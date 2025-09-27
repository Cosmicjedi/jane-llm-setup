# vLLM + Open WebUI Docker Setup

A streamlined Docker Compose setup for running vLLM with Open WebUI on your NVIDIA GPU.

## 🚀 Quick Start

1. **Prerequisites**
   - Docker and Docker Compose installed
   - NVIDIA GPU with drivers installed
   - NVIDIA Container Toolkit configured

2. **Setup and Run**
   ```bash
   # Clone or navigate to this directory
   cd llm-setup

   # Run the setup script
   ./setup.sh

   # Monitor the services (optional)
   ./monitor.sh
   ```

3. **Access the Services**
   - Open WebUI: http://localhost:3000
   - vLLM API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Configuration

Edit the `.env` file to customize your setup:

- `MODEL_NAME`: The Hugging Face model to use (default: Qwen/Qwen2.5-14B-Instruct)
- `MAX_MODEL_LEN`: Maximum context length (default: 16384)
- `GPU_MEMORY_UTILIZATION`: GPU memory usage (default: 0.90)
- `DTYPE`: Data type for model (default: auto, can be float16, float8, etc.)

## 🔧 Management Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f vllm
docker-compose logs -f open-webui

# Restart services
docker-compose restart

# Pull latest images
docker-compose pull

# Check service status
docker-compose ps
```

## 📊 Monitoring

Use the included monitoring script for real-time status:

```bash
./monitor.sh
```

Or check GPU usage directly:

```bash
nvidia-smi
```

## 🔑 API Usage

The vLLM server provides an OpenAI-compatible API. Use the API key from your `.env` file:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-vllm-api-key-here"  # From .env file
)

response = client.chat.completions.create(
    model="Qwen/Qwen2.5-14B-Instruct",
    messages=[
        {"role": "user", "content": "Hello!"}
    ]
)
print(response.choices[0].message.content)
```

## 🐛 Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA driver
nvidia-smi

# Test GPU access in Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Services Not Starting
```bash
# Check logs for errors
docker-compose logs vllm
docker-compose logs open-webui

# Ensure ports are not in use
sudo lsof -i :3000
sudo lsof -i :8000
```

### Out of Memory
- Reduce `GPU_MEMORY_UTILIZATION` in `.env`
- Use a smaller model
- Reduce `MAX_MODEL_LEN`

## 📝 Notes

- First run will download the model (~30GB for Qwen 14B)
- The setup uses FP8/auto quantization for optimal performance on RTX 4090
- Open WebUI data is persisted in `./open-webui-data`
- Models are cached in `~/.cache/huggingface`

## 🔒 Security

- API keys are auto-generated on first setup
- vLLM API is only accessible locally (127.0.0.1:8000)
- Open WebUI is accessible on all interfaces (0.0.0.0:3000) - restrict this for production
- User signup is disabled by default

## 📈 Performance Tips

For RTX 4090 (16GB VRAM):
- Qwen2.5-14B with 16K context: ~70-90 tokens/sec
- Use `--dtype float8` if supported for better performance
- Enable `--enable-prefix-caching` for repeated prompts (add to docker-compose.yml)

## 📚 Additional Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Model Options on Hugging Face](https://huggingface.co/models)