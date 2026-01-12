import os
import time
import telebot
import yt_dlp
import threading
from flask import Flask
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip
import moviepy.video.fx.all as vfx

# --- Web Server para o Render não dormir ---
app = Flask(__name__)
@app.route('/')
def health(): return "Bot Online!", 200
def run_flask(): app.run(host='0.0.0.0', port=10000)

# --- Configuração do Bot ---
TOKEN = os.environ.get('TELEGRAM_TOKEN')
bot = telebot.TeleBot(TOKEN)

def editar_video_leve(input_path, output_path):
    print(f"🎬 Editando: {input_path}")
    clip = VideoFileClip(input_path)
    
    # 1. Anti-bloqueio (Espelhar e Velocidade)
    clip = clip.fx(vfx.mirror_x)
    clip = clip.fx(vfx.speedx, 1.05)

    # 2. Barra de Título Amarela
    altura_barra = int(clip.h * 0.12)
    barra = ColorClip(size=(clip.w, altura_barra), color=(255, 255, 0)).set_duration(clip.duration).set_position(('center', 'top'))
    
    txt_titulo = TextClip("ACHADINHO ÚTIL! ✨", fontsize=int(altura_barra*0.5), color='black', font='Arial-Bold', method='caption', size=(clip.w*0.9, None))
    txt_titulo = txt_titulo.set_duration(clip.duration).set_position(('center', int(clip.h*0.02)))

    # 3. Montagem (Sem legendas IA para economizar RAM)
    final = CompositeVideoClip([clip, barra, txt_titulo])
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
    
    clip.close()
    final.close()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        # Limpa o link do Douyin se houver texto chinês
        if "douyin.com" in url and "http" in url:
            url = url.split("http")[1]
            url = "http" + url.split(" ")[0]

        msg_status = bot.reply_to(message, "⏳ Vídeo detectado! Editando agora (leva 1-2 min)...")
        
        try:
            b = f"v_{message.chat.id}.mp4"
            f = f"res_{message.chat.id}.mp4"
            
            with yt_dlp.YoutubeDL({'outtmpl': b, 'format': 'best', 'quiet': True}) as ydl:
                ydl.download([url])

            editar_video_leve(b, f)

            with open(f, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="✅ Seu vídeo pronto para postar!")

            os.remove(b)
            os.remove(f)
        except Exception as e:
            bot.reply_to(message, f"❌ Erro: {str(e)}")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🚀 Bot Iniciado no modo LITE!")
    bot.infinity_polling()
