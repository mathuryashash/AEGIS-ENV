FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Unsloth (no [colab-new] extra — that extra pins old PyTorch and downgrades torch)
RUN pip install --no-cache-dir \
    "unsloth @ git+https://github.com/unslothai/unsloth.git" \
    && pip install --no-cache-dir --no-deps xformers \
    && pip install --no-cache-dir \
    trl peft accelerate bitsandbytes huggingface_hub safetensors

# Force PyTorch 2.5.1+cu121 LAST — unsloth_zoo requires torch._inductor.config (PyTorch 2.4+)
# Must be after all other installs to prevent any package from downgrading it
RUN pip install --force-reinstall --no-cache-dir \
    "torch==2.5.1" "torchvision==0.20.1" "torchaudio==2.5.1" \
    --index-url https://download.pytorch.org/whl/cu121

COPY train.py .
COPY aegis_training_data_500.json .

EXPOSE 7860
CMD ["python", "-u", "train.py"]
