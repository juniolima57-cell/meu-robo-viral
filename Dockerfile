FROM python:3.10-slim

# Instala ferramentas de vídeo, imagem e fontes do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-dejavu-core \
    && apt-get clean

# COMANDO CRUCIAL: Remove a trava de segurança do ImageMagick para permitir escrita de texto
RUN sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

# Porta usada pelo Flask para o Render não matar o bot
EXPOSE 10000

CMD ["python", "bot.py"]
