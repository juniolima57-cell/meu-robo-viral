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
    
    # 1. Anti-bloqueio (Espelhar e aumentar velocidade em 5%)
    clip = clip.fx(vfx.mirror_x)
    clip = clip.fx(vfx.speedx, 1.05)

    # 2. Barra de Título Amarela
    altura_barra = int(clip.h * 0.12)
    barra = ColorClip(size=(clip.w, altura_barra), color=(255, 255, 0)).set_duration(clip.duration).set_position(('center', 'top'))
    
    # Usando DejaVu-Sans-Bold (Fonte padrão Linux) para evitar erros
    txt_titulo = TextClip(
        "ACHADINHO ÚTIL! ✨", 
        fontsize=int(altura_barra*0.5), 
        color='black', 
        font='DejaVu-Sans-Bold', 
        method='caption', 
        size=(clip.w*0.9, None)
    )
    txt_titulo = txt_titulo.set_duration(clip.duration).set_position(('center', int(clip.h*0.02)))

    # 3. Montagem Final
    final = CompositeVideoClip([clip, barra, txt_titulo])
    
    # 'ultrafast' ajuda a não estourar a memória do Render
    final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24, preset="ultrafast")
    
    clip.close()
    final.close()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if "http" in url:
        # Limpa links que vêm com texto (comum no Douyin e TikTok)
        if "http" in url:
            try:
                url = url.split("http")[1].split(" ")[0]
                url = "http" + url
            except:
                pass

        msg_status = bot.reply_to(message, "⏳ Vídeo detectado! Editando agora (leva 1-2 min)...")
        
        b = f"v_{message.chat.id}.mp4"
        f = f"res_{message.chat.id}.mp4"
        
        try:
            # Download do vídeo
            ydl_opts = {
                'outtmpl': b,
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            # Edição
            editar_video_leve(b, f)

            # Envio
            with open(f, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption="✅ Seu vídeo está pronto!")

        except Exception as e:
            bot.reply_to(message, f"❌ Erro no processamento: {str(e)}")
        
        finally:
            # Limpeza de arquivos temporários
            if os.path.exists(b): os.remove(b)
            if os.path.exists(f): os.remove(f)

if __name__ == "__main__":
    # Inicia servidor de saúde em segundo plano
    threading.Thread(target=run_flask).start()
    print("🚀 Bot Iniciado no modo LITE!")
    bot.infinity_polling()
