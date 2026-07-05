FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install python3.10 and git
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Make python3.10 the default python3
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Set up user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:${PATH}"
WORKDIR /home/user/app

# ============================================================
# CRITICAL: Version pinning for unsloth compatibility
# ============================================================

# a. Upgrade pip first
RUN python3 -m pip install --upgrade pip setuptools wheel

# b. Install torch with CUDA 12.1 (MUST be 2.3.1 - 2.4.0 breaks unsloth_zoo)
RUN python3 -m pip install torch==2.3.1 torchvision==0.18.1 torchaudio==2.3.1 --index-url https://download.pytorch.org/whl/cu121

# c. Install transformers (MUST be 4.44.2 - 4.46+ breaks Unpack import)
RUN python3 -m pip install transformers==4.44.2

# d. Install xformers (compatible version)
RUN python3 -m pip install xformers==0.0.27

# e. Install unsloth AFTER torch and transformers
RUN python3 -m pip install unsloth

# f. Install unsloth_zoo (MUST be after unsloth)
RUN python3 -m pip install unsloth_zoo

# g. Install other required packages
RUN python3 -m pip install peft accelerate bitsandbytes datasets huggingface_hub wandb trl openai pydantic pyyaml fastapi uvicorn

# Copy application code
COPY --chown=user:user train.py .
COPY --chown=user:user aegis_training_data_500.json .

EXPOSE 7860

CMD ["python3", "-u", "train.py"]