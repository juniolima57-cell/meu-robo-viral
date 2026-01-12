FROM python:3.10-slim

# 1. Instala dependências em uma única camada para evitar erros
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && apt-get clean

# 2. COMANDO UNIVERSAL: Localiza o policy.xml (seja ImageMagick-6 ou 7) e remove a trava
RUN find /etc/ImageMagick* -name policy.xml -exec sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read|write" pattern="@\*"/g' {} +

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Porta para o Web Server do Render
EXPOSE 10000

CMD ["python", "bot.py"]
