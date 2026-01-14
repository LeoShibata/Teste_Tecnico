FROM python:3.9-slim

WORKDIR /app

# Instala depêndencias do sistema para o drive do Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000