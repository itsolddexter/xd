from telethon import TelegramClient, events, Button
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.types import ChannelParticipantsAdmins, PeerChannel

API_ID = '28905243'
API_HASH = '9be6c8141d6d9d94f264953876ac34ad'
BOT_TOKEN = '7131007033:AAHH1wLt-jAnUBp5pDy--D9fL82w-1u-3AQ'
ADMIN_ID = 7136183860

REQUIRED_CHANNELS = []
platforms = ['Platform1', 'Platform2', 'Platform3', 'Platform4']
W_MESSAGE_BEFORE_JOIN = "<b>Welcome! 🎉</b> Please join the required channels before proceeding."
W_MESSAGE_AFTER_JOIN = "<b>Welcome! 🚀</b> You have joined all the required channels. Please select your platform."
ENTER_UID_MESSAGE = "🔑 Please enter your UID."
INVALID_UID_MESSAGE = "❌ Invalid UID. Please enter a valid UID."
PENDING_VERIFICATION_MESSAGE = "⏳ <b>Your UID verification is pending, please wait for confirmation.</b>"
VERIFICATION_SUCCESS = "✅ Your UID has been verified successfully!"
VERIFICATION_FAILED = "❌ Verification failed. Please try again."

user_data = {}  # To store user data with chat_id as key
buttons_per_row = 4

client = TelegramClient('botxd', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def generate_platform_buttons():
    buttons = [Button.inline(platform, f'p_{platform}') for platform in platforms]
    return [buttons[i:i + buttons_per_row] for i in range(0, len(buttons), buttons_per_row)]

def generate_verification_buttons(uid):
    return [Button.inline("✅ Accept", f'v_{uid}_yes'), Button.inline("❌ Reject", f'v_{uid}_no')]

async def is_user_in_channel(user_id, channel):
    try:
        participant = await client(GetParticipantRequest(channel, user_id))
        return participant.participant is not None
    except:
        return False

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    chat_id = event.chat_id

    if chat_id not in user_data:
        user_data[chat_id] = {'user_id': user_id, 'username': event.sender.username, 'first_name': event.sender.first_name}

    not_joined_channels = [channel for channel in REQUIRED_CHANNELS if not await is_user_in_channel(user_id, channel)]
    if not_joined_channels:
        join_message = "<b>Need To Join These Channels:</b> 📢\n\n" + "\n".join([f"1) {channel}" for channel in not_joined_channels]) + "\n\n<i>After Joining, Click On '🔄 Try Again!'</i> 😊"
        bot_name = (await client.get_me()).username
        try_again_url = f"https://t.me/{bot_name}?start=start"
        await client.send_message(chat_id, W_MESSAGE_BEFORE_JOIN, parse_mode='html')
        await client.send_message(chat_id, join_message, parse_mode='html', buttons=[Button.url("🔄 Try Again!", try_again_url)])
        
    else:
        user_data[chat_id]['awaiting_uid'] = False
        await client.send_message(chat_id, W_MESSAGE_AFTER_JOIN, parse_mode='html')
        await client.send_message(chat_id, "Select your platform:", buttons=generate_platform_buttons())

@client.on(events.NewMessage(pattern='/admin'))
async def admin_panel(event):
    if event.sender_id == ADMIN_ID:
        buttons = [
            [Button.inline("📋 Set Channels", "set_channels"), Button.inline("📝 Set Start After", "set_start_message_after")],
            [Button.inline("📝 Set Start Before", "set_start_message_before"), Button.inline("🔧 Set Platforms", "set_platforms")],
            [Button.inline("🔢 Set Buttons Per Row", "set_buttons_per_row"), Button.inline("📢 Broadcast", "broadcast")],
            [Button.inline("📊 Stats", "stats")]
        ]
        await event.reply("<b>Admin panel:</b>", buttons=buttons, parse_mode='html')

@client.on(events.NewMessage(pattern='/send'))
async def send_message_to_user(event):
    if event.sender_id == ADMIN_ID:
        try:
            args = event.message.message.split(' ', 2)
            if len(args) < 3:
                await event.reply("Usage: /send <user_id> <message>")
                return
            user_id = int(args[1])
            text = args[2]
            await client.send_message(user_id, text)
            await event.reply("Message sent successfully.")
        except Exception as e:
            await event.reply(f"Error: {str(e)}")
    else:
        await event.reply("You are not authorized to use this command.")

@client.on(events.CallbackQuery(data=b"set_channels"))
async def set_channels(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the channel usernames in the format @Channel1, @Channel2, ...")
            response = await conv.get_response()
            channels = response.text.split(',')
            global REQUIRED_CHANNELS
            REQUIRED_CHANNELS = [channel.strip() for channel in channels if channel.strip().startswith('@')]
            await conv.send_message("Channels set successfully: " + ", ".join(REQUIRED_CHANNELS))

@client.on(events.CallbackQuery(data=b"set_start_message_before"))
async def set_start_message_before(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the new start message for users who need to join channels in HTML format.")
            response = await conv.get_response()
            global W_MESSAGE_BEFORE_JOIN
            W_MESSAGE_BEFORE_JOIN = response.text
            await conv.send_message("Start join message updated successfully.")

@client.on(events.CallbackQuery(data=b"set_start_message_after"))
async def set_start_message_after(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the new start message for users who have joined channels in HTML format.")
            response = await conv.get_response()
            global W_MESSAGE_AFTER_JOIN
            W_MESSAGE_AFTER_JOIN = response.text
            await conv.send_message("Start no join message updated successfully.")

@client.on(events.CallbackQuery(data=b"set_platforms"))
async def set_platforms(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the platform names separated by commas.")
            response = await conv.get_response()
            global platforms
            platforms = [platform.strip() for platform in response.text.split(',')]
            await conv.send_message("Platforms updated successfully.")

@client.on(events.CallbackQuery(data=b"set_buttons_per_row"))
async def set_buttons_per_row(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the number of buttons per row as a single number.")
            response = await conv.get_response()
            global buttons_per_row
            try:
                buttons_per_row = int(response.text.strip())
                await conv.send_message("Buttons per row updated successfully.")
            except ValueError:
                await conv.send_message("Invalid number. Please send a valid number.")

@client.on(events.CallbackQuery(data=b"broadcast"))
async def handle_broadcast(event):
    if event.sender_id == ADMIN_ID:
        await event.delete()
        async with client.conversation(event.chat_id) as conv:
            await conv.send_message("Please send the broadcast message (text, image, or video).")
            response = await conv.get_response()
            if response.text:
                await broadcast_message(response.text)
            elif response.photo:
                await broadcast_media(response, 'photo')
            elif response.video:
                await broadcast_media(response, 'video')

@client.on(events.CallbackQuery(data=b"stats"))
async def handle_stats(event):
    if event.sender_id == ADMIN_ID:
        total_users = len(user_data)
        await event.delete()
        await client.send_message(event.chat_id, f"📊 <b>Total Users:</b> {total_users}", parse_mode='html')

async def broadcast_message(text):
    for chat_id in user_data.keys():
        await client.send_message(chat_id, text, parse_mode='html')

async def broadcast_media(message, media_type):
    caption = message.text if message.text else ""
    for chat_id in user_data.keys():
        if media_type == 'photo':
            await client.send_file(chat_id, message.photo, caption=caption)
        elif media_type == 'video':
            await client.send_file(chat_id, message.video, caption=caption)

@client.on(events.CallbackQuery(data=lambda data: data.startswith(b'p_')))
async def handle_platform_selection(event):
    platform = event.data.decode('utf-8').split('_')[1]
    chat_id = event.chat_id

    if chat_id in user_data:
        user_info = user_data[chat_id]
        user_info['platform'] = platform
        user_info['awaiting_uid'] = True
        await event.respond(ENTER_UID_MESSAGE)
        await event.delete()

@client.on(events.NewMessage())
async def handle_message(event):
    chat_id = event.chat_id

    if chat_id in user_data and user_data[chat_id].get('awaiting_uid'):
        await handle_uid(event)
    elif event.sender_id != ADMIN_ID:
        await forward_user_messages(event)
    else:
        await handle_admin_reply(event)

async def handle_uid(event):
    uid = event.text
    chat_id = event.chat_id

    if chat_id in user_data:
        user_data[chat_id].update({'uid': uid, 'awaiting_uid': False})
        user_info = user_data[chat_id]
        await event.respond(PENDING_VERIFICATION_MESSAGE, parse_mode='html')
        verification_buttons = generate_verification_buttons(user_info['uid'])
        await client.send_message(ADMIN_ID, f"<b>PLATFORM NAME:</b> {user_info['platform']}\n<b>UID:</b> <code>{user_info['uid']}</code>\n<b>USERNAME:</b> @{user_info['username']}\n<b>NAME:</b> {user_info['first_name']}\n<b>TELEGRAM ID:</b> {user_info['user_id']}", buttons=verification_buttons, parse_mode='html')
    else:
        await event.respond(INVALID_UID_MESSAGE)

@client.on(events.CallbackQuery(data=lambda data: data.startswith(b'v_')))
async def handle_verification(event):
    _, uid, result = event.data.decode('utf-8').split('_')
    username, name, telegram_id, platform = "", "", "", ""  # Initialize variables to avoid undefined reference

    for user_info in user_data.values():
        if user_info.get('uid') == uid:
            username = user_info.get('username')
            name = user_info.get('first_name')
            telegram_id = user_info.get('user_id')
            platform = user_info.get('platform')
            break

    if result == 'yes':
        await client.send_message(telegram_id, VERIFICATION_SUCCESS)
        await client.send_message(ADMIN_ID, f"<b>Accepted ✅</b>\n\n<b>UID:</b> <code>{uid}</code>\n<b>Username:</b> @{username}\n<b>First Name:</b> {name}\n<b>Telegram ID:</b> {telegram_id}", parse_mode='html')
    else:
        await client.send_message(telegram_id, VERIFICATION_FAILED)
        await client.send_message(ADMIN_ID, f"<b>Rejected ❌</b>\n\n<b>UID:</b> <code>{uid}</code>\n<b>Username:</b> @{username}\n<b>First Name:</b> {name}\n<b>Telegram ID:</b> {telegram_id}", parse_mode='html')
    await event.delete()

async def forward_user_messages(event):
    chat_id = event.chat_id

    if chat_id not in user_data:
        user_data[chat_id] = {'user_id': event.sender_id, 'username': event.sender.username, 'first_name': event.sender.first_name}

    forward_msg = await client.forward_messages(ADMIN_ID, event.message.id, chat_id)
    #await client.send_message(ADMIN_ID, f"Reply to {event.sender.first_name} (ID: {event.sender_id}) by replying to this message.", reply_to=forward_msg)

async def handle_admin_reply(event):
    if event.is_reply and event.reply_to_msg_id:
        reply_to_msg = await client.get_messages(event.chat_id, ids=event.reply_to_msg_id)
        original_user_id = reply_to_msg.forward.sender_id if reply_to_msg.forward else None
        if original_user_id:
            await client.send_message(original_user_id, event.message)

client.start()
client.run_until_disconnected()
