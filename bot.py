from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from config.configs import *
from config.keyboards import *

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter a number:", reply_markup=DIGITS_KB)
    context.user_data["start_msg_id"] = start_msg.id

    return 0

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

    # Now you can do any logic with your number via `context.user_data['number']`

    # End of converstation
    await context.bot.edit_message_text(
        text=f"Success!",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["message_id"]
    )

    # Now delete a trash left...
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["start_msg_id"]
    )

    del context.user_data["number"]
    del context.user_data["message_id"]
    del context.user_data["start_msg_id"]

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

    # Now delete a trash left...
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["start_msg_id"]
    )

    del context.user_data["number"]
    del context.user_data["message_id"]
    del context.user_data["start_msg_id"]

    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    states = dict.fromkeys([n for n in range(4)], [CallbackQueryHandler(process_number, pattern='^[0-9]$')])

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
