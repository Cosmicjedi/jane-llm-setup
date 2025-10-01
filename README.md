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
   cd jane-llm-setup

   # Run the setup script
   ./setup.sh

   # Monitor the services (optional)
   ./monitor.sh
   ```

3. **Interactive Model Selector (NEW!)** ⭐
   ```bash
   # Launch the interactive model selector
   ./select_model.py
   ```
   
   Features:
   - 🎯 Easy switching between multiple LLM models
   - 🎨 Beautiful color-coded terminal UI
   - 📊 Real-time service status monitoring
   - 📝 Integrated log viewer
   - 🔄 Quick restart and health checks
   
   Supported Models:
   - Qwen2.5-7B-Instruct (default)
   - Mistral-7B-Instruct-v0.3
   - Mistral-7B-Instruct-v0.2
   - Llama-3-8B-Instruct
   - Phi-3-Mini-Instruct

4. **Access the Services**
   - Open WebUI: http://localhost:3000 (or http://your-server-ip:3000)
   - vLLM API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Configuration

Edit the `.env` file to customize your setup:

### Model Selection by GPU VRAM:
- **16GB VRAM** (RTX 4090, A4000): Use 7B models
  - `MODEL_NAME=Qwen/Qwen2.5-7B-Instruct`
  - `MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.3`
  - `MODEL_NAME=meta-llama/Llama-3.2-8B-Instruct` (requires HF token)

- **24GB VRAM** (RTX 3090/4090, A5000): Can use 13B models
  - `MODEL_NAME=Qwen/Qwen2.5-14B-Instruct`
  - `MODEL_NAME=meta-llama/Llama-3.2-13B-Instruct`

### Other Settings:
- `MAX_MODEL_LEN`: Maximum context length (default: 8192)
- `GPU_MEMORY_UTILIZATION`: GPU memory usage (default: 0.95)
- `DTYPE`: Data type for model (default: auto, can be float16, bfloat16)

## 🎯 Interactive Model Selector

The included `select_model.py` script provides an easy way to switch between different LLM models:

### Usage

```bash
./select_model.py
```

### Features

- **[1-5]**: Select from 5 pre-configured models
- **[s]**: Stop all services
- **[l]**: View logs in real-time
- **[r]**: Restart services
- **[h]**: Check health status
- **[q]**: Quit

### How It Works

The selector:
1. Updates your `.env` file with the chosen model
2. Stops running containers gracefully
3. Restarts services with the new model
4. Shows real-time status and endpoints

### Model Options

| # | Model | VRAM | Context | Description |
|---|-------|------|---------|-------------|
| 1 | Qwen2.5-7B-Instruct | ~14GB | 8K | Default - Excellent general purpose |
| 2 | Mistral-7B-Instruct-v0.3 | ~14GB | 4K | Strong reasoning capabilities |
| 3 | Mistral-7B-Instruct-v0.2 | ~14GB | 4K | Previous Mistral version |
| 4 | Llama-3-8B-Instruct | ~16GB | 8K | Meta's latest (requires HF token) |
| 5 | Phi-3-Mini-Instruct | ~8GB | 4K | Lower VRAM option |

### Example Workflow

```bash
# Start the selector
./select_model.py

# Choose option [2] for Mistral
# Confirm with 'y'
# Wait ~2 minutes for model to load

# Press [h] to check health
# Press [l] to view logs
# Press [q] to exit

# Open WebUI will now use the new model!
```

## 🔧 Management Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f vllm
docker compose logs -f open-webui

# Restart services
docker compose restart

# Pull latest images
docker compose pull

# Check service status
docker compose ps
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
    model="Qwen/Qwen2.5-7B-Instruct",
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
docker compose logs vllm
docker compose logs open-webui

# Ensure ports are not in use
sudo lsof -i :3000
sudo lsof -i :8000
```

### Out of Memory
- Reduce `GPU_MEMORY_UTILIZATION` in `.env`
- Use a smaller model (7B instead of 14B)
- Reduce `MAX_MODEL_LEN`
- Enable quantization: set `DTYPE=float8` or `DTYPE=int8`

### Docker Compose Command Not Found
If you get `docker-compose: command not found`, the script will automatically try `docker compose` (without hyphen) which is the newer version.

## 📝 Notes

- First run will download the model (~15GB for 7B models, ~30GB for 14B models)
- The setup uses automatic quantization for optimal performance
- Open WebUI data is persisted in `./open-webui-data`
- Models are cached in `~/.cache/huggingface`

## 🔒 Security

- API keys are auto-generated on first setup
- vLLM API is only accessible locally (127.0.0.1:8000)
- Open WebUI is accessible on all interfaces (0.0.0.0:3000) - restrict this for production
- User signup is disabled by default

## 📈 Performance Tips

For RTX 4090 (16GB VRAM):
- Qwen2.5-7B with 8K context: ~100-150 tokens/sec
- Use `--dtype bfloat16` for better performance
- Enable `--enable-prefix-caching` for repeated prompts (add to docker-compose.yml)

For memory optimization:
- The setup includes `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` to prevent fragmentation
- Monitor GPU memory with `nvidia-smi -l 1`

## 📚 Additional Resources

- [vLLM Documentation](https://docs.vllm.ai/)
- [Open WebUI Documentation](https://docs.openwebui.com/)
- [Model Options on Hugging Face](https://huggingface.co/models)