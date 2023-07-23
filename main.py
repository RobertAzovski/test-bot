from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Conversation states
DGT_1, DGT_2, DGT_3, DGT_4 = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton('1'), KeyboardButton('2'), KeyboardButton('3')],
        [KeyboardButton('4'), KeyboardButton('5'), KeyboardButton('6')],
        [KeyboardButton('7'), KeyboardButton('8'), KeyboardButton('9')],
        [KeyboardButton('0'), KeyboardButton('/cancel')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a number:", reply_markup=reply_markup)

    return DGT_1

async def process_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    number = update.message.text
    if isinstance(context.user_data.get('number'), str):
        context.user_data['number'] += number
    else:
        context.user_data['number'] = number
    print(number)

    if not context.user_data.get("message_id"):
        msg = await context.bot.send_message(
            text=f"You entered: {context.user_data['number']}",
            chat_id=update.effective_chat.id,
        )
        context.user_data["message_id"] = msg.id
    else:
        await context.bot.edit_message_text(
            text=f"You entered: {context.user_data['number']}",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["message_id"]
        )
    

    if len(context.user_data['number']) < 4:
        return len(context.user_data['number'])
    
    await context.bot.edit_message_text(
        text=f"Success!",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["message_id"]
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Cancelling.")

    if context.user_data.get("message_id"):
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            text="Operation cancelled.",
            message_id=context.user_data["message_id"]
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Operation cancelled."
        )

    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DGT_1: [MessageHandler(filters.Regex('^[0-9]$'), process_number)],
            DGT_2: [MessageHandler(filters.Regex('^[0-9]$'), process_number)],
            DGT_3: [MessageHandler(filters.Regex('^[0-9]$'), process_number)],
            DGT_4: [MessageHandler(filters.Regex('^[0-9]$'), process_number)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
