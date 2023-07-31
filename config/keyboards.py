from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

DIGITS_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton('1', callback_data='1'), InlineKeyboardButton('2', callback_data='2'), InlineKeyboardButton('3', callback_data='3')],
    [InlineKeyboardButton('4', callback_data='4'), InlineKeyboardButton('5', callback_data='5'), InlineKeyboardButton('6', callback_data='6')],
    [InlineKeyboardButton('7', callback_data='7'), InlineKeyboardButton('8', callback_data='8'), InlineKeyboardButton('9', callback_data='9')],
    [InlineKeyboardButton('0', callback_data='0'), InlineKeyboardButton('cancel', callback_data='cancel')]
])

TWO_STEP_ASK_KB = InlineKeyboardMarkup([
    [InlineKeyboardButton('Yes', callback_data='two_step_yes'), InlineKeyboardButton('No', callback_data='two_step_no')]
])