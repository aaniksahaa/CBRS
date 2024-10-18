from datetime import datetime
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ContextTypes
from utils import *
from api import * 
from keep_alive import keep_alive
from message_parser import *

# keep_alive()

BOT_USERNAME = 'delta77bloodbot'
BOT_LINK = f'https://t.me/{BOT_USERNAME}'
FRONTEND_BASE_URL = 'https://delta-blood-bot.netlify.app'
GENERIC_ERROR_MSG = "Sorry! We are facing an issue... Please try again later."

ids = []

def get_user(update: Update):
    if update.message:
        return update.message.from_user
    elif update.callback_query:
        return update.callback_query.from_user
    return None 

def search_telegram_user(username, chat_id):
    matching_donors = fetch_donors({
        # 'telegramUsername': username,
        'chatPlatform': 'telegram',
        "telegramChatId": str(chat_id), # search the id as string in db
    })
    if matching_donors:
        matching_donor = matching_donors[0]   # ideally there should be at max one match
        matching_donor['telegramChatId'] = int(matching_donor['telegramChatId'])
        
        required_fields = ['bloodGroup', 'latitude', 'longitude']
        hasCompleteInfo = True
        for field in required_fields:
            if not matching_donor[field]:
                hasCompleteInfo = False
                break
        # note that this field is being set here...
        matching_donor['hasCompleteInfo'] = hasCompleteInfo

        return matching_donor
    else:
        return None
    
def init_telegram_user(user, chat_id):
    response = create_donor({
        "name": " ".join([user.first_name, user.last_name]),
        "firstName": user.first_name,
        "lastName": user.last_name,
        "chatPlatform": "telegram",
        "telegramUsername": user.username,
        "telegramChatId": str(chat_id), # store the id as string in db
    })

    if response['success']:
        return response['donor']
    else:
        return None

def enable_notifications(donor_id):
    response = update_donor(donor_id,{
            "isNotificationDisabled": False
        })
    return response

def disable_notifications(donor_id):
    response = update_donor(donor_id,{
            "isNotificationDisabled": True
        })
    return response

def get_chat_type(update):
    return update.effective_chat.type

####################    BOT WORKFLOW    ######################

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        group_greetings_text = f"""
Greetings! I am a telegram bot designed to facilitate the searching for emergency blood donation. When I find messages in the group that are seeking blood donation, I will automatically notify nearby registered donors based on criteria matches.

<b>If any of you wish to register as a blood donor, please inbox me by clicking the following link:</b>

{BOT_LINK}

Thanks!
"""
        await update.message.reply_text(group_greetings_text, parse_mode='HTML')
        return 

    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id

    matching_donor = search_telegram_user(username, chat_id)

    new_user = None

    if matching_donor:
        enable_notifications(matching_donor['id'])
        if not matching_donor['hasCompleteInfo']:
            new_user = matching_donor    
    else:
        created_user = init_telegram_user(user, chat_id)
        if created_user:
            new_user = created_user

    help_text = f"""
🩸 Delta Blood Bot 🩸

Welcome <b>{get_full_name(user)}</b> ! We are happy to have you. Here is a list of commands to ease your interaction.

/help - Show help text for using the bot
/show_my_info - View your last saved information
/update_my_info - Update your information

/register_as_donor - Register to our donor database with your complete info
/goodbye - Unregister from our donor database

📌 A Few Notes:

✅ Your blood_group, last_donated date and location are required to register
✅ Even after you register, you will be able to update your info any time
✅ Please update your last_donated date when you donate blood
✅ Please be assured that we do not share your information anywhere else
"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')

    if new_user:
        registration_text = f"""
<b>Attention!</b>

Dear <b>{new_user['name']}</b>, since you are a new user, we would like to collect a bit more info about you so that you may be served with appropriate blood seeking requests nearby.

Please do care to provide your detailed info through the following link:

{FRONTEND_BASE_URL}/home/{new_user['id']}

After you provide your info, please check whether they are okay by the command 
/show_my_info

Thank you!
    """
        await update.message.reply_text(registration_text, parse_mode='HTML')

async def register_as_donor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        return 
    
    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id

    matching_donor = search_telegram_user(username, chat_id)

    new_user = None

    if matching_donor:
        enable_notifications(matching_donor['id'])
        if not matching_donor['hasCompleteInfo']:
            new_user = matching_donor    
    else:
        created_user = init_telegram_user(user, chat_id)
        if created_user:
            new_user = created_user

    if new_user:
        registration_text = f"""
Dear <b>{get_full_name(user)}</b>, since you are a new user, we would like to collect a bit more info about you so that you may be served with appropriate blood seeking requests nearby.

Please do care to provide your detailed info through the following link:

{FRONTEND_BASE_URL}/home/{new_user['id']}

After you provide your info, please check whether they are okay by the command 
/show_my_info

Thank you!
    """
        await update.message.reply_text(registration_text, parse_mode='HTML')
    else:
        reply_text = f"""
Dear <b>{get_full_name(user)}</b>, you are already registered as a donor and your notifications have been enabled.
"""
        await update.message.reply_text(reply_text, parse_mode='HTML')

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        return 
    
    user = get_user(update)

    help_text = f"""
🩸 Delta Blood Bot 🩸

Welcome @{user.username} ! We are happy to have you. Here is a list of commands to ease your interaction.

/help - Show help text for using the bot
/show_my_info - View your last saved information
/update_my_info - Update your information

/register_as_donor - Register to our donor database with your complete info
/goodbye - Unregister from our donor database

📌 A Few Notes:

✅ Your blood_group, last_donated date and location are required to register
✅ Even after you register, you will be able to update your info any time
✅ Please update your last_donated date when you donate blood
✅ Please be assured that we do not share your information anywhere else
"""
    await update.message.reply_text(help_text)
    

async def show_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        return 
    
    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id

    matching_donor = search_telegram_user(username, chat_id)

    reply_text = ""

    if not matching_donor:
        reply_text = GENERIC_ERROR_MSG + "If the issue persists, consider registering again with /start command "
    else:
        NA_MESSAGE = "<i>Not set yet</i>"

        last_donated = format_iso_date(matching_donor['lastDonated']) if matching_donor['lastDonated'] else NA_MESSAGE
        location = NA_MESSAGE
        if matching_donor['latitude'] and matching_donor['longitude']:
            lat = matching_donor['latitude']
            lon = matching_donor['longitude']
            location = f"Latitude={round(lat,2)}°N, Longitude={round(lon,2)}°E"
        blood_group = matching_donor['bloodGroup'] if matching_donor['bloodGroup'] else NA_MESSAGE

        reply_text = f"""
🩸 Delta Blood Bot 🩸

Welcome <b>{get_full_name(user)}</b>! Here are your currently saved data. 

✅ <b>Blood Group</b>: {blood_group}
✅ <b>Last Donation Date</b>: {last_donated}
✅ <b>Location</b>: 
{location}

You may click /update_my_info to make changes anytime.

Thank you!
    """
        
    await update.message.reply_text(reply_text, parse_mode='HTML')

async def update_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        return 
    
    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id

    matching_donor = search_telegram_user(username, chat_id)

    reply_text = ""

    if not matching_donor:
        reply_text = GENERIC_ERROR_MSG
    else:
        reply_text = f"""
🩸 Delta Blood Bot 🩸

Dear <b>{get_full_name(user)}</b>, please update your info through the following link:

{FRONTEND_BASE_URL}/home/{matching_donor['id']}

After you provide your info, please check whether they are okay by the command 
/show_my_info

Thank you!
    """
        await update.message.reply_text(reply_text, parse_mode='HTML')
    

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'group':
        return 
    
    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id

    matching_donor = search_telegram_user(username, chat_id)

    reply_text = GENERIC_ERROR_MSG

    if matching_donor:
        response = disable_notifications(matching_donor['id'])

        if response['success']:
            reply_text = f"""
You are successfully unregistered and you won't receive further notifications. If you change your mind, just click on /register_as_donor again.
"""

    await update.message.reply_text(reply_text)

###############################     MESSAGE HANDLER     ###############################

def initial_screening(text):
    text = text.lower()
    if len(text) < 30:
        return False
    patterns = ['blood', 'ব্লাড', 'রক্ত', 'emergency']
    flag = False
    for p in patterns:
        if p in text:
            flag = True
            break
    return flag

async def process_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if get_chat_type(update) == 'private':
        return 
    
    user = get_user(update)
    username = user.username
    chat_id = update.message.chat_id
    message_id = update.message.message_id 
    
    user_text = update.message.text
    # print(user_text)

    flag = initial_screening(user_text)

    if flag:
        parsed_data = parse_blood_seeking_message(user_text)
        # print(parsed_data)

        if parsed_data.get('error', False):
            # parsing error
            return
        
        # print(json.dumps(parsed_data, indent=4))

        bloodrequest = parsed_data
        bloodrequest['sourceTelegramChatId'] = str(chat_id)
        bloodrequest['sourceTelegramMessageId'] = message_id

        print(json.dumps(bloodrequest, indent=4))

        response = create_bloodrequest(bloodrequest)

        if response['success']:
            created_bloodrequest = response['bloodrequest']
            print(json.dumps(created_bloodrequest, indent=4))

            matching_donors = find_matching_donors(created_bloodrequest['id'])

            print(json.dumps(matching_donors, indent=4))

            # this part should actually happen centrally
            candidates = matching_donors['nearbyDonors'] + matching_donors['otherEligibleDonors']

            LIMIT = 5

            text = f'A matching blood donation request from <b>{get_full_name(user)}</b>! Please help if you can.\n\n{user_text}'

            for donor in candidates[:LIMIT]:
                # print(donor)
                distance = None
                if(donor.get('distance', None)):
                    distance = donor['distance']
                    text += f"\n\nThe location is approximately <b>{distance} kilometers</b> away from you."
                if donor['chatPlatform'] == 'telegram':
                    await context.bot.send_message(chat_id=donor['telegramChatId'], text=text, parse_mode='HTML')

        # users = read_users()
        # matches = []
        # for u in users:
        #     if(u['blood_group'] == info['blood_group']):
        #         matches.append(u)

        # response = ''
        # if len(matches) == 0:
        #     response = 'Sorry! No matching donor found'
        # else:
        #     response = f'{len(matches)} matching donor found. I am notifying...'

        # await update.message.reply_text(response)

        # for u in matches:
        #     text = f'A matching blood seeking request from {get_full_name(user)}! Please help if you can.\n\n{user_text}'
        #     await context.bot.send_message(chat_id=u['chat_id'], text=text)


####################################################################################


# Main function to run the bot
def main() -> None:
    application = ApplicationBuilder().token(TG_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    
    application.add_handler(CommandHandler("show_my_info", show_my_info))
    application.add_handler(CommandHandler("update_my_info", update_my_info))

    application.add_handler(CommandHandler("register_as_donor", register_as_donor))
    application.add_handler(CommandHandler("goodbye", unregister))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text))

    keep_alive(application.bot)

    # Start the bot
    application.run_polling()
    # await application.idle()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
