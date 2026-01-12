import os
import time
import telebot
from telebot import apihelper # Importante para o truque do IP
import yt_dlp
import whisper
import moviepy.video.fx.all as vfx
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

# --- TRUQUE PARA PULAR O ERRO DE REDE ---
# Forçamos o bot a falar com o IP oficial do Telegram, pulando o erro de DNS
apihelper.API_URL = "https://149.154.167.220/bot{0}/{1}"

TOKEN = os.environ.get('TELEGRAM_TOKEN')

def iniciar_bot():
    while True:
        try:
            if not TOKEN:
                print("❌ Erro: Configure o TELEGRAM_TOKEN nas Secrets!")
                time.sleep(60)
                continue
            
            bot = telebot.TeleBot(TOKEN)
            # Testa a conexão básica
            user = bot.get_me()
            print(f"🚀 SUCESSO! Robo online: @{user.username}")
            return bot
        except Exception as e:
            print(f"⚠️ Tentando conectar... (Erro: {e})")
            time.sleep(10)

bot = iniciar_bot()

# Carrega a IA
print("🧠 Carregando IA Whisper...")
model = whisper.load_model("base")

# --- FUNÇÃO DE EDIÇÃO VIRAL ---
def editar_video(input_path, output_path):
    clip = VideoFileClip(input_path)
    
    # Anti-bloqueio
    clip = clip.fx(vfx.mirror_x)
    clip = clip.fx(vfx.speedx, 1.05)

    # Titulo Amarelo
    barra = ColorClip(size=(clip.w, int(clip.h*0.12)), color=(255, 255, 0)).set_duration(clip.duration).set_position(('center', 'top'))
    txt_t = TextClip("ACHADINHO UTIL! ✨", fontsize=45, color='black', font='Arial-Bold', method='caption', size=(clip.w*0.9, None)).set_duration(clip.duration).set_position(('center', int(clip.h*0.02)))

    # Legendas com IA
    res = model.transcribe(input_path)
    subs = []
    for s in res['segments']:
        cap = TextClip(s['text'].upper(), fontsize=30, color='white', stroke_color='black', stroke_width=1, font='Arial-Bold', method='caption', size=(clip.w*0.8, None)).set_start(s['start']).set_end(s['end']).set_position(('center', int(clip.h*0.8)))
        subs.append(cap)

    final = CompositeVideoClip([clip, barra, txt_t] + subs)
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
    clip.close()
    final.close()

@bot.message_handler(func=lambda message: True)
def msg_recebida(message):
    if "http" in message.text:
        bot.reply_to(message, "⏳ Ja estou editando! Aguarde uns 3 minutos...")
        try:
            # Download
            path_b = f"b_{message.chat.id}.mp4"
            path_f = f"f_{message.chat.id}.mp4"
            with yt_dlp.YoutubeDL({'outtmpl': path_b, 'format': 'best', 'quiet': True}) as ydl:
                ydl.download([message.text])
            
            # Edicao
            editar_video(path_b, path_f)
            
            # Envio
            with open(path_f, 'rb') as v:
                bot.send_video(message.chat.id, v, caption="✅ Video pronto!")
            
            os.remove(path_b)
            os.remove(path_f)
        except Exception as e:
            bot.reply_to(message, f"❌ Erro: {e}")

bot.infinity_polling()
