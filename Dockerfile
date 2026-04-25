FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Unsloth and training dependencies
RUN pip install --no-cache-dir \
    "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" \
    && pip install --no-cache-dir --no-deps xformers \
    && pip install --no-cache-dir \
    trl peft accelerate bitsandbytes huggingface_hub safetensors

# Copy training script and dataset
COPY train.py .
COPY aegis_training_data_500.json .

EXPOSE 7860

# -u for unbuffered stdout so logs appear in real time in HF Space console
CMD ["python", "-u", "train.py"]
