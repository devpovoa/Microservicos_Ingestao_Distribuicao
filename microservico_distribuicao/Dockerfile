# microservico_distribuicao/Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instalar dependências do sistema necessárias ao psycopg2-binary (e outras comuns)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copiar o código do serviço (apenas o microserviço de distribuição)
COPY distrib /app/distrib

# Expor a porta padrão do Django dev server
EXPOSE 8000

# Variáveis padrão para o Django (pode ser sobrescrito pelo compose/env)
ENV DJANGO_SETTINGS_MODULE=core.settings

# Comando default: rodar o servidor de dev no container
WORKDIR /app/distrib
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
