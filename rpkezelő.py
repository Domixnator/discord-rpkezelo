import os
import discord
from discord import app_commands
from discord.ext import commands
import datetime

# =============================
# BOT BEÁLLÍTÁSOK
# =============================
TOKEN = os.getenv("MTQ2Nzg4NDAxNDY2ODA4NzUxMQ.GA0V99.f2BW21RpshtPMJJY6d45axFCmeZHck84zhj8IA")

ALLOWED_ROLES = ["RP Staff"]          # rang neve
RP_CHANNEL_ID = 1302415423186407509    # RP csatorna ID
LOG_CHANNEL_ID = 1302415427070201984   # LOG csatorna ID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =============================
# JOGOSULTSÁG ELLENŐRZÉS
# =============================
def has_permission(interaction: discord.Interaction) -> bool:
    return any(role.name in ALLOWED_ROLES for role in interaction.user.roles)

# =============================
# GOMBOS VIEW (1 katt / user)
# =============================
class RPJoinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.users = set()

    async def check(self, interaction: discord.Interaction):
        if interaction.user.id in self.users:
            await interaction.response.send_message(
                "⚠️ Már jelentkeztél erre az RP-re!",
                ephemeral=True
            )
            return False
        self.users.add(interaction.user.id)
        return True

    @discord.ui.button(label="Jövök", style=discord.ButtonStyle.success, emoji="🟢")
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check(interaction):
            return
        await interaction.response.send_message("✅ Jelentkezés rögzítve!", ephemeral=True)

    @discord.ui.button(label="Kések", style=discord.ButtonStyle.primary, emoji="🟡")
    async def late(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check(interaction):
            return
        await interaction.response.send_message("🟡 Késést jeleztél!", ephemeral=True)

    @discord.ui.button(label="Nem jövök", style=discord.ButtonStyle.danger, emoji="🔴")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check(interaction):
            return
        await interaction.response.send_message("🔴 Nem jössz az RP-re.", ephemeral=True)

# =============================
# READY
# =============================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bejelentkezve: {bot.user}")

# =============================
# /test
# =============================
@bot.tree.command(name="test", description="Bot tesztelése")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("✅ A bot működik!", ephemeral=True)

# =============================
# /help
# =============================
@bot.tree.command(name="help", description="RP Kezelő parancsok")
async def help_cmd(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📜 RP Kezelő",
        color=discord.Color.dark_red()
    )
    embed.add_field(name="/rp <idő>", value="RP felhívás", inline=False)
    embed.add_field(name="/rpstart", value="RP indítása", inline=False)
    embed.add_field(name="/rpend", value="RP lezárása", inline=False)
    embed.add_field(name="/test", value="Teszt parancs", inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

# =============================
# /rp
# =============================
@bot.tree.command(name="rp", description="RP felhívás küldése")
@app_commands.describe(time="Mikor lesz az RP? (pl. 18:00)")
async def rp(interaction: discord.Interaction, time: str):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod.", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    log_channel = bot.get_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(
        title="🚨 RP FELHÍVÁS",
        description=(
            f"A mai napon **{time}**-kor RP lesz!\n\n"
            "🟢 Jövök\n🟡 Kések\n🔴 Nem jövök"
        ),
        color=discord.Color.dark_red(),
        timestamp=datetime.datetime.utcnow()
    )
    embed.set_footer(text="LCRP Staff Team")

    await rp_channel.send(embed=embed, view=RPJoinView())
    await interaction.response.send_message("✅ RP elküldve!", ephemeral=True)

    if log_channel:
        await log_channel.send(
            f"📌 RP kiírva | Idő: {time} | Ki: {interaction.user.mention}"
        )

# =============================
# /rpstart
# =============================
@bot.tree.command(name="rpstart", description="RP indítása")
async def rpstart(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod.", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    await rp_channel.send("🚓 **RP START** – jó játékot!\n**LCRP Staff Team**")
    await interaction.response.send_message("✅ RP START elküldve!", ephemeral=True)

# =============================
# /rpend
# =============================
@bot.tree.command(name="rpend", description="RP lezárása")
async def rpend(interaction: discord.Interaction):
    if not has_permission(interaction):
        await interaction.response.send_message("⛔ Nincs jogod.", ephemeral=True)
        return

    rp_channel = bot.get_channel(RP_CHANNEL_ID)
    await rp_channel.send(
        "🏁 **RP END** – köszönjük a részvételt!\n**LCRP Staff Team**"
    )
    await interaction.response.send_message("✅ RP END elküldve!", ephemeral=True)

# =============================
# INDÍTÁS
# =============================
if not TOKEN:
    raise RuntimeError("❌ DISCORD_BOT_TOKEN nincs beállítva!")

bot.run(TOKEN)
