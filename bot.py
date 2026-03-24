import discord
from discord.ext import commands
from discord import app_commands
import json
import datetime
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load warnings
if not os.path.exists("warnings.json"):
    with open("warnings.json", "w") as f:
        json.dump({}, f)

def load_warnings():
    with open("warnings.json", "r") as f:
        return json.load(f)

def save_warnings(data):
    with open("warnings.json", "w") as f:
        json.dump(data, f, indent=4)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ---------------- MODERATION ---------------- #

@bot.tree.command(name="ban", description="Ban a user")
@app_commands.describe(user="User to ban", reason="Reason")
async def ban(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("No permission!", ephemeral=True)
    await user.ban(reason=reason)
    await interaction.response.send_message(f"Banned {user} | Reason: {reason}")

@bot.tree.command(name="kick", description="Kick a user")
async def kick(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("No permission!", ephemeral=True)
    await user.kick()
    await interaction.response.send_message(f"Kicked {user}")

@bot.tree.command(name="mute", description="Mute a user")
async def mute(interaction: discord.Interaction, user: discord.Member, minutes: int):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("No permission!", ephemeral=True)
    duration = datetime.timedelta(minutes=minutes)
    await user.timeout(duration)
    await interaction.response.send_message(f"Muted {user} for {minutes} minutes")

@bot.tree.command(name="unmute", description="Unmute a user")
async def unmute(interaction: discord.Interaction, user: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("No permission!", ephemeral=True)
    await user.timeout(None)
    await interaction.response.send_message(f"Unmuted {user}")

@bot.tree.command(name="clear", description="Clear messages")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("No permission!", ephemeral=True)
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Deleted {amount} messages", ephemeral=True)

@bot.tree.command(name="warn", description="Warn a user")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("No permission!", ephemeral=True)

    data = load_warnings()
    uid = str(user.id)

    if uid not in data:
        data[uid] = []

    data[uid].append({
        "reason": reason,
        "moderator": str(interaction.user),
        "time": str(datetime.datetime.now())
    })

    save_warnings(data)
    await interaction.response.send_message(f"{user} has been warned.")

@bot.tree.command(name="warnings", description="View warnings")
async def warnings(interaction: discord.Interaction, user: discord.Member):
    data = load_warnings()
    uid = str(user.id)

    if uid not in data or len(data[uid]) == 0:
        return await interaction.response.send_message("No warnings found.")

    msg = ""
    for i, warn in enumerate(data[uid], 1):
        msg += f"{i}. {warn['reason']} (by {warn['moderator']})\n"

    await interaction.response.send_message(msg)

# ---------------- INFO ---------------- #

@bot.tree.command(name="userinfo", description="User info")
async def userinfo(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"{user}", color=discord.Color.blue())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Joined", value=user.joined_at)
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Server info")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=guild.name, color=discord.Color.green())
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Owner", value=guild.owner)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="User avatar")
async def avatar(interaction: discord.Interaction, user: discord.Member):
    embed = discord.Embed(title=f"{user}'s Avatar")
    embed.set_image(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Bot latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")

@bot.tree.command(name="botinfo", description="Bot info")
async def botinfo(interaction: discord.Interaction):
    embed = discord.Embed(title="Bot Info", color=discord.Color.purple())
    embed.add_field(name="Name", value=bot.user)
    embed.add_field(name="Servers", value=len(bot.guilds))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="roleinfo", description="Role info")
async def roleinfo(interaction: discord.Interaction, role: discord.Role):
    embed = discord.Embed(title=role.name, color=role.color)
    embed.add_field(name="Members", value=len(role.members))
    embed.add_field(name="Permissions", value=str(role.permissions))
    await interaction.response.send_message(embed=embed)

# ---------------- RUN ---------------- #

bot.run(os.getenv("TOKEN"))