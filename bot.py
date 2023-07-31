import asyncio
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, filters
from pyrogram import Client
from pyrogram.types import User
from pyrogram.errors import BadRequest, SessionPasswordNeeded
from config.configs import *
from config.keyboards import *


class AuthStates:
    handle_acc_phone = 0
    fetch_actions = 1
    handle_password = 2
    process_number_1 = 3
    process_number_2 = 4
    process_number_3 = 5
    process_number_4 = 6
    process_number_5 = 7


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    start_msg = await context.bot.send_message(chat_id=update.effective_chat.id, text="Enter the account phone number:")
    context.user_data["auth_data"] = {}
    context.user_data["auth_data"]["start_msg_id"] = start_msg.id

    return AuthStates.handle_acc_phone

async def handle_acc_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone_number = update.message.text
    
    context.user_data["auth_data"]["phone_number"] = phone_number

    msg = await context.bot.send_message(
            text=f"Do you have two-step verification on this account ?(required to create a session):",
            chat_id=update.effective_chat.id,
            reply_markup=TWO_STEP_ASK_KB
        )
    
    context.user_data["auth_data"]["message_id"] = msg.id

    return AuthStates.fetch_actions

async def fetch_actions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer("Processing.")
    if update.callback_query.data == "two_step_yes":
        await context.bot.edit_message_text(
            text="Send two-step password in chat:",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["auth_data"]["message_id"]
        )

        return AuthStates.handle_password
    else:
        app = Client(context.user_data["auth_data"]["phone_number"], api_id=API_ID, api_hash=API_HASH, in_memory=True)
        context.user_data["auth_data"]["app"] = app
        await app.connect()
        sent_code = await app.send_code(phone_number=context.user_data["auth_data"]["phone_number"])

        context.user_data["auth_data"]["phone_code_hash"] = sent_code.phone_code_hash

        await context.bot.edit_message_text(
            text=f"Now type the authorization code:",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["auth_data"]["message_id"],
            reply_markup=DIGITS_KB
        )

        return AuthStates.process_number_1

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    password = update.message.text

    context.user_data["auth_data"]["password"] = password

    app = Client(context.user_data["auth_data"]["phone_number"], api_id=API_ID, api_hash=API_HASH, password=password, in_memory=True)
    context.user_data["auth_data"]["app"] = app
    await app.connect()
    sent_code = await app.send_code(phone_number=context.user_data["auth_data"]["phone_number"])

    context.user_data["auth_data"]["phone_code_hash"] = sent_code.phone_code_hash

    await context.bot.edit_message_text(
        text=f"Now type the authorization code:",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["auth_data"]["message_id"],
        reply_markup=DIGITS_KB
    )

    return 3

async def process_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    phone_code = update.callback_query.data

    if isinstance(context.user_data["auth_data"].get('phone_code'), str):
        context.user_data["auth_data"]['phone_code'] += phone_code
    else:
        context.user_data["auth_data"]['phone_code'] = phone_code
    print(phone_code)
    await update.callback_query.answer(context.user_data['auth_data']['phone_code'])

    if len(context.user_data["auth_data"]['phone_code']) < 5:
        return 2 + len(context.user_data["auth_data"]['phone_code'])

    # Now you can do any logic with your number via `context.user_data['number']`
    app: Client = context.user_data["auth_data"]["app"]

    try:
        user = await app.sign_in(
            context.user_data["auth_data"]["phone_number"],
            context.user_data["auth_data"]["phone_code_hash"],
            context.user_data["auth_data"]["phone_code"]
        )
    except BadRequest as e:
        print(e)
        print(context.user_data["auth_data"])
        await context.bot.edit_message_text(
            text=f"[ERROR] Some error happened. Make sure that all data is correct.",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["auth_data"]["message_id"]
        )
        del context.user_data["auth_data"]
        await app.disconnect()

        return ConversationHandler.END
    except SessionPasswordNeeded:
        await context.bot.edit_message_text(
            text=f"[ERROR] You didn't type two-step password, but it is required.",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["auth_data"]["message_id"]
        )
        del context.user_data["auth_data"]
        await app.disconnect()

        return ConversationHandler.END

    if not isinstance(user, User):
        await context.bot.edit_message_text(
            text=f"[ERROR] The account is not registered yet.",
            chat_id=update.effective_chat.id,
            message_id=context.user_data["auth_data"]["message_id"]
        )
        del context.user_data["auth_data"]

        return ConversationHandler.END
    session_string = await app.export_session_string()
    print(session_string)
    await app.disconnect()

    # End of converstation
    await context.bot.edit_message_text(
        text=f"Success! Session for {(user.first_name, user.last_name, user.username)} was created.",
        chat_id=update.effective_chat.id,
        message_id=context.user_data["auth_data"]["message_id"]
    )
    
    # Now delete a trash left...
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["auth_data"]["start_msg_id"]
    )

    del context.user_data["auth_data"]

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("Cancelling.")
    await update.callback_query.answer("Operation cancelled.")

    if context.user_data["auth_data"]["message_id"]:
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            text="Operation cancelled.",
            message_id=context.user_data["auth_data"]["message_id"]
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Operation cancelled."
        )

    # Now delete a trash left...
    await context.bot.delete_message(
        chat_id=update.effective_chat.id,
        message_id=context.user_data["auth_data"]["start_msg_id"]
    )

    del context.user_data["auth_data"]

    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    states = {
        AuthStates.handle_acc_phone: [MessageHandler(filters.Regex("^\d+$"), handle_acc_phone)],
        AuthStates.fetch_actions: [CallbackQueryHandler(fetch_actions, pattern='two_step_yes|two_step_no')],
        AuthStates.handle_password: [MessageHandler(filters.Regex("^\d{4}$"), handle_password)],
        AuthStates.process_number_1: [CallbackQueryHandler(process_number, pattern='^\d$')],
        AuthStates.process_number_2: [CallbackQueryHandler(process_number, pattern='^\d$')],
        AuthStates.process_number_3: [CallbackQueryHandler(process_number, pattern='^\d$')],
        AuthStates.process_number_4: [CallbackQueryHandler(process_number, pattern='^\d$')],
        AuthStates.process_number_5: [CallbackQueryHandler(process_number, pattern='^\d$')],
    }


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
