import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

# ------------------------------
# 🔧 파일 초기화
# ------------------------------
def load_json(filename, default):
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            json.dump(default, f)
    with open(filename, 'r') as f:
        return json.load(f)

user_points = load_json("user_points.json", {})
shop = load_json("shop.json", {})
config = load_json("config.json", {"points_per_message": 1})

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

# ------------------------------
# 📈 채팅 감지 → 포인트 적립
# ------------------------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    user_id = str(message.author.id)
    user_points[user_id] = user_points.get(user_id, 0) + config["points_per_message"]
    save_json("user_points.json", user_points)
    await bot.process_commands(message)

# ------------------------------
# 🎁 포인트 확인
# ------------------------------

@bot.command()
async def points(ctx):
    user_id = str(ctx.author.id)
    points = user_points.get(user_id, 0)
    await ctx.send(f"{ctx.author.mention} has {points} points.")

# ------------------------------
# 🛍️ 역할 구매
# ------------------------------
@bot.command(name="buy")
async def buy_role(ctx, role_name):
    user_id = str(ctx.author.id)

    if role_name not in shop:
        await ctx.send("This role is not available in the shop.")
        return

    price = shop[role_name]
    points = user_points.get(user_id, 0)

    if points < price:
        await ctx.send(f"You need {price} points to buy `{role_name}`, but you have only {points}.")
        return

    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send("The role exists in the shop, but not in this server.")
        return

    await ctx.author.add_roles(role)
    user_points[user_id] -= price
    save_json("user_points.json", user_points)
    await ctx.send(f"You have successfully purchased the `{role_name}` role for {price} points!")

# ------------------------------
# 🛒 역할 등록 (관리자만)
# ------------------------------

@bot.command(name="shop_role")
@commands.has_permissions(administrator=True)
async def shop_role(ctx, role_name, price: int):
    shop[role_name] = price
    save_json("shop.json", shop)
    await ctx.send(f"Role `{role_name}` registered for {price} points.")

# ------------------------------
# ⚙️ 포인트 적립량 설정 (관리자만)
# ------------------------------

@bot.command(name="set_earning")
@commands.has_permissions(administrator=True)
async def set_earning(ctx, points: int):
    config["points_per_message"] = points
    save_json("config.json", config)
    await ctx.send(f"Earning rate set to {points} points per message.")

# ------------------------------
# 봇 시작
# ------------------------------
bot.run("YOUR_DISCORD_BOT_TOKEN")