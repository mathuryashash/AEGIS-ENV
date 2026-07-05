FROM python:3.10-slim
WORKDIR /app
RUN pip install --no-cache-dir openenv-core fastapi uvicorn pydantic
COPY . .
CMD ["python", "-m", "aegis_env.server"]