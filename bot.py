import os
import time
import telebot
import threading
from flask import Flask # Mini site para o Render nao desligar o bot

# 1. Cria o mini-site para o Health Check
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot Online!", 200

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# 2. Configurações do Bot
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

# (Aqui você cola as suas funções de edição: editar_video, etc.)

@bot.message_handler(func=lambda message: True)
def responder(message):
    if "http" in message.text:
        bot.reply_to(message, "⏳ Processando vídeo... Aguarde.")
        # ... resto do seu código de download e edição ...

# 3. Liga tudo junto
if __name__ == "__main__":
    # Liga o mini-site em uma "thread" separada
    threading.Thread(target=run_flask).start()
    
    # Liga o robô do Telegram
    print("🚀 Robô e Web Server iniciados!")
    bot.infinity_polling()
