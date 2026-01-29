# pyright: reportOptionalMemberAccess=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownMemberType=false

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from datetime import timedelta
import json, os, random, io, time, requests

# ================= ENV =================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN missing")

# ================= FILES =================

XP_FILE = "xp.json"
SETTINGS_FILE = "settings.json"
WARN_FILE = "warns.json"

# ================= INTENTS =================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="m;", intents=intents)
tree = bot.tree

# ================= JSON =================

def load_json(file, default):
    if not os.path.exists(file):
        return default
    with open(file, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file, data):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

xp_data = load_json(XP_FILE, {})
settings = load_json(SETTINGS_FILE, {})
warns = load_json(WARN_FILE, {})

# ================= SETTINGS =================

def get_guild_settings(gid):
    gid = str(gid)
    if gid not in settings:
        settings[gid] = {
            "welcome": None,
            "goodbye": None,
            "level": None,
            "modlog": None,
            "autoroles": [],
            "antilinks": False,
            "spam_limit": 5
        }
    return settings[gid]

# ================= MOD LOG =================

async def modlog(guild, embed):
    gs = get_guild_settings(guild.id)
    if gs["modlog"]:
        ch = guild.get_channel(gs["modlog"])
        if ch:
            await ch.send(embed=embed)

# ================= XP SYSTEM =================

XP_COOLDOWN = {}

def add_xp(uid, gid, amount):
    key = f"{gid}-{uid}"
    xp_data.setdefault(key, {"xp": 0, "level": 1})
    xp_data[key]["xp"] += amount
    needed = xp_data[key]["level"] * 100
    leveled = False
    if xp_data[key]["xp"] >= needed:
        xp_data[key]["xp"] -= needed
        xp_data[key]["level"] += 1
        leveled = True
    save_json(XP_FILE, xp_data)
    return leveled, xp_data[key]

# ================= WARN SYSTEM =================

def add_warn(gid, uid, reason):
    warns.setdefault(str(gid), {}).setdefault(str(uid), []).append(reason)
    save_json(WARN_FILE, warns)

def get_warns(gid, uid):
    return warns.get(str(gid), {}).get(str(uid), [])

# ================= AUTO MOD =================

spam_tracker = {}

def is_spam(uid, limit):
    now = time.time()
    spam_tracker.setdefault(uid, []).append(now)
    spam_tracker[uid] = [t for t in spam_tracker[uid] if now - t < 10]
    return len(spam_tracker[uid]) > limit

# ================= EVENTS =================

@bot.event
async def on_ready():
    await tree.sync()
    await bot.change_presence(activity=discord.Game(name="m;help | Arcane XP"))
    print(f"Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    gs = get_guild_settings(message.guild.id)

    # XP
    now = time.time()
    key = f"{message.guild.id}-{message.author.id}"
    if XP_COOLDOWN.get(key, 0) < now:
        XP_COOLDOWN[key] = now + 60
        leveled, data = add_xp(message.author.id, message.guild.id, random.randint(5, 10))
        if leveled and gs["level"]:
            ch = message.guild.get_channel(gs["level"])
            if ch:
                await ch.send(f"🎉 {message.author.mention} reached **Level {data['level']}**!")

    # Anti-links
    if gs["antilinks"] and ("http://" in message.content or "https://" in message.content):
        await message.delete()
        await message.channel.send(f"🚫 {message.author.mention} links are not allowed")
        await modlog(message.guild, discord.Embed(
            title="AutoMod | Link",
            description=f"{message.author} posted a link",
            color=discord.Color.red()
        ))
        return

    # Spam
    if is_spam(message.author.id, gs["spam_limit"]):
        until = discord.utils.utcnow() + timedelta(minutes=5)
        await message.author.timeout(until, reason="AutoMod: Spam")
        await modlog(message.guild, discord.Embed(
            title="AutoMod | Spam",
            description=f"{message.author} timed out",
            color=discord.Color.red()
        ))
        return

    # Fun triggers
    triggers = {
        "banana": "🍌 Secret banana unlocked!",
        "who asked": "💀 nobody",
        "skill issue": "🎯 confirmed skill issue"
    }

    for k, v in triggers.items():
        if k in message.content.lower():
            await message.channel.send(v)

    await bot.process_commands(message)

# ================= MOD COMMANDS =================

@tree.command(name="warn")
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(interaction, member: discord.Member, reason: str):
    add_warn(interaction.guild.id, member.id, reason)
    await modlog(interaction.guild, discord.Embed(
        title="⚠ Warn",
        description=f"{member} warned\nReason: {reason}",
        color=discord.Color.orange()
    ))
    await interaction.response.send_message(f"{member.mention} warned.")

@tree.command(name="warnings")
async def warnings(interaction, member: discord.Member):
    warns_list = get_warns(interaction.guild.id, member.id)
    msg = "\n".join(warns_list) or "No warnings."
    await interaction.response.send_message(msg)

@tree.command(name="timeout")
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(interaction, member: discord.Member, minutes: int, reason: str):
    until = discord.utils.utcnow() + timedelta(minutes=minutes)
    await member.timeout(until, reason=reason)
    await modlog(interaction.guild, discord.Embed(
        title="⏱ Timeout",
        description=f"{member} timed out\n{reason}",
        color=discord.Color.red()
    ))
    await interaction.response.send_message("Timed out.")

@tree.command(name="clear")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("Messages cleared.", ephemeral=True)

@tree.command(name="kick")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction, member: discord.Member, reason: str):
    await member.kick(reason=reason)
    await modlog(interaction.guild, discord.Embed(
        title="👢 Kick",
        description=f"{member} kicked\n{reason}",
        color=discord.Color.red()
    ))
    await interaction.response.send_message("Kicked.")

@tree.command(name="ban")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction, member: discord.Member, reason: str):
    await member.ban(reason=reason)
    await modlog(interaction.guild, discord.Embed(
        title="🔨 Ban",
        description=f"{member} banned\n{reason}",
        color=discord.Color.dark_red()
    ))
    await interaction.response.send_message("Banned.")

# ================= FUN COMMANDS =================

@tree.command(name="ping")
async def ping(interaction):
    await interaction.response.send_message(f"Pong! 🏓 {round(bot.latency * 1000)}ms")

@tree.command(name="coinflip")
async def coinflip(interaction):
    await interaction.response.send_message(random.choice(["🪙 Heads", "🪙 Tails"]))

@tree.command(name="roll")
async def roll(interaction, sides: int = 6):
    await interaction.response.send_message(f"🎲 Rolled: {random.randint(1, sides)}")

@tree.command(name="8ball")
async def eightball(interaction, question: str):
    responses = ["Yes", "No", "Maybe", "Definitely", "Absolutely not"]
    await interaction.response.send_message(f"🎱 {random.choice(responses)}")

# ================= RUN =================

bot.run(TOKEN)
