FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

COPY --chown=user:user pyproject.toml uv.lock ./
COPY --chown=user:user aegis_env/ ./aegis_env/

RUN pip install --no-cache-dir -e .

ENV SCENARIO_DIR=/home/user/app/aegis_env/data/scenarios

EXPOSE 7860

CMD ["aegis-server"]
