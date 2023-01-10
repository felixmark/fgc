from telegram import *
from telegram.ext import *
from enum import Enum
from fgc_tools import FGCCreator
import cairosvg
import os
CREATE_FGC_TEXT = "Create FGC"
READ_FGC_TEXT = "Read FGC"

class State(Enum):
    NONE = 0
    DECISION = 1
    CREATE_FGC = 2
    READ_FGC = 3

current_state = State.NONE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with inline buttons attached."""
    global current_state
    print("Received /start")
    buttons = [[KeyboardButton(CREATE_FGC_TEXT), KeyboardButton(READ_FGC_TEXT)]]
    reply_markup = ReplyKeyboardMarkup(buttons)
    await update.message.reply_text("Create or read FGC?",  reply_markup=reply_markup)
    current_state = State.DECISION

async def textHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    global current_state
    if current_state == State.DECISION:
        if update.message.text.startswith(CREATE_FGC_TEXT):
            current_state = State.CREATE_FGC
            await update.message.reply_text('Send the string to encode.')
        elif update.message.text.startswith(READ_FGC_TEXT):
            current_state = State.READ_FGC
            await update.message.reply_text('Send a photo to decode.')
    elif current_state == State.CREATE_FGC:
        svg_file_name = update.message.text + ".svg"
        png_file_name = update.message.text + ".png"

        FGCCreator.create_fgc(
            color_inner="#39a887", 
            color_outer="#0f1a3b",
            data=update.message.text, 
            output_file=svg_file_name,
            color_background="#ffffff",
            write_data_as_text=False
        )
        cairosvg.svg2png(url=svg_file_name, write_to=png_file_name)

        await update.message.reply_photo(png_file_name)
        os.remove(svg_file_name) 
        os.remove(png_file_name) 

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Type /start to create or read an FGC.')



with open('.secrets/bot_token.txt','r') as file:
    bot_token = file.read()

app = ApplicationBuilder().token(bot_token).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(MessageHandler(filters.TEXT, textHandler))

app.run_polling()