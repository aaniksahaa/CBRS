from datetime import datetime
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes
from utils import *

from keep_alive import keep_alive

# keep_alive()

ids = []

def get_user(update: Update):
    if update.message:
        return update.message.from_user
    elif update.callback_query:
        return update.callback_query.from_user
    return None 



############# JSON DB FOR NOW #####################



file_path = 'users.json'

def read_users():
    """Read the users from the JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

def write_users(users):
    """Write the users back to the JSON file."""
    with open(file_path, 'w') as file:
        json.dump(users, file, indent=4)

def search_user(username):
    """Search for a user by username."""
    users = read_users()
    for user in users:
        if user['username'] == username:
            return user
    return None

def update_user(username, **kwargs):
    """Update user information."""
    users = read_users()
    for user in users:
        if user['username'] == username:
            for key, value in kwargs.items():
                if key in user:
                    user[key] = value
            write_users(users)
            return True
    return False

def init_user(username, chat_id):
    users = read_users()
    users.append({
        "username": username,
        "chat_id": chat_id,
        "blood_group": None,
        "latitude": None,
        "longitude": None,
        "last_donation_month": None,
        "last_donation_year": None
    })
    write_users(users)


####################    BOT CODE    ######################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    chat_id = update.message.chat_id

    print(chat_id)

    u = search_user(user.username)
    if u is None:
        init_user(user.username, chat_id)


    help_text = f"""
🩸 Delta Blood Bot 🩸

Welcome @{user.username} ! We are happy to have you. Here is a list of commands to ease your interaction.

/start - Start the bot
/help - Show help text for using the bot
/my_info - View your last saved information

/blood_group - Input your blood group
/location - Input your location information
/last_donated - Input the date of your last blood donation

/register - Register to our donor database
/goodbye - Unregister from our donor database

📌 A Few Notes:

✅ Your /blood_group, /last_donated date and /location are required to register
✅ Even after you register, you will be able to update your info any time
✅ Please update your /last_donated date when you donate blood
✅ We do not share your information anywhere else. Please be assured
"""
    
    sent_message = await update.message.reply_text(help_text)

    # Wait for 5 seconds
    await asyncio.sleep(5)

    # Delete the bot's own message using chat_id and message_id
    await context.bot.delete_message(chat_id=sent_message.chat_id, message_id=sent_message.message_id)


async def show_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    u = search_user(user.username)

    month = u['last_donation_month']
    year = u['last_donation_year']
    lat = u['latitude']
    lon = u['longitude']

    help_text = f"""
🩸 Delta Blood Bot 🩸

Welcome @{user.username} ! Here are your currently saved data. 

✅ Blood Group: {u['blood_group']}
✅ Last Donation Date: {get_date_text(month,year)}
✅ Location: 
Latitude={lat}, Longitude={lon}

"""
    
    await update.message.reply_text(help_text)


async def register(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    await update.message.reply_text(f"""
Thanks {user.first_name}! You are registered as a donor.
""")

########################     BLOOD GROUP INPUT     #########################


# List of blood groups
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

# Function to start the bot and show blood group buttons
async def input_blood_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Generate the keyboard layout
    keyboard = []
    row = []
    for i, group in enumerate(BLOOD_GROUPS):
        row.append(InlineKeyboardButton(group, callback_data=f'bg_{group}'))
        # Create a new row after every two buttons
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    # Add any remaining buttons to the last row
    if row:
        keyboard.append(row)
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text('Please select your blood group:', reply_markup=reply_markup)

# Function to handle button presses
async def bg_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    query = update.callback_query
    blood_group = query.data.split('_')[1]
    await query.answer()

    response = 'Sorry! Error.'

    # Update a user
    updated = update_user(user.username, blood_group=blood_group)
    if updated:
        response = f"""
Thanks {user.first_name}! Your blood group is saved.

✅ Blood Group: {blood_group}
"""
        
    await query.edit_message_text(text=response)




###############################     LOCATION INPUT     ###############################


# Function to start the bot and ask for location
async def input_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user = get_user(update)

    ids.append(chat_id)

    location_button = KeyboardButton(text="✅ Please click here to share ✅\n📍📍 Your Location 📍📍 ", request_location=True)
    custom_keyboard = [[location_button]]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)

    first_name = user.first_name

    await update.message.reply_text(f"""Dear {first_name}, Please share your location:""", reply_markup=reply_markup)

# Function to handle the location update
async def process_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    user_location = update.message.location
    latitude = user_location.latitude
    longitude = user_location.longitude

    # Access user details
    user = get_user(update)

    response = 'Sorry! Error.'

    # Update a user
    updated = update_user(user.username, latitude=latitude, longitude=longitude)

    if updated:
        response = f"""
Thanks {user.first_name}! Your updated location is saved.

✅ Location: 
Latitude={latitude}, Longitude={longitude}
"""
    
    # Send a response including the user's details
    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())

    # await update.message.reply_text(f'Thanks! Your location: lat={latitude}, lon={longitude}')


####################################################################################


###############################     DATE INPUT     ###############################

async def input_last_donated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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

async def handle_date_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user = get_user(update)

    data = query.data

    if data.startswith('year_'):
        year = int(data.split('_')[1])
        context.user_data['year'] = year
        await query.edit_message_text(f"Year selected: {year}\n\nNow, please select a month:", reply_markup=create_month_keyboard())
    
    elif data.startswith('month_'):
        month = int(data.split('_')[1])
        context.user_data['month'] = month
        year = context.user_data['year']

        response = 'Sorry! Error.'

        # Update a user
        updated = update_user(user.username, last_donation_month=month, last_donation_year=year)

        if updated:
            response = f"""
Thanks for sharing, {user.first_name}! Your updated date is saved.
                                      
✅ Last Donation Date: {get_date_text(month,year)}
"""

        await query.edit_message_text(text=response)


####################################################################################



###############################     MESSAGE HANDLER     ###############################

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update)
    user_text = update.message.text.lower()
    # for now, using a naive approach
    patterns = ['blood', 'ব্লাড', 'রক্ত']
    flag = False
    for p in patterns:
        if p in user_text:
            flag = True
            break 
    if flag:
        info = get_info(user_text)
        users = read_users()
        matches = []
        for u in users:
            if(u['blood_group'] == info['blood_group']):
                matches.append(u)

        response = ''
        if len(matches) == 0:
            response = 'Sorry! No matching donor found'
        else:
            response = f'{len(matches)} matching donor found. I am notifying...'

        await update.message.reply_text(response)

        for u in matches:
            text = f'A matching blood seeking request from {get_full_name(user)}! Please help if you can.\n\n{user_text}'
            await context.bot.send_message(chat_id=u['chat_id'], text=text)


####################################################################################


# Main function to run the bot
def main() -> None:
    application = ApplicationBuilder().token(TG_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CommandHandler("register", register))
    application.add_handler(CommandHandler("my_info", show_my_info))
    application.add_handler(CommandHandler("blood_group", input_blood_group))
    application.add_handler(CommandHandler("last_donated", input_last_donated))
    application.add_handler(CommandHandler("location", input_location))

    application.add_handler(MessageHandler(filters.LOCATION, process_location))

    # Register the message handler for responding to "hello"
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    application.add_handler(CallbackQueryHandler(handle_date_button, pattern='year_|month_'))
    application.add_handler(CallbackQueryHandler(bg_button, pattern='bg_'))

    keep_alive(application.bot)

    # Start the bot
    application.run_polling()
    # await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
