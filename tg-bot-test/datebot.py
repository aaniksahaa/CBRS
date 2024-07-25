from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from datetime import datetime

from utils import * 


################ DATE PICKER ################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please select a year:', reply_markup=create_year_keyboard())

def create_year_keyboard() -> InlineKeyboardMarkup:
    current_year = datetime.now().year
    keyboard = [[InlineKeyboardButton(str(year), callback_data=f'year_{year}') for year in range(current_year, current_year - 3, -1)]]
    return InlineKeyboardMarkup(keyboard)

def create_month_keyboard() -> InlineKeyboardMarkup:
    months_abbr = [calendar.month_abbr[i] for i in range(1, 13)]
    keyboard = [
        [InlineKeyboardButton(month, callback_data=f'month_{i+1}') for i, month in enumerate(months_abbr[:6])],
        [InlineKeyboardButton(month, callback_data=f'month_{i+7}') for i, month in enumerate(months_abbr[6:])]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith('year_'):
        year = int(data.split('_')[1])
        context.user_data['year'] = year
        await query.edit_message_text(f"Year selected: {year}\nNow, please select a month:", reply_markup=create_month_keyboard())
    
    elif data.startswith('month_'):
        month = int(data.split('_')[1])
        context.user_data['month'] = month
        year = context.user_data['year']
        await query.edit_message_text(text=f"Selected Date: {get_date_text(month,year)}")

################ DATE PICKER ################

def main() -> None:
    application = Application.builder().token(TG_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_button, pattern='year_|month_'))

    application.run_polling()
    application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
