import telebot
from telebot import types
import requests
import uuid
import datetime
import json
import urllib3
import os
import time
import threading
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ============================================================
# ⚙️ သင့် VPS (၃) လုံး၏ အချက်အလက်များ
# ============================================================
BOT_TOKEN = "9058833367:AAGe4a5-PXaQAZJRnuy91AUc36U7zZH_2cM"
ADMIN_ID = 5617375002
ADMIN_CONTACT = "@Kenobe21" 

CHANNEL_LINK = "https://t.me/Skyblue021"
CHANNEL_USERNAME = "@Skyblue021"
BOT_LINK = "https://t.me/SkyBlueFreevpn_bot?start="

# 🚨 VPS ၁ (Port 2083)
VPS1_URL = "https://157.85.96.190:2083"
VPS1_PATH = "U6lL3EX7t2yq0q6"
VPS1_USER = "eYJmFn4UNl"
VPS1_PASS = "uLVwVpPaLb"
VPS1_IP = "157.85.96.190"
VPS1_PORT = "2083"
VPS1_INBOUND_ID = 1

# 🚨 VPS ၂ (Port 41899)
VPS2_URL = "https://119.10.142.16:41899"
VPS2_PATH = "kB8wYdqzZ5DlzpP"
VPS2_USER = "BVO9Zd0FtA"
VPS2_PASS = "JkbeqV9i0q"
VPS2_IP = "119.10.142.16"
VPS2_PORT = "41899"
VPS2_INBOUND_ID = 1

# 🚨 VPS ၃ (Port 2053)
VPS3_URL = "https://103.114.203.136:2053"
VPS3_PATH = "dLWnOXijDgbnRhW"
VPS3_USER = "eIIC3epKrY"
VPS3_PASS = "G6ifUF2Wi9"
VPS3_IP = "103.114.203.136"
VPS3_PORT = "2053"
VPS3_INBOUND_ID = 1

bot = telebot.TeleBot(BOT_TOKEN)

DB_FILE = "users_coin.json"
HISTORY_FILE = "purchase_history.json"
ACTIVE_USERS_FILE = "active_users.json"

users_db = {} 
purchase_history = [] 
active_users = set()

def load_data():
    global users_db, purchase_history, active_users
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                users_db = json.load(f)
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                purchase_history = json.load(f)
        if os.path.exists(ACTIVE_USERS_FILE):
            with open(ACTIVE_USERS_FILE, "r", encoding="utf-8") as f:
                active_users = set(json.load(f))
    except Exception as e:
        print(f"Data Load Error: {e}")

def save_data():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(users_db, f, ensure_ascii=False, indent=4)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(purchase_history, f, ensure_ascii=False, indent=4)
        with open(ACTIVE_USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(active_users), f)
    except Exception as e:
        print(f"Data Save Error: {e}")

load_data()

def check_join(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

def get_vps_details(vps_choice):
    if vps_choice == "1":
        return VPS1_URL, VPS1_PATH, VPS1_USER, VPS1_PASS, VPS1_IP, VPS1_PORT, VPS1_INBOUND_ID
    elif vps_choice == "2":
        return VPS2_URL, VPS2_PATH, VPS2_USER, VPS2_PASS, VPS2_IP, VPS2_PORT, VPS2_INBOUND_ID
    elif vps_choice == "3":
        return VPS3_URL, VPS3_PATH, VPS3_USER, VPS3_PASS, VPS3_IP, VPS3_PORT, VPS3_INBOUND_ID

def create_account_with_auto_switch(start_vps, username, days, gb):
    vps_order = [str(start_vps)]
    all_vps = ["1", "2", "3"]
    for v in all_vps:
        if v not in vps_order:
            vps_order.append(v)

    for current_vps in vps_order:
        success, result = auto_create_vless_account(current_vps, username, days, gb)
        
        if success:
            return True, result, current_vps 
            
        if result == "Duplicate":
            print(f"VPS {current_vps} တွင် '{username}' ရှိပြီးသားဖြစ်၍ နောက် VPS သို့ ပြောင်းမည်...")
            continue 
        else:
            return False, result, current_vps 
            
    return False, "VPS အားလုံးတွင် ဒီအကောင့်နာမည် ရှိနေပြီး ဖြစ်ပါသည်။", start_vps

def auto_create_vless_account(vps_choice, username, days, gb):
    try:
        url, path, user, pw, ip, port, inbound_id = get_vps_details(vps_choice)
        
        session = requests.Session()
        session.verify = False
        
        login_url = f"{url}/{path}/login"
        login_data = {"username": user, "password": pw}
        
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။"

        expire_time = int((datetime.datetime.now() + datetime.timedelta(days=days)).timestamp() * 1000)
        new_uuid = str(uuid.uuid4())
        
        total_gb_bytes = int(gb) * 1073741824 
        
        add_url = f"{url}/{path}/panel/api/inbounds/addClient"
        
        settings_data = {
            "clients": [{
                "id": new_uuid,
                "flow": "",
                "email": username,
                "limitIp": 1, 
                "totalGB": total_gb_bytes, 
                "expiryTime": expire_time,
                "enable": True,
                "tgId": "",
                "subId": username
            }]
        }
        
        payload = {
            "id": int(inbound_id),
            "settings": json.dumps(settings_data, ensure_ascii=True)
        }
        
        headers = {"Content-Type": "application/json"}
        response = session.post(add_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200 and response.json().get("success"):
            vless_link = f"vless://{new_uuid}@{ip}:{port}?type=ws&encryption=none&path={path if path else '/'}&host={ip}&security=none#{username}"
            return True, vless_link
        else:
            if "Duplicate email" in response.text:
                return False, "Duplicate"
            return False, f"Error: {response.text}"
            
    except Exception as e:
        return False, str(e)

def get_vps_clients(vps_choice):
    try:
        url, path, user, pw, ip, port, inbound_id = get_vps_details(vps_choice)
        
        session = requests.Session()
        session.verify = False
        
        login_url = f"{url}/{path}/login"
        login_data = {"username": user, "password": pw}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။"

        list_url = f"{url}/{path}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(inbound_id):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
        return True, clients
    except Exception as e:
        return False, str(e)

def delete_vless_account(vps_choice, username):
    try:
        url, path, user, pw, ip, port, inbound_id = get_vps_details(vps_choice)
        
        session = requests.Session()
        session.verify = False
        
        login_url = f"{url}/{path}/login"
        login_data = {"username": user, "password": pw}
        login_res = session.post(login_url, json=login_data, timeout=15)
        
        if login_res.status_code != 200 or not login_res.json().get("success"):
            return False, "Login မအောင်မြင်ပါ။"

        list_url = f"{url}/{path}/panel/api/inbounds/list"
        res_list = session.get(list_url, timeout=15)
        
        clients = []
        for inbound in res_list.json().get("obj", []):
            if inbound["id"] == int(inbound_id):
                settings = json.loads(inbound["settings"])
                clients = settings.get("clients", [])
                break
        
        target_uuid = None
        for client in clients:
            if client.get("email") == username:
                target_uuid = client.get("id")
                break
        
        if not target_uuid:
            return False, f"'{username}' ဆိုတဲ့ အကောင့်ကို VPS {vps_choice} မှာ ရှာမတွေ့ပါ။"

        del_url = f"{url}/{path}/panel/api/inbounds/{inbound_id}/delClient/{target_uuid}"
        res_del = session.post(del_url, timeout=15)
        
        if res_del.status_code == 200 and res_del.json().get("success"):
            return True, f"'{username}' အကောင့်ကို VPS {vps_choice} မှ အောင်မြင်စွာ ဖျက်လိုက်ပါပြီ။"
        else:
            return False, f"ဖျက်လို့မရပါ: {res_del.text}"
            
    except Exception as e:
        return False, str(e)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = str(message.from_user.id)
    active_users.add(user_id)
    save_data()

    if user_id not in users_db:
        users_db[user_id] = {"joined": False, "vpn": []}
    
    if users_db[user_id]["joined"]:
        show_main_menu(message.chat.id, user_id)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="📢 Channel Join ရန်", url=CHANNEL_LINK))
        markup.add(types.InlineKeyboardButton(text="✅ Join ပြီးပါပြီ", callback_data="check_join"))
        
        bot.send_message(
            message.chat.id, 
            "⚠️ **ကျွန်ုပ်တို့၏ ဝန်ဆောင်မှုကို အသုံးပြုရန် အောက်ပါ Channel ကို Join ပေးပါ။**\n\n"
            "Join ပြီးပါက '✅ Join ပြီးပါပြီ' ကို နှိပ်ပါ။", 
            reply_markup=markup, 
            parse_mode='Markdown'
        )

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def verify_join(call):
    user_id = str(call.from_user.id)
    if check_join(call.from_user.id):
        users_db[user_id]["joined"] = True
        save_data()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "အဆင်ပြေပါပြီ။ ကြိုဆိုပါတယ်။")
        show_main_menu(call.message.chat.id, user_id)
    else:
        bot.answer_callback_query(call.id, "❌ Channel ကို Join မထားရသေးပါဘူး။", show_alert=True)

def show_main_menu(chat_id, user_id):
    markup = types.InlineKeyboardMarkup()
    if int(user_id) == ADMIN_ID:
        markup.add(types.InlineKeyboardButton(text="🛠️ Admin - အကောင့်အသစ်ထုတ်ရန်", callback_data="admin_create"))
        markup.add(types.InlineKeyboardButton(text="📋 VPS အတွင်း အကောင့်စာရင်းကြည့်ရန်", callback_data="admin_check_vps_list"))
    
    markup.add(types.InlineKeyboardButton(text="🎁 သူငယ်ချင်းအတွက် လင့်ခ်တောင်းရန်", callback_data="buy_for_friend"))
    
    welcome_text = (
        "🌟 **Sky Blue VPN Bot မှ ကြိုဆိုပါတယ်** 🌟\n\n"
        "📌 **သူငယ်ချင်းကို ပေးသုံးရန်** - သူငယ်ချင်းရဲ့ Telegram ID ကို ထည့်ပြီး လင့်ခ်တောင်းနိုင်ပါတယ်။\n\n"
        f"👨‍💻 **အကူအညီလိုပါက:** {ADMIN_CONTACT}\n\n"
        "👇 ရွေးချယ်ပါ -"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "admin_create")
def admin_create_menu(call):
    if call.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 1 မှ ထုတ်မည်", callback_data="admin_vps_1"))
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 2 မှ ထုတ်မည်", callback_data="admin_vps_2"))
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 3 မှ ထုတ်မည်", callback_data="admin_vps_3"))
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_main"))
    
    bot.edit_message_text(
        "🛠️ **Admin - အကောင့်အသစ် ထုတ်ပေးရန်**\n\n"
        "ဘယ် VPS ကနေ ထုတ်ပေးမလဲ ရွေးချယ်ပါ -",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_vps_'))
def admin_process_vps(call):
    if call.from_user.id != ADMIN_ID: return
    vps_num = call.data.replace("admin_vps_", "")
    
    bot.edit_message_text(
        f"✅ VPS {vps_num} ကို ရွေးချယ်ပြီးပါပြီ။\n\n"
        "📝 ကျေးဇူးပြု၍ **အကောင့်နာမည်** (ဥပမာ - `myfriend`) ကို ရိုက်ထည့်ပါ -",
        call.message.chat.id, call.message.message_id
    )
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, admin_get_name, vps_num)

def admin_get_name(message, vps_num):
    account_name = message.text.strip()
    bot.reply_to(message, 
        f"✅ အကောင့်နာမည်: `{account_name}`\n\n"
        "📅 ကျေးဇူးပြု၍ **သက်တမ်း (ရက်)** ကို ရိုက်ထည့်ပါ (ဥပမာ - `30`) -",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(message, admin_get_days, vps_num, account_name)

def admin_get_days(message, vps_num, account_name):
    try:
        days = int(message.text.strip())
    except:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ ဂဏန်းသက်သက်သာ ရိုက်ထည့်ပါ (ဥပမာ - 30)။")
        bot.register_next_step_handler(message, admin_get_days, vps_num, account_name)
        return
        
    gb = days * 2
    bot.reply_to(message, "⏳ အကောင့်ဖန်တီးနေသည်...")
    
    success, result, final_vps = create_account_with_auto_switch(vps_num, account_name, days, gb)

    if success:
        bot.send_message(
            message.chat.id, 
            f"🎉 **အကောင့်ဖန်တီးပြီးပါပြီ!**\n\n"
            f"🌐 **ထုတ်ပေးလိုက်သည့် VPS:** VPS {final_vps}\n"
            f"📁 **အကောင့်:** `{account_name}`\n"
            f"⏳ **သက်တမ်း:** {days} ရက်\n"
            f"📦 **Data ပမာဏ:** {gb} GB\n\n"
            f"📄 **လင့်ခ်:**\n`{result}`", 
            parse_mode='Markdown'
        )
    else:
        bot.send_message(message.chat.id, f"⚠️ Error: အကောင့်ဖန်တီးမရပါ။\n{result}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_check_vps_list")
def admin_check_vps_list(call):
    if call.from_user.id != ADMIN_ID: return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 1 စစ်မည်", callback_data="check_list_1"))
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 2 စစ်မည်", callback_data="check_list_2"))
    markup.add(types.InlineKeyboardButton(text="🇹🇭 VPS 3 စစ်မည်", callback_data="check_list_3"))
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_main"))
    
    bot.edit_message_text(
        "📋 **ဘယ် VPS ရဲ့ အကောင့်စာရင်းကို စစ်မလဲ?**",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('check_list_'))
def admin_process_check_list(call):
    if call.from_user.id != ADMIN_ID: return
    vps_num = call.data.replace("check_list_", "")
    
    bot.edit_message_text(f"⏳ VPS {vps_num} ရဲ့ အကောင့်စာရင်းကို ဆွဲယူနေသည်...", call.message.chat.id, call.message.message_id)
    
    success, clients = get_vps_clients(vps_num)
    
    if not success:
        bot.edit_message_text(f"❌ Error: {clients}", call.message.chat.id, call.message.message_id)
        return
        
    if not clients:
        bot.edit_message_text(f"📁 VPS {vps_num} မှာ VPN အကောင့် မရှိပါ။", call.message.chat.id, call.message.message_id)
        return
        
    msg = f"📋 **VPS {vps_num} အတွင်း အကောင့်စာရင်း (စုစုပေါင်း {len(clients)} ခု)**\n\n"
    for i, c in enumerate(clients, 1):
        email = c.get("email", "Unknown")
        expiry = c.get("expiryTime", 0)
        if expiry == 0:
            expire_date = "မကုန်ဆုံးပါ"
        else:
            exp_utc = datetime.datetime.fromtimestamp(expiry / 1000, tz=datetime.timezone.utc)
            exp_mm = exp_utc + datetime.timedelta(hours=6, minutes=30)
            expire_date = exp_mm.strftime('%Y-%m-%d %H:%M')
        msg += f"{i}. `{email}` (ကုန်ဆုံး: {expire_date})\n"
        
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f"🗑️ VPS {vps_num} မှ အကောင့်ဖျက်ရန်", callback_data=f"delete_client_{vps_num}"))
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="admin_check_vps_list"))
    
    if len(msg) > 4000:
        for i in range(0, len(msg), 4000):
            bot.send_message(call.message.chat.id, msg[i:i+4000], parse_mode='Markdown')
        bot.send_message(call.message.chat.id, "ဖျက်လိုပါက အောက်ပါခလုတ်ကို နှိပ်ပါ -", reply_markup=markup)
    else:
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_client_'))
def admin_delete_client_prompt(call):
    if call.from_user.id != ADMIN_ID: return
    
    vps_num = call.data.replace("delete_client_", "")
    
    bot.send_message(
        call.message.chat.id, 
        f"🗑️ **VPS {vps_num}** မှ ဖျက်လိုသော အကောင့်နာမည်ကို ရိုက်ထည့်ပါ -"
    )
    
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, admin_delete_client, vps_num)

def admin_delete_client(message, vps_num):
    account_name = message.text.strip()
    bot.reply_to(message, f"⏳ '{account_name}' ကို VPS {vps_num} မှ ဖျက်နေသည်...")
    
    success, result = delete_vless_account(vps_num, account_name)
    
    if success:
        bot.send_message(message.chat.id, f"✅ {result}")
    else:
        bot.send_message(message.chat.id, f"⚠️ {result}")

@bot.callback_query_handler(func=lambda call: call.data == "buy_for_friend")
def buy_for_friend_menu(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text="🔙 နောက်သို့", callback_data="back_main"))
    
    bot.edit_message_text(
        f"🎁 **သူငယ်ချင်းအတွက် လင့်ခ်တောင်းရန်**\n\n"
        "📝 ကျေးဇူးပြု၍ သူငယ်ချင်းရဲ့ **Telegram ID** ကို ရိုက်ထည့်ပါ (ဥပမာ - `8823368996`) -",
        call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown'
    )
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, get_friend_id)

def get_friend_id(message):
    user_id = str(message.from_user.id)
    friend_id = message.text.strip()
    
    bot.reply_to(message, f"✅ သင့်တောင်းခံမှုကို လက်ခံရရှိပါပြီ။\n\nAdmin က သင့်သူငယ်ချင်း (ID: `{friend_id}`) အတွက် အကောင့်ထုတ်ပေးပါလိမ့်မယ်။", parse_mode='Markdown')
    
    admin_markup = types.InlineKeyboardMarkup()
    admin_markup.add(types.InlineKeyboardButton(text="🛠️ ယခု အကောင့်ထုတ်ပေးမည်", callback_data="admin_create"))
    
    bot.send_message(
        ADMIN_ID, 
        f"🔔 **သူငယ်ချင်းအတွက် လင့်ခ်တောင်းခံမှု**\n\n"
        f"👤 တောင်းခံသူ: {message.from_user.full_name} (ID: {user_id})\n"
        f"🎯 သူငယ်ချင်း ID: `{friend_id}`",
        reply_markup=admin_markup,
        parse_mode='Markdown'
    )
    try:
        bot.send_message(friend_id, "🎉 သင့်သူငယ်ချင်းက သင့်အတွက် VPN လင့်ခ်တစ်ခု တောင်းခံထားပါတယ်။ Admin က မကြာမီ ပို့ပေးပါလိမ့်မယ်။")
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_main(call):
    user_id = str(call.from_user.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_main_menu(call.message.chat.id, user_id)

@bot.message_handler(commands=['help'])
def help_command(message):
    if message.from_user.id != ADMIN_ID: 
        bot.reply_to(message, "❌ ဒီ Command ကို Admin ပဲ အသုံးပြုခွင့်ရှိပါတယ်။")
        return
        
    help_text = (
        "🤖 **Admin အတွက် အသုံးပြုနိုင်သော Command များ**\n\n"
        "🔹 **/help** - ဒီစာမျက်နှာကို ဖွင့်ရန်။\n\n"
        "🔹 **/online** - လက်ရှိ Bot ကို သုံးနေတဲ့ လူဦးရေကို ကြည့်ရန်။\n\n"
        "🔹 **/history** - ဝယ်ယူမှု မှတ်တမ်းများကို ကြည့်ရန်။"
    )
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['online'])
def online_users_command(message):
    if message.from_user.id != ADMIN_ID: return
    
    total_users = len(users_db)
    online_count = len(active_users)
    
    text = (
        "📊 **Bot အသုံးပြုသူ အခြေအနေ**\n\n"
        f"👥 **စုစုပေါင်း အသုံးပြုသူ:** {total_users} ယောက်\n"
        f"🟢 **လက်ရှိ အွန်လိုင်း (ရောက်သုံးနေသူ):** {online_count} ယောက်"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['history'])
def history_command(message):
    if message.from_user.id != ADMIN_ID: return
    if not purchase_history:
        bot.reply_to(message, "📁 ဝယ်ယူမှု မှတ်တမ်း မရှိသေးပါ။")
        return
        
    msg = "📋 **ဝယ်ယူမှု မှတ်တမ်း (မကြာသေးမီက)**\n\n"
    for item in purchase_history[-20:]:
        msg += (
            f"👤 User: `{item['user_id']}`\n"
            f"🌐 VPS: {item.get('vps', 'N/A')}\n"
            f"🎫 အကောင့်: `{item['username']}`\n"
            f"📅 ရက်: {item['days']} ရက် | 📦 Data: {item.get('gb', 'N/A')} GB\n"
            f"🕒 {item['date']}\n"
            f"--- --- ---\n"
        )
        
    if len(msg) > 4000:
        for i in range(0, len(msg), 4000):
            bot.send_message(message.chat.id, msg[i:i+4000], parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, msg, parse_mode='Markdown')

if __name__ == '__main__':
    print("🤖 Sky Blue Multi-VPS Bot စတင်နေသည်...")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Error တက်သွားပါသည်: {e}")
            print("5 စက္ကန့်အတွင်း ပြန်လည် စတင်ပါမည်...")
            time.sleep(5)

