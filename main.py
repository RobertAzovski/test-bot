from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Conversation states
DGT_1, DGT_2, DGT_3, DGT_4 = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
        [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
        [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
        [InlineKeyboardButton('0', callback_data='0'), InlineKeyboardButton('cancel', callback_data='cancel')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a number:", reply_markup=reply_markup)

    return DGT_1

async def process_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    number = update.callback_query.data
    await update.callback_query.answer(number)
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
    await update.callback_query.answer("Operation cancelled.")

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

    del context.user_data["number"]
    del context.user_data["message_id"]

    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    states = dict.fromkeys([DGT_1, DGT_2, DGT_3, DGT_4], [CallbackQueryHandler(process_number, pattern='^[0-9]$')])

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states=states,
        fallbacks=[CallbackQueryHandler(cancel, pattern='cancel')],
    )
    application.add_handler(conv_handler)

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()
