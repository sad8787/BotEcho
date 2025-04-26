from asyncio.windows_events import NULL
from email.message import Message
import json
import asyncio
import os
import platform
from pickle import NONE, TRUE
from typing import Sequence
from unittest.mock import DEFAULT
import telegram
from telegram import User
from telegram.ext import *
from telegram import ForceReply, Update,Chat, ChatMember, ChatMemberUpdated,Bot
from telegram.ext import Updater,Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ChatAction
from typing import List, Dict
from datetime import datetime

#app
import keys


##IA
import transformers
#from transformers.models.gpt_neo.modeling_gpt_neo import GPTNeoForCausalLM
#from transformers.models.gpt2.tokenization_gpt2 import GPT2Tokenizer
from transformers.pipelines import pipeline
import torch

##SO
# Detectar sistema operativo
if platform.system() == "Windows":
    base_path = "C:/fotosTelegramECHOBOT"
else:
    base_path = "c/fotosTelegramECHOBOT"
# Crear carpeta base si no existe
os.makedirs(base_path, exist_ok=True)


# Create the Application and pass it your bot's token.
application = Application.builder().token(keys.token).build()
#generator_en = pipeline("text-generation", model="gpt2", tokenizer="gpt2", truncation=True)
generator_es = pipeline(
        "text-generation",
        model="datificate/gpt2-small-spanish",
        tokenizer="datificate/gpt2-small-spanish",
        pad_token_id=50256,
        truncation=True
    )
def text_generator(text: str, max_length: int = 100, idioma: str = "es"):
     try:
        resultado = generator_es(text, max_length=max_length)    
        if isinstance(resultado, list) and 'generated_text' in resultado[0]:
            return resultado[0]['generated_text']
        else:
            return "No te entiendo"
     except Exception as e:
        print( f"Error: {str(e)}")
        return f"No te entiendo"



# Bot commands
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:    
    if update.message and update.message.text:
        text_base = update.message.text        
        print(text_base)
        text=text_generator(text_base,200) or "No se pudo generar texto"
        print(text)
        await update.message.reply_text(str(text))
    else:
        print ("No menssage")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text( "Hola! Soy un bot de prueba. Envíame un mensaje y te responderé." )


# Manejar fotos
async def save_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.from_user:
        user_id= get_user_id_safe(update)
        if user_id is None:
            await update.message.reply_text("No se pudo identificar al usuario.")
            return
        
        user_folder = os.path.join(base_path, user_id)
        os.makedirs(user_folder, exist_ok=True)

        # 🔄 Lanzar tarea para limpiar fotos antiguas (sin bloquear)
        asyncio.create_task(limpiar_fotos_antiguas(user_folder))

        if update.message.photo:
            photo = update.message.photo[-1]  # Foto de mayor resolución
            file = await context.bot.get_file(photo.file_id)

            # Crear nombre basado en fecha y hora
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(user_folder, f"{timestamp}.jpg")

            try:
                await file.download_to_drive(file_path)
                await update.message.reply_text("Foto guardada correctamente.")
            except OSError as e:
                if "No space left on device" in str(e) or e.errno == 28:
                    await update.message.reply_text("Error: No hay espacio en el disco para guardar la foto.")
                    print(f"[ERROR] Sin espacio en disco al guardar {file_path}")
                else:
                    await update.message.reply_text("Error del sistema al guardar la foto.")
                    print(f"[ERROR] OSError desconocido: {str(e)}")
            except Exception as e:
                await update.message.reply_text("Ocurrió un error inesperado al guardar la foto.")
                print(f"[ERROR] {str(e)}")
        else:
            await update.message.reply_text("No se recibió ninguna foto.")
    else:
        print("Mensaje o usuario no disponible.")


async def ultimas_fotos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message and update.message.from_user:
        user_id = str(update.message.from_user.id)
        user_folder = os.path.join(base_path, user_id)

        if not os.path.exists(user_folder):
            await update.message.reply_text("No tienes fotos guardadas todavía.")
            return

        # Mostrar que el bot está "pensando"
        userid= get_user_id_safe(update)
        if userid is None:
            await update.message.reply_text("No se pudo identificar al usuario.")
            return
        await context.bot.send_chat_action(chat_id=userid, action=ChatAction.UPLOAD_PHOTO)

        # Obtener las 3 fotos más recientes por fecha de modificación
        fotos = sorted(
            [f for f in os.listdir(user_folder) if f.lower().endswith(".jpg")],
            key=lambda x: os.path.getmtime(os.path.join(user_folder, x)),
            reverse=True
        )[:3]

        if not fotos:
            await update.message.reply_text("No se encontraron fotos recientes.")
            return

        for foto in fotos:
            path = os.path.join(user_folder, foto)
            try:
                with open(path, "rb") as img:
                    await update.message.reply_photo(photo=img)
            except Exception as e:
                await update.message.reply_text(f"No pude enviar una foto: {str(e)}")
    else:
        if update.message:
            await update.message.reply_text("No se pudo identificar al usuario.")








# Auxiliares
def get_user_id_safe(update: Update):
    return str(update.message.from_user.id) if update.message and update.message.from_user else None

async def limpiar_fotos_antiguas(user_folder: str):
    try:
        fotos = sorted(
            [f for f in os.listdir(user_folder) if f.lower().endswith(".jpg")],
            key=lambda x: os.path.getmtime(os.path.join(user_folder, x))
        )
        if len(fotos) >= 9:
            foto_mas_antigua = fotos[0]
            path_a_borrar = os.path.join(user_folder, foto_mas_antigua)
            os.remove(path_a_borrar)
            print(f"[INFO] Foto antigua eliminada: {path_a_borrar}")
    except Exception as e:
        print(f"[ERROR] Al eliminar foto antigua: {str(e)}")

# Run the program
if __name__ == '__main__':      
    # Commands    
    application.add_handler(MessageHandler( filters.TEXT  & ~filters.COMMAND ,echo))   
    application.add_handler(MessageHandler(filters.PHOTO, save_photo))
    application.add_handler(CommandHandler("ultimasfotos", ultimas_fotos))
    application.add_handler(CommandHandler("start", start))
    application.run_polling(1.0)