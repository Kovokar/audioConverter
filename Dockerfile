FROM python:3.10-slim

# ---------------------------------------------------
# 1. Instalar dependências do sistema
# ---------------------------------------------------
RUN apt-get update && apt-get install -y \
    ffmpeg \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------
# 2. Criar diretório do app
# ---------------------------------------------------
WORKDIR /app

# ---------------------------------------------------
# 3. Instalar dependências Python
# ---------------------------------------------------
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# ---------------------------------------------------
# 4. Copiar o projeto Django
# ---------------------------------------------------
COPY . .

# ---------------------------------------------------
# 5. Expor porta
# ---------------------------------------------------
EXPOSE 8000

# ---------------------------------------------------
# 6. Rodar migrações e iniciar servidor
# ---------------------------------------------------
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
