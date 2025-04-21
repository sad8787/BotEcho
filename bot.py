#@SadielBotbot:
# Reemplaza esto con tu propio token
#TOKEN = "5459892481:AAFdl1xAQKVylQ-1RPjQjJqakNNCBPTroDo"
#@PrototypeSalesMPro100robot:
#TOKEN = "2066976010:AAGW71YiXVE1qdygauqP9_YfuEBFsH2aofg"
#@TextWebBot:
TOKEN = "6661596250:AAH56SLFmd1J8HAO2lIzrWfriDB1oHryvqg"

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
print("0")
from transformers import GPTNeoForCausalLM, AutoTokenizer
import torch
print("1")
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-1.3B")
model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-1.3B")

def generate_text(prompt: str, max_length: int = 50):
    """
    Genera texto a partir de un prompt utilizando el modelo GPT-Neo.

    :param prompt: El texto inicial a partir del cual el modelo generará más texto.
    :param max_length: La longitud máxima del texto generado.
    :return: El texto generado por el modelo.
    """
    # Tokenizamos el prompt
    inputs = tokenizer(prompt, return_tensors="pt")

    # Obtenemos la atención (attention_mask) de los tokens
    attention_mask = inputs["attention_mask"]

    # Generamos el texto
    outputs = model.generate(
        inputs["input_ids"],
        attention_mask=attention_mask,
        max_length=max_length,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id  # Esto elimina el warning sobre el pad_token
    )

    # Decodificamos los resultados generados en texto
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return generated_text

print("2")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):   
    await update.message.reply_text("¡Hola! Soy un bot de eco. Mándame un mensaje y lo repetiré.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text or "" 
    if message_text:  # Si hay texto en el mensaje 
        message_text=message_text.lower()
        if "había una vez" not in message_text:
            message_text = "Había una vez " + message_text
        print(message_text)
        generated_text = generate_text(message_text,100)
        print(generated_text)
        #reverso = message_text[::-1] 
        await update.message.reply_text(generated_text)
    else:        
        await update.message.reply_text(f''' Hola  debes escribir algo como, Había una vez un dragón que ''')
    
    

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.run_polling()

if __name__ == '__main__':
    main()

