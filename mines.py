import discord
from discord.ext import commands
from discord import app_commands
import os
import json
import random
import asyncio
from dotenv import load_dotenv

# --------------------
# Setup
# --------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="m;", intents=intents, help_command=None)
tree = bot.tree

STATUSES = [
    "/help for commands",
    "🤗 Giving free hugs",
    "👉 Poking responsibly",
    "💖 Shipping users",
    "🎮 Fun commands online"
]

async def status_rotator():
    await bot.wait_until_ready()
    i = 0
    while not bot.is_closed():
        activity = discord.CustomActivity(name=STATUSES[i])
        await bot.change_presence(
            status=discord.Status.online,
            activity=activity
        )
        i = (i + 1) % len(STATUSES)
        await asyncio.sleep(30)  # rotate every 30 seconds

# --------------------
# ACTION SYSTEM
# --------------------
ACTIONS = {
    "poke": {
        "emoji": "👉",
        "color": discord.Color.purple(),
        "gifs": [
            "https://media.tenor.com/8n9m9gZyYgUAAAAC/anime-poke.gif",
            "https://media.tenor.com/kK6v0Z7Yt0QAAAAC/poke-anime.gif",
            "https://media.tenor.com/4uEw0G5ZK1QAAAAC/poke-cute.gif",
            "https://media.tenor.com/y8Z0zXzX5N8AAAAC/anime-poke.gif",
            "https://media.tenor.com/Lz1v9U7R8nQAAAAC/anime-poke.gif"
        ]
    },

    "kiss": {
        "emoji": "💋",
        "color": discord.Color.red(),
        "gifs": [
            "https://media.tenor.com/0AVbKGY_MxMAAAAC/anime-kiss.gif",
            "https://media.tenor.com/2VZ8sZkWbFQAAAAC/kiss-anime.gif",
            "https://media.tenor.com/9KQK7XyZ7X0AAAAC/anime-kiss.gif",
            "https://media.tenor.com/Yu7F8KQk0oUAAAAC/anime-kiss.gif",
            "https://media.tenor.com/F8Z7qXxZ3S4AAAAC/anime-kiss.gif"
        ]
    },

    "pat": {
        "emoji": "🫳",
        "color": discord.Color.green(),
        "gifs": [
            "https://media.tenor.com/2roX3uxz_68AAAAC/anime-head-pat.gif",
            "https://media.tenor.com/FpF3X7XoH7UAAAAC/pat-anime.gif",
            "https://media.tenor.com/7l3n6bYqJ6AAAAAC/anime-pat.gif",
            "https://media.tenor.com/0GJYx2x8cK0AAAAC/anime-headpat.gif",
            "https://media.tenor.com/2mF6bZ9x8fUAAAAC/anime-pat.gif"
        ]
    },

    "punch": {
        "emoji": "👊",
        "color": discord.Color.orange(),
        "gifs": [
            "https://media.tenor.com/l1xTnYH9D7sAAAAC/anime-punch.gif",
            "https://media.tenor.com/0vR2rjv4JkUAAAAC/punch-anime.gif",
            "https://media.tenor.com/Ws6Dm1ZWkWEAAAAC/anime-punch.gif",
            "https://media.tenor.com/4MGCj5x8gHAAAAAC/anime-punch.gif",
            "https://media.tenor.com/JG9m7cY2Zp8AAAAC/anime-punch.gif"
        ]
    },

    "bite": {
        "emoji": "🦷",
        "color": discord.Color.dark_red(),
        "gifs": [
            "https://media.tenor.com/1Yw3sPp5kYcAAAAC/anime-bite.gif",
            "https://media.tenor.com/q8K5J5K0YgAAAAAC/anime-bite.gif",
            "https://media.tenor.com/0m7X8bZ8sLAAAAAC/anime-bite.gif",
            "https://media.tenor.com/5Zc8Z9Z9Z9AAAAC/anime-bite.gif",
            "https://media.tenor.com/8n9m9gZyYgUAAAAC/anime-bite.gif"
        ]
    },

    "hug": {
        "emoji": "🤗",
        "color": discord.Color.blurple(),
        "gifs": [
            "https://media.tenor.com/Ct6J9Y6iJb8AAAAC/anime-hug.gif",
            "https://media.tenor.com/7l3n6bYqJ6AAAAAC/anime-hug.gif",
            "https://media.tenor.com/0GJYx2x8cK0AAAAC/anime-hug.gif",
            "https://media.tenor.com/2mF6bZ9x8fUAAAAC/anime-hug.gif",
            "https://media.tenor.com/x7yKZ9Z8AAAAC/anime-hug.gif"
        ]
    },

    "slap": {
        "emoji": "🖐️",
        "color": discord.Color.dark_orange(),
        "gifs": [
            "https://media.tenor.com/Ws6Dm1ZWkWEAAAAC/anime-slap.gif",
            "https://media.tenor.com/4MGCj5x8gHAAAAAC/anime-slap.gif",
            "https://media.tenor.com/5u3J1Y5nX0QAAAAC/slap-anime.gif",
            "https://media.tenor.com/JG9m7cY2Zp8AAAAC/anime-slap.gif",
            "https://media.tenor.com/8n9m9gZyYgUAAAAC/anime-slap.gif"
        ]
    }
}
# --------------------
# STORAGE
# --------------------
def load_action_data(action):
    file = f"{action}.json"
    if not os.path.exists(file):
        return {}
    with open(file, "r") as f:
        return json.load(f)

def save_action_data(action, data):
    with open(f"{action}.json", "w") as f:
        json.dump(data, f, indent=4)

# --------------------
# CORE ACTION HANDLER
# --------------------
async def perform_action(author, target, action_name, send_func):
    if target.id == author.id:
        await send_func("😅 You can’t do that to yourself!")
        return

    data = load_action_data(action_name)
    uid = str(target.id)
    data[uid] = data.get(uid, 0) + 1
    save_action_data(action_name, data)

    action = ACTIONS[action_name]

    embed = discord.Embed(
        title=f"{action['emoji']} {action_name.upper()}!",
        description=(
            f"**{author.name}** {action_name}ed **{target.name}**!\n\n"
            f"📊 **Total times {action_name}ed:** `{data[uid]}`"
        ),
        color=action["color"]
    )
    embed.set_image(url=random.choice(action["gifs"]))
    embed.set_footer(text="Fun commands 🎮")

    await send_func(embed=embed)

# --------------------
# ACTION COMMAND FACTORY (FIXED)
# --------------------
def create_action_command(action_name: str):
    @app_commands.command(
        name=action_name,
        description=f"{action_name.capitalize()} someone"
    )
    async def action_cmd(
        interaction: discord.Interaction,
        user: discord.User
    ):
        await perform_action(
            interaction.user,
            user,
            action_name,
            interaction.response.send_message
        )

    return action_cmd

for action in ACTIONS.keys():
    tree.add_command(create_action_command(action))

# --------------------
# SHIP STORAGE
# --------------------
SHIP_FILE = "ships.json"

def load_ships() -> dict:
    if not os.path.exists(SHIP_FILE):
        return {}
    with open(SHIP_FILE, "r") as f:
        return json.load(f)

def save_ships(data: dict) -> None:
    with open(SHIP_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_ship_key(user1_id: int, user2_id: int) -> str:
    return "-".join(map(str, sorted((user1_id, user2_id))))

# --------------------
# FUN SLASH COMMANDS
# --------------------
@tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

@tree.command(name="coinflip")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 **{random.choice(['Heads', 'Tails'])}**")

@tree.command(name="roll")
async def roll(interaction: discord.Interaction, max: int = 100):
    await interaction.response.send_message(f"🎲 You rolled **{random.randint(1, max)}**")

@tree.command(name="dice")
async def dice(interaction: discord.Interaction):
    await interaction.response.send_message(f"🎲 Dice rolled: **{random.randint(1,6)}**")

@tree.command(name="8ball")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        # Positive
        "It is certain",
        "It is decidedly so",
        "Without a doubt",
        "Yes – definitely",
        "You may rely on it",
        "As I see it, yes",
        "Most likely",
        "Outlook good",
        "Yes",
        "Signs point to yes",

        # Neutral / Unclear
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Maybe",
        "Hard to say",
        "Could go either way",

        # Negative
        "Don’t count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
        "Absolutely not",
        "No chance"
    ]

    await interaction.response.send_message(f"🎱 **Question:** {question}\n**Answer:** {random.choice(responses)}")

@tree.command(name="joke")
async def joke(interaction: discord.Interaction):
    jokes = [
        # Tech
        "Why did the dev quit? Too many bugs 🐛",
        "I told my PC a joke… it froze 💀",
        "My code works and I don’t know why 😎",
        "Debugging is just arguing with yourself",
        "I pressed F5 and hoped for the best 🙏",

        # Gaming
        "Lag is just the game giving you time to think 🎮",
        "Skill issue? No. Server issue.",
        "I didn’t lose — I was gathering data",
        "NPCs have better pathfinding than me",
        "Tutorial boss hardest boss",

        # Life
        "I need a 6-month break after a 10-minute task",
        "I’m not lazy, I’m on energy-saving mode 🔋",
        "Sleep is just a free trial I never get",
        "I put something somewhere safe… it’s gone forever",
        "Why is doing nothing so exhausting?",

        # Chaos / Random
        "I stared at the fridge for food ideas. Still hungry.",
        "I blinked and the day was over",
        "Nothing is on fire — suspicious",
        "This joke was loading… please wait ⏳",
        "I had a thought. It left."
    ]

    await interaction.response.send_message(random.choice(jokes))

@tree.command(name="roast")
async def roast(interaction: discord.Interaction, user: discord.User):
    roasts = [
        # Tech
        "Built like unoptimized code 💀",
        "Runs on Internet Explorer energy 🐌",
        "More bugs than a beta release 🐛",
        "One typo away from disaster",
        "Even Stack Overflow sighed",

        # Gaming
        "Tutorial boss energy",
        "Would lose a fight with a loading screen ⏳",
        "Lag didn’t save you this time",
        "NPC behavior detected",
        "Still waiting for the respawn",

        # Life
        "Has alarm clocks but no motivation ⏰",
        "Survives entirely on vibes",
        "Confidence of someone who didn’t read the instructions",
        "Built different… unfortunately",
        "Runs on caffeine and bad decisions",

        # Chaos
        "If confusion were a sport, you’d medal",
        "Main character in the wrong timeline",
        "No thoughts, just vibes",
        "Even chaos is confused",
        "This roast was handcrafted 🧯"
    ]

    await interaction.response.send_message(f"🔥 {user.mention} {random.choice(roasts)}")

@tree.command(name="ship", description="Ship two users together 💖")
async def ship(interaction: discord.Interaction, user1: discord.User, user2: discord.User):
    ships = load_ships()
    key = get_ship_key(user1.id, user2.id)

    if key not in ships:
        ships[key] = random.randint(0, 100)
        save_ships(ships)

    percent = ships[key]

    if percent >= 80:
        status = "💞 Perfect match!"
    elif percent >= 50:
        status = "💖 Looking good!"
    elif percent >= 30:
        status = "💔 Could work..."
    else:
        status = "💀 Uh oh..."

    embed = discord.Embed(
        title="💘 Ship Result",
        description=f"❤️ **{percent}%** ❤️\n{status}",
        color=discord.Color.pink()
    )

    embed.add_field(name="👤 User 1", value=user1.mention, inline=True)
    embed.add_field(name="👤 User 2", value=user2.mention, inline=True)

    embed.set_thumbnail(url=user1.display_avatar.url)
    embed.set_author(name=user2.name, icon_url=user2.display_avatar.url)
    embed.set_footer(text="🧪 Ship scores are persistent")

    await interaction.response.send_message(embed=embed)

@tree.command(name="choose")
async def choose(interaction: discord.Interaction, choices: str):
    options = [c.strip() for c in choices.split(",")]
    await interaction.response.send_message(f"🤔 I choose **{random.choice(options)}**")

@tree.command(name="reverse")
async def reverse(interaction: discord.Interaction, text: str):
    await interaction.response.send_message(text[::-1])

@tree.command(name="rate")
async def rate(interaction: discord.Interaction, thing: str):
    await interaction.response.send_message(f"⭐ **{thing}** is rated **{random.randint(0,10)}/10**")

@tree.command(name="rps")
async def rps(interaction: discord.Interaction, choice: str):
    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)
    await interaction.response.send_message(f"🪨📄✂️ You: **{choice}** | Bot: **{bot_choice}**")

@tree.command(name="number")
async def number(interaction: discord.Interaction):
    await interaction.response.send_message(f"🔢 Random number: **{random.randint(0, 9999)}**")

# --------------------
# HELP COMMAND
# --------------------
@tree.command(name="help", description="Show all bot commands")
async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(title="🤖 Bot Commands", color=discord.Color.blurple())

    embed.add_field(
        name="🎭 Actions",
        value=", ".join(f"`/{a}`" for a in ACTIONS),
        inline=False
    )

    embed.add_field(
        name="🎮 Fun",
        value=(
            "`/ping` `/coinflip` `/roll` `/dice` `/8ball` `/joke` `/roast`\n"
            "`/ship` `/choose` `/reverse` `/rate` `/number` `/rps`"
        ),
        inline=False
    )

    await interaction.response.send_message(embed=embed)

# --------------------
# READY
# --------------------
@bot.event
async def on_ready():
    bot.loop.create_task(status_rotator())
    await tree.sync()
    print(f"Logged in as {bot.user}")

bot.run(TOKEN)


