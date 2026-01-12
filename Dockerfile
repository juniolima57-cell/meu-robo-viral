FROM python:3.9

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia os arquivos
COPY . .

# Permissão ImageMagick (comando universal)
RUN POLICY_PATH=$(find /etc/ImageMagick-* -name policy.xml) && \
    sed -i 's/policy domain="path" rights="none" pattern="@\*"/policy domain="path" rights="read|write" pattern="@\*"/g' $POLICY_PATH

# Instala as bibliotecas
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
