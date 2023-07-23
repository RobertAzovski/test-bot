from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
# Conversation states
DGT_1, DGT_2, DGT_3, DGT_4 = range(5, start=1)

async def start(update, context):
    keyboard = [
        [KeyboardButton('1'), KeyboardButton('2'), KeyboardButton('3')],
        [KeyboardButton('4'), KeyboardButton('5'), KeyboardButton('6')],
        [KeyboardButton('7'), KeyboardButton('8'), KeyboardButton('9')],
        [KeyboardButton('0'), KeyboardButton('cancel')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a number:", reply_markup=reply_markup)
    return DGT_1

async def process_number(update, context):
    number = update.message.text
    if isinstance(context.user_data['number'], str):
        context.user_data['number'] += number
    else:
        context.user_data['number'] = ''

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"You entered: {context.user_data['number']}")

    if len(context.user_data['number']) < 4:
        return len(context.user_data['number'])

    return ConversationHandler.END

async def cancel(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Operation cancelled.")
    return ConversationHandler.END

def main():
    application = Application.builder().token("6289014145:AAEZVhcWsJk3qKJHAsgJM9Me_JD_-bPiOjs").build()

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
