import os
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
import threading
import datetime
import time

# =============================
# Flask (Render keep-alive)
# =============================
app = Flask("")

@app.route("/")
def home():
    return "✅ RP Kezelő bot fut!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# =============================
# Discord bot beállítások
# =============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_ROLES = ["RP Staff"]  # <<< ezt a rangot cseréld
RP_CHANNEL_ID = 123456789012345678  # <<< RP csatorna ID

def has_permission(interaction: discord.Interaction) -> bool:
    return any(role.name in ALLOWED_ROLES for role in interaction.user.roles)

# =============================
# Events
# =============================
@bot.event
async def on_ready():
    print(f"✅ Bejelentkezve mint {bot.user}")
    await bot.tree.sync()

# =============================
# Parancsok
# =============================

@bot.tree.command(name="help", description="Parancsok listája")
async def help_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod ehhez!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📜 RP Kezelő parancsok",
        color=discord.Color.blue()
    )
    embed.add_field(name="/rp <idő>", value="RP felhívás küldése", inline=False)
    embed.add_field(name="/rpstart", value="RP indítás szöveg", inline=False)
    embed.add_field(name="/rpend", value="RP lezárás szöveg", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# -----------------------------
# /rp
# -----------------------------
@bot.tree.command(name="rp", description="RP felhívás küldése")
@app_commands.describe(time="Mikor lesz az RP? (pl. 18:00)")
async def rp_slash(interaction: discord.Interaction, time: str):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod ehhez!", ephemeral=True)
        return

    channel = bot.get_channel(RP_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ RP csatorna nem található!", ephemeral=True)
        return

    message = f"""**RP Felhívás**

A mai napon **{time}**-kor RP lesz!

🟢 **Pipa** – Ha jössz  
🟡 **Sárga** – Ha késel  
🔴 **Piros** – Ha nem érsz rá
"""

    await channel.send(message)
    await interaction.response.send_message("✅ RP felhívás elküldve!", ephemeral=True)

# -----------------------------
# /rpstart
# -----------------------------
@bot.tree.command(name="rpstart", description="RP indítása")
async def rpstart_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod ehhez!", ephemeral=True)
        return

    channel = bot.get_channel(RP_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ RP csatorna nem található!", ephemeral=True)
        return

    await channel.send("🚓 **RP START** – mindenkinek jó játékot!\n**LCRP Staff Team**")
    await interaction.response.send_message("✅ RP START elküldve!", ephemeral=True)

# -----------------------------
# /rpend
# -----------------------------
@bot.tree.command(name="rpend", description="RP lezárása")
async def rpend_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod ehhez!", ephemeral=True)
        return

    channel = bot.get_channel(RP_CHANNEL_ID)
    if not channel:
        await interaction.response.send_message("❌ RP csatorna nem található!", ephemeral=True)
        return

    await channel.send(
        "🏁 **RP END** – köszönjük mindenkinek a részvételt,\n"
        "reméljük mindenki jól érezte magát!\n"
        "**LCRP Staff Team**"
    )
    await interaction.response.send_message("✅ RP END elküldve!", ephemeral=True)

# =============================
# Indítás (Render-barát)
# =============================
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    token = os.getenv("DISCORD_BOT_TOKEN")

    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN hiányzik!")

    while True:
        try:
            bot.run(token)
        except Exception as e:
            print(f"❌ Hiba: {e} – újraindítás 10 mp múlva")
            time.sleep(10)
