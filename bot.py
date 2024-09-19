import discord
from discord.ext import commands, tasks
import json
import random
import time

# Set up the bot and command prefix
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Load or initialize cheese data
def load_data():
    try:
        with open('cheese_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(data):
    with open('cheese_data.json', 'w') as f:
        json.dump(data, f, indent=4)

# Load the cheese data on startup
cheese_data = load_data()

# Function to get a user's cheese count
def get_cheese(user_id):
    return cheese_data.get(str(user_id), {"cheese": 0, "last_collect": 0, "last_steal": 0})

# Command: !collect - Collect cheese once a day
@bot.command(name="collect")
async def collect(ctx):
    user = ctx.author
    user_id = str(user.id)
    user_data = get_cheese(user_id)

    # Cooldown of 24 hours (10 seconds)
    if time.time() - user_data['last_collect'] < 10:
        await ctx.send(f"🧀 You need to wait before collecting more cheese, {user.name}!")
        return

    # Add random cheese between 1 and 10
    collected_cheese = random.randint(1, 100)
    user_data['cheese'] += collected_cheese
    user_data['last_collect'] = time.time()

    # Update cheese data and save it
    cheese_data[user_id] = user_data
    save_data(cheese_data)

    await ctx.send(f"🧀 {user.name} collected {collected_cheese} cheese! You now have {user_data['cheese']} 🧀.")

# Command: !steal - Attempt to steal cheese from another user
@bot.command(name="steal")
async def steal(ctx, target: discord.Member):
    user = ctx.author
    user_id = str(user.id)
    target_id = str(target.id)

    # Self-stealing check
    if user_id == target_id:
        await ctx.send("🧀 You can't steal cheese from yourself!")
        return

    # Get user and target data
    user_data = get_cheese(user_id)
    target_data = get_cheese(target_id)

    # Cooldown of 1 hour (10 seconds)
    if time.time() - user_data['last_steal'] < 10:
        await ctx.send(f"🧀 You need to wait before stealing again, {user.name}!")
        return

    # Check if the target has cheese
    if target_data['cheese'] == 0:
        await ctx.send(f"🧀 {target.name} has no cheese to steal!")
        return

    # Steal success/failure with 50% chance
    if random.random() < 0.5:
        stolen_cheese = random.randint(1, min(10, target_data['cheese']))
        target_data['cheese'] -= stolen_cheese
        user_data['cheese'] += stolen_cheese
        user_data['last_steal'] = time.time()

        # Update cheese data and save it
        cheese_data[user_id] = user_data
        cheese_data[target_id] = target_data
        save_data(cheese_data)

        await ctx.send(f"🧀 {user.name} successfully stole {stolen_cheese} cheese from {target.name}! You now have {user_data['cheese']} 🧀.")
    else:
        user_data['last_steal'] = time.time()
        cheese_data[user_id] = user_data
        save_data(cheese_data)
        await ctx.send(f"🧀 {user.name} failed to steal cheese from {target.name}. Better luck next time!")

# Command: !cheese - Display user's cheese balance
@bot.command(name="cheese")
async def cheese(ctx, target: discord.Member = None):
    # If no target is provided, default to the command sender (ctx.author)
    if target is None:
        target = ctx.author

    # Fetch the cheese data for the target user
    target_data = get_cheese(str(target.id))

    # Send a message showing the cheese count
    await ctx.send(f"🧀 {target.name} has {target_data['cheese']} cheese.")


# Command: !leaderboard - Show top cheese collectors
@bot.command(name="leaderboard")
async def leaderboard(ctx):
    sorted_data = sorted(cheese_data.items(), key=lambda x: x[1]['cheese'], reverse=True)[:10]
    leaderboard_text = "🧀 **Cheese Leaderboard** 🧀\n"
    for i, (user_id, data) in enumerate(sorted_data):
        user = await bot.fetch_user(int(user_id))
        leaderboard_text += f"{i+1}. {user.name} - {data['cheese']} cheese\n"
    await ctx.send(leaderboard_text)

# Bot ready event
@bot.event
async def on_ready():
    print(f'🧑‍💻 Bot is online as {bot.user}! Cheese heist is on!')

# Run the bot (replace 'YOUR_BOT_TOKEN' with your actual bot token)
bot.run('MTI4Mjg4NDg0MDgzNTc3NjU2Mg.Gqwzvy.Dr7eOtcoNo0P3KBbK9kEGCoK7fhHWbBEA1xI7g')
