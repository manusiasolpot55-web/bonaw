import httpx
import random
import asyncio

from pyrogram import (
    Client,
    filters,
)
from pyrogram.types import Message

from clients import navy
from helpers import CMD
from database import dB, state


__MODULES__ = "AI chat bot"
__HELP__ = """<blockquote>Command Help **AI chat bot**</blockquote>
<blockquote expandable>--**Moderation Commands**--

    **Turn on or off and list chat group**
        `{0}chatbot` (on/off/list)
    **Function add and remove or list user blacklist**
        `{0}aichatbl` (add/remove/list)
        
<b>   {1}</b>
"""


API_URL = "https://api.maelyn.eu/api/ai/chatgpt"
API_KEY = "sk_ms_d7055ecce43fc610ddc512040dd3edd4dd00c10a8e19f930"

TRIGGER_WORDS = ["bot", "ubot", "prem", "nokos"]


async def ai_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False


async def chatbot_manager(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /chatbot [on/off/list]")

    sub_command = message.command[1].lower()
    chat_id = message.chat.id
    
    sts = await dB.get_list_from_var(client.me.id, "AI_CHAT_BOT") or []

    if sub_command in ["on", "off"]:
        if not await ai_admin(client, chat_id, message.from_user.id):
            return await message.reply_text("Anda bukan admin di grup ini!")

    if sub_command == "on":
        if chat_id in sts:
            return await message.reply_text("AI Chatbot sudah aktif di grup ini.")
            
        await dB.add_to_var(client.me.id, "AI_CHAT_BOT", chat_id)
        await message.reply_text("AI Chatbot berhasil diaktifkan.")

    elif sub_command == "off":
        if chat_id not in sts:
            return await message.reply_text("AI Chatbot belum aktif di grup ini.")
            
        await dB.remove_from_var(client.me.id, "AI_CHAT_BOT", chat_id)
        await message.reply_text("AI Chatbot berhasil dinonaktifkan.")

    elif sub_command == "list":
        if not sts:
            return await message.reply_text("Tidak ada grup yang mengaktifkan AI.")
        
        text = "Daftar grup yang mengaktifkan AI:\n\n"
        for gid in sts:
            try:
                chat = await client.get_chat(gid)
                text += f"• {chat.title} (`{gid}`)\n"
            except:
                text += f"• Grup tidak ditemukan (`{gid}`)\n"
        await message.reply_text(text)
        
    else:
        await message.reply_text("Perintah tidak dikenal. Gunakan: /chatbot [on/off/list]")


async def aichatbl_manager(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("Gunakan: /aichatbl [add/remove/list]")

    sub = message.command[1].lower()
    sts = await dB.get_list_from_var(client.me.id, "AI_BL_USER") or []

    if sub == "add":
        target_id = message.reply_to_message.from_user.id if message.reply_to_message else (int(message.command[2]) if len(message.command) > 2 else None)
        if not target_id: return await message.reply_text("Reply pesan atau masukkan user_id.")
        
        if target_id in sts:
            return await message.reply_text("User ini sudah diblokir.")
        
        await dB.add_to_var(client.me.id, "AI_BL_USER", target_id)
        return await message.reply_text(f"Berhasil memblokir user `{target_id}`")

    elif sub == "remove":
        target_id = message.reply_to_message.from_user.id if message.reply_to_message else (int(message.command[2]) if len(message.command) > 2 else None)
        if not target_id: return await message.reply_text("Reply pesan atau masukkan user_id.")
        
        if target_id not in sts:
            return await message.reply_text("User ini tidak ada dalam daftar blokir.")
        
        await dB.remove_from_var(client.me.id, "AI_BL_USER", target_id)
        return await message.reply_text(f"User `{target_id}` telah dibuka blokirnya.")

    elif sub == "list":
        if not sts: return await message.reply_text("Daftar blokir kosong.")
        
        text = "Daftar user yang diblokir AI:\n\n"
        for uid in sts:
            try:
                user = await client.get_users(uid)
                text += f"• {user.first_name} (`{uid}`)\n"
            except:
                text += f"• User tidak ditemukan (`{uid}`)\n"
        return await message.reply_text(text)


async def ai_response(_: Client, message: Message):
    user_input = message.text
    
    active_groups = await dB.get_list_from_var(client.me.id, "AI_CHAT_BOT") or []
    if chat_id not in active_groups:
        return

    blacklisted_users = await dB.get_list_from_var(client.me.id, "AI_BL_USER") or []
    if user_id in blacklisted_users:
        return

    await client.send_chat_action(chat_id, "typing")
    await asyncio.sleep(random.uniform(1.0, 2.0))

    if any(word in user_input for word in TRIGGER_WORDS):
        return await message.reply_text("Beli di @herololl serba murah.")

    headers = {
        "x-maelyn-auth": API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system", 
                "content": (
                    "Kamu adalah six."
                    "Sifatmu: tengil, ketus, tidak peduli."
                    "ATURAN MUTLAK:"
                    "1) Balas 3-5 kata saja."
                    "2) DILARANG keras pakai tanda tanya (?) dan emoji."
                    "3) Bahasa gaul/kasual."
                    "4) Jangan ramah."        
                )
            },
            {
                "role": "user", 
                "content": user_input
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as http:
            response = await http.post(
                API_URL,
                json=payload,
                headers=headers,
                timeout=5.0
            )
            data = response.json()

            if data.get("success"):
                reply_text = data.get("result", {}).get("text", "?")
                await message.reply_text(reply_text)
            else:
                fallback = [
                    "Mager jawabnya.",
                    "Bahas lain saja.",
                    "Gak guna banget.",
                    "Skip aja lah.",
                    "Pikir sendiri sana."
                ]
                await message.reply_text(random.choice(fallback))
            
    except Exception:
        await message.reply_text("Server tidak merespons. Berisik.")


@CMD.NO_CMD("AI_CHAT_BOT", navy)
async def _(client, message):
    return await ai_response(client, message)


@CMD.UBOT("chatbot")
@CMD.ONLY_GROUP
async def _(client, message):
    return await chatbot_manager(client, message)


@CMD.UBOT("aichatbl")
@CMD.ONLY_GROUP
async def _(client, message):
    return await aichatbl_manager(client, message)

   
