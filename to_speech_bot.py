from telegram import Update, InputFile
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes
from gtts import gTTS
from aiofiles.os import remove as aio_remove
from aiofiles import open as aio_open  # Use aiofiles for asynchronous file operations
from typing import final
import asyncio

KEY: final = '7000535672:AAGCuDvaLprwh6H4vDvsx48Dz6D8Myo6_OU'
bot_username: final = 'to_speech_bot'

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello There. I convert text to speech')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('If you send me a text, I will reply with the same text in a voice note')


# Responses
async def text_to_speech(text: str, message_id: int, lang: str = 'en') -> str:
    tts = gTTS(text=text, lang=lang)
    filename = f"response_{message_id}.mp3"
    await asyncio.to_thread(tts.save, filename)  # Run blocking I/O in a thread
    return filename


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text = update.message.text
    message_id = update.message.message_id

    print(f'User ({update.message.chat.username}) in {message_type}: {text}')

    if message_type == 'group':
        if bot_username in text:
            new_text = text.replace(bot_username, '').strip()
            filename = await text_to_speech(new_text, message_id)
        else:
            return
    else:
        filename = await text_to_speech(text, message_id)

    print('Bot: sending voice note')

    # Open the file, read its content and then pass it to InputFile
    async with aio_open(filename, 'rb') as audio:
        audio_data = await audio.read()  # Read the content of the file
        await update.message.reply_voice(
            voice=InputFile(audio_data, filename=filename))  # Pass the content to InputFile

    await aio_remove(filename)  # Use aiofiles.os for async file removal


if __name__ == '__main__':
    application = Application.builder().token(KEY).build()

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()
