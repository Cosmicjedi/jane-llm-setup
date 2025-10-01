#!/usr/bin/env python3
"""
Interactive Model Selector for jane-llm-setup
Allows switching between different LLM models dynamically
Compatible with existing vLLM + Open WebUI setup
"""

import os
import sys
import subprocess
import time
from typing import Dict, List, Optional

# Available model configurations
MODELS = {
    "1": {
        "name": "Qwen2.5-7B-Instruct",
        "model_id": "Qwen/Qwen2.5-7B-Instruct",
        "description": "Original default model - Qwen 2.5 7B",
        "max_model_len": "8192",
        "gpu_memory_utilization": "0.95"
    },
    "2": {
        "name": "Mistral-7B-Instruct-v0.3",
        "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "description": "Mistral AI 7B Instruct v0.3",
        "max_model_len": "4096",
        "gpu_memory_utilization": "0.95"
    },
    "3": {
        "name": "Mistral-7B-Instruct-v0.2",
        "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
        "description": "Mistral AI 7B Instruct v0.2",
        "max_model_len": "4096",
        "gpu_memory_utilization": "0.95"
    },
    "4": {
        "name": "Llama-3-8B-Instruct",
        "model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
        "description": "Meta Llama 3 8B Instruct",
        "max_model_len": "8192",
        "gpu_memory_utilization": "0.90"
    },
    "5": {
        "name": "Phi-3-Mini-Instruct",
        "model_id": "microsoft/Phi-3-mini-4k-instruct",
        "description": "Microsoft Phi-3 Mini 4K Instruct (lower VRAM)",
        "max_model_len": "4096",
        "gpu_memory_utilization": "0.85"
    }
}


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header():
    """Print the application header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}╔═══════════════════════════════════════════╗")
    print("║    Jane LLM Setup - Model Selector      ║")
    print(f"╚═══════════════════════════════════════════╝{Colors.ENDC}\n")


def print_models():
    """Display available models"""
    print(f"{Colors.OKBLUE}Available Models:{Colors.ENDC}\n")
    for key, model in MODELS.items():
        # Check if this is the current model
        current_model = get_current_model()
        is_current = (current_model == model['model_id'])
        marker = f" {Colors.OKGREEN}← CURRENT{Colors.ENDC}" if is_current else ""
        
        print(f"  {Colors.BOLD}[{key}]{Colors.ENDC} {model['name']}{marker}")
        print(f"      Model ID: {model['model_id']}")
        print(f"      Description: {model['description']}")
        print(f"      Max Length: {model['max_model_len']}")
        print()


def get_current_model() -> Optional[str]:
    """Get the currently configured model from .env file"""
    env_file = '.env'
    if not os.path.exists(env_file):
        return None
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('MODEL_NAME='):
                    return line.split('=', 1)[1].strip()
    except Exception:
        pass
    
    return None


def get_service_status() -> str:
    """Check if vLLM service is running"""
    try:
        result = subprocess.run(
            ['docker', 'ps', '--filter', 'name=vllm-server', '--format', '{{.Status}}'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip():
            return f"{Colors.OKGREEN}running{Colors.ENDC}"
        return f"{Colors.WARNING}stopped{Colors.ENDC}"
    except Exception:
        return f"{Colors.FAIL}unknown{Colors.ENDC}"


def stop_services():
    """Stop all running services"""
    print(f"\n{Colors.WARNING}Stopping all services...{Colors.ENDC}")
    try:
        subprocess.run(['docker-compose', 'down'], check=True)
        print(f"{Colors.OKGREEN}✓ All services stopped{Colors.ENDC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}✗ Failed to stop services: {e}{Colors.ENDC}")
        return False


def update_env_file(model_config: Dict):
    """Update .env file with the selected model configuration"""
    env_file = '.env'
    env_example = '.env.example'
    
    # Read existing .env or use .env.example as template
    env_content = []
    source_file = env_file if os.path.exists(env_file) else env_example
    
    try:
        with open(source_file, 'r') as f:
            env_content = f.readlines()
    except Exception as e:
        print(f"{Colors.FAIL}✗ Failed to read env file: {e}{Colors.ENDC}")
        return False
    
    # Update the relevant lines
    updated_content = []
    for line in env_content:
        if line.startswith('MODEL_NAME='):
            updated_content.append(f"MODEL_NAME={model_config['model_id']}\n")
        elif line.startswith('MAX_MODEL_LEN='):
            updated_content.append(f"MAX_MODEL_LEN={model_config['max_model_len']}\n")
        elif line.startswith('GPU_MEMORY_UTILIZATION='):
            updated_content.append(f"GPU_MEMORY_UTILIZATION={model_config['gpu_memory_utilization']}\n")
        else:
            updated_content.append(line)
    
    # Write updated content
    try:
        with open(env_file, 'w') as f:
            f.writelines(updated_content)
        return True
    except Exception as e:
        print(f"{Colors.FAIL}✗ Failed to update .env file: {e}{Colors.ENDC}")
        return False


def start_services(model_config: Dict):
    """Start the services with selected model"""
    print(f"\n{Colors.OKCYAN}Starting services with {model_config['name']}...{Colors.ENDC}")
    print(f"{Colors.WARNING}This may take 1-3 minutes for first startup...{Colors.ENDC}")
    
    try:
        subprocess.run(['docker-compose', 'up', '-d'], check=True)
        print(f"{Colors.OKGREEN}✓ Services started{Colors.ENDC}")
        print(f"\n{Colors.OKBLUE}Available interfaces:{Colors.ENDC}")
        print(f"  • vLLM API: http://localhost:8000")
        print(f"  • Open WebUI: http://localhost:3000")
        print(f"  • Health check: http://localhost:8000/health")
        print(f"\n{Colors.WARNING}Note: Services may take 1-2 minutes to become fully ready{Colors.ENDC}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"{Colors.FAIL}✗ Failed to start services: {e}{Colors.ENDC}")
        return False


def view_logs():
    """View logs for all services"""
    print(f"\n{Colors.OKCYAN}Viewing logs...{Colors.ENDC}")
    print(f"{Colors.WARNING}(Press Ctrl+C to exit){Colors.ENDC}\n")
    try:
        subprocess.run(['docker-compose', 'logs', '-f'])
    except KeyboardInterrupt:
        print(f"\n{Colors.OKGREEN}Exiting log viewer{Colors.ENDC}")


def check_health():
    """Check the health of vLLM service"""
    import urllib.request
    import json
    
    print(f"\n{Colors.OKCYAN}Checking service health...{Colors.ENDC}\n")
    
    try:
        # Check vLLM health
        with urllib.request.urlopen('http://localhost:8000/health', timeout=5) as response:
            print(f"{Colors.OKGREEN}✓ vLLM API: Healthy{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ vLLM API: Not responding{Colors.ENDC}")
        print(f"  Error: {e}")
    
    try:
        # Check Open WebUI
        with urllib.request.urlopen('http://localhost:3000', timeout=5) as response:
            print(f"{Colors.OKGREEN}✓ Open WebUI: Accessible{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.WARNING}⚠ Open WebUI: Not accessible (may still be starting){Colors.ENDC}")
    
    # Show Docker status
    print(f"\n{Colors.OKBLUE}Docker containers:{Colors.ENDC}")
    subprocess.run(['docker-compose', 'ps'])


def main():
    """Main interactive loop"""
    # Check if .env exists, if not create from .env.example
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        print(f"{Colors.WARNING}No .env file found. Creating from .env.example...{Colors.ENDC}")
        try:
            subprocess.run(['cp', '.env.example', '.env'], check=True)
            print(f"{Colors.OKGREEN}✓ Created .env file{Colors.ENDC}")
            print(f"{Colors.WARNING}⚠ Please edit .env and set your API keys before starting services!{Colors.ENDC}")
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}✗ Failed to create .env: {e}{Colors.ENDC}")
    
    while True:
        print_header()
        
        # Show current status
        print(f"{Colors.OKBLUE}Current Status:{Colors.ENDC}")
        current_model = get_current_model()
        if current_model:
            print(f"  Active Model: {Colors.OKGREEN}{current_model}{Colors.ENDC}")
        else:
            print(f"  Active Model: {Colors.WARNING}Not configured{Colors.ENDC}")
        print(f"  vLLM Service: {get_service_status()}")
        print()
        
        print_models()
        
        print(f"{Colors.OKBLUE}Actions:{Colors.ENDC}")
        print(f"  {Colors.BOLD}[s]{Colors.ENDC} Stop all services")
        print(f"  {Colors.BOLD}[l]{Colors.ENDC} View logs")
        print(f"  {Colors.BOLD}[r]{Colors.ENDC} Restart services")
        print(f"  {Colors.BOLD}[h]{Colors.ENDC} Check health")
        print(f"  {Colors.BOLD}[q]{Colors.ENDC} Quit\n")
        
        choice = input(f"{Colors.BOLD}Select a model or action: {Colors.ENDC}").strip().lower()
        
        if choice == 'q':
            print(f"\n{Colors.OKCYAN}Goodbye!{Colors.ENDC}\n")
            sys.exit(0)
        
        elif choice == 's':
            stop_services()
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        
        elif choice == 'l':
            view_logs()
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        
        elif choice == 'r':
            print(f"\n{Colors.WARNING}Restarting services...{Colors.ENDC}")
            subprocess.run(['docker-compose', 'restart'], check=False)
            print(f"{Colors.OKGREEN}✓ Services restarted{Colors.ENDC}")
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        
        elif choice == 'h':
            check_health()
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        
        elif choice in MODELS:
            model_config = MODELS[choice]
            
            # Check if this is already the current model
            if get_current_model() == model_config['model_id']:
                print(f"\n{Colors.WARNING}This model is already selected.{Colors.ENDC}")
                restart = input(f"{Colors.BOLD}Restart services anyway? (y/n): {Colors.ENDC}").strip().lower()
                if restart == 'y':
                    if stop_services():
                        if start_services(model_config):
                            print(f"\n{Colors.OKGREEN}✓ Services restarted{Colors.ENDC}")
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
                continue
            
            # Confirm model switch
            print(f"\n{Colors.WARNING}This will stop all services and switch to {model_config['name']}{Colors.ENDC}")
            confirm = input(f"{Colors.BOLD}Continue? (y/n): {Colors.ENDC}").strip().lower()
            
            if confirm == 'y':
                if stop_services():
                    if update_env_file(model_config):
                        print(f"{Colors.OKGREEN}✓ Configuration updated{Colors.ENDC}")
                        if start_services(model_config):
                            print(f"\n{Colors.OKGREEN}✓ Successfully switched to {model_config['name']}{Colors.ENDC}")
                        else:
                            print(f"\n{Colors.FAIL}✗ Failed to start services{Colors.ENDC}")
                    else:
                        print(f"\n{Colors.FAIL}✗ Failed to update configuration{Colors.ENDC}")
                else:
                    print(f"\n{Colors.FAIL}✗ Failed to stop existing services{Colors.ENDC}")
                
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
            else:
                print(f"\n{Colors.WARNING}Operation cancelled{Colors.ENDC}")
                input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")
        
        else:
            print(f"\n{Colors.FAIL}Invalid choice. Please try again.{Colors.ENDC}")
            input(f"\n{Colors.OKBLUE}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    # Check if docker-compose is available
    try:
        subprocess.run(['docker-compose', '--version'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{Colors.FAIL}Error: docker-compose is not installed or not in PATH{Colors.ENDC}")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not os.path.exists('docker-compose.yml'):
        print(f"{Colors.FAIL}Error: docker-compose.yml not found in current directory{Colors.ENDC}")
        print(f"{Colors.WARNING}Please run this script from the jane-llm-setup directory{Colors.ENDC}")
        sys.exit(1)
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.OKCYAN}Interrupted by user. Goodbye!{Colors.ENDC}\n")
        sys.exit(0)
