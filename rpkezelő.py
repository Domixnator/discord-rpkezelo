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
# Discord bot
# =============================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

ALLOWED_ROLES = [RPStaff]          # <<< jogosult rang
RP_CHANNEL_ID = 1302415423186407509    # <<< RP csatorna
LOG_CHANNEL_ID = 1302415427070201984   # <<< LOG csatorna

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
# /help
# =============================
@bot.tree.command(name="help", description="RP Kezelő parancsok")
async def help_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod!", ephemeral=True)
        return

    embed = discord.Embed(
        title="📜 RP Kezelő parancsok",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="/rp <idő>", value="RP felhívás (embed)", inline=False)
    embed.add_field(name="/rpstart", value="RP indítása", inline=False)
    embed.add_field(name="/rpend", value="RP lezárása", inline=False)
    embed.add_field(name="/test", value="Bot tesztelése", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================
# /test
# =============================
@bot.tree.command(name="test", description="Bot működésének tesztelése")
async def test_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod!", ephemeral=True)
        return

    await interaction.response.send_message("✅ A bot működik!", ephemeral=True)

# =============================
# /rp (EMBED)
# =============================
@bot.tree.command(name="rp", description="RP felhívás küldése")
@app_commands.describe(time="Mikor lesz az RP? (pl. 18:00)")
async def rp_slash(interaction: discord.Interaction, time: str):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod!", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    if not rp_channel:
        await interaction.response.send_message("❌ RP csatorna nem található!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🚨 RP Felhívás",
        description=(
            f"A mai napon **{time}**-kor RP lesz!\n\n"
            "🟢 **Pipa** – Ha jössz\n"
            "🟡 **Sárga** – Ha késel\n"
            "🔴 **Piros** – Ha nem érsz rá"
        ),
        color=discord.Color.dark_red(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="LCRP Staff Team")

    await rp_channel.send(embed=embed)
    await interaction.response.send_message("✅ RP felhívás elküldve!", ephemeral=True)

    if log_channel:
        log_embed = discord.Embed(
            title="📌 RP FELHÍVÁS LOG",
            color=discord.Color.dark_red()
        )
        log_embed.add_field(name="Idő", value=time, inline=True)
        log_embed.add_field(name="Ki adta ki", value=interaction.user.mention, inline=True)
        log_embed.add_field(name="Csatorna", value=rp_channel.mention, inline=False)
        log_embed.set_footer(text=f"User ID: {interaction.user.id}")
        log_channel.send(embed=log_embed)

# =============================
# /rpstart
# =============================
@bot.tree.command(name="rpstart", description="RP indítása")
async def rpstart_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod!", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    await rp_channel.send("🚓 **RP START** – mindenkinek jó játékot!\n**LCRP Staff Team**")
    await interaction.response.send_message("✅ RP START elküldve!", ephemeral=True)

    if log_channel:
        log_channel.send(
            f"▶️ **RP START** | Ki: {interaction.user.mention} | Csatorna: {rp_channel.mention}"
        )

# =============================
# /rpend
# =============================
@bot.tree.command(name="rpend", description="RP lezárása")
async def rpend_slash(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod!", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    await rp_channel.send(
        "🏁 **RP END** – köszönjük mindenkinek a részvételt,\n"
        "reméljük mindenki jól érezte magát!\n"
        "**LCRP Staff Team**"
    )
    await interaction.response.send_message("✅ RP END elküldve!", ephemeral=True)

    if log_channel:
        log_channel.send(
            f"⏹️ **RP END** | Ki: {interaction.user.mention} | Csatorna: {rp_channel.mention}"
        )

# =============================
# Indítás (Render)
# =============================
if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    token = os.getenv("MTQ2Nzg4NDAxNDY2ODA4NzUxMQ.Ge4NRI.BlBe0Yz-B3DPg4xYdwjzLIHcvmJKgKYkvRYFMA")

    if not token:
        raise RuntimeError("❌ DISCORD_BOT_TOKEN hiányzik!")

    while True:
        try:
            bot.run(token)
        except Exception as e:
            print(f"❌ Hiba: {e} – újraindítás 10 mp múlva")
            time.sleep(10)

