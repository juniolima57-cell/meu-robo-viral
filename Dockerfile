FROM python:3.10-slim

# Instala dependências do sistema, fontes e ImageMagick
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-liberation \
    && apt-get clean

# Remove a trava de segurança do ImageMagick que impede o MoviePy de escrever textos
RUN sed -i 's/domain="path" rights="none" pattern="@\*"/domain="path" rights="read|write" pattern="@\*"/g' /etc/ImageMagick-6/policy.xml

WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
