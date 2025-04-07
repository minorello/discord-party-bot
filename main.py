import os
import discord
from discord.ext import commands
from discord import app_commands

# Pega o token diretamente das variáveis de ambiente (Render)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("❌ Erro: DISCORD_TOKEN não definido nas variáveis de ambiente.")
    exit(1)

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)
party_slots = {"EK": None, "ED": None, "MS": None, "RP": None}
voc_emojis = {"EK": "⚔️", "ED": "🧙‍♂️", "MS": "🧙", "RP": "🌽"}
GUILD_ID = 420982558080106499
GUILD = discord.Object(id=GUILD_ID)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=GUILD)
    print(f"✅ Bot conectado como {bot.user}")

@bot.tree.command(name="pt", description="Mostra a composição atual da party.", guild=GUILD)
async def show_party(interaction: discord.Interaction):
    status = ""
    for voc, member in party_slots.items():
        emoji = voc_emojis.get(voc, "")
        status += f"**{emoji} {voc}:** {member.mention if member else '🔄 Aguardando membro...'}\n"

    if all(party_slots.values()):
        view = JoinPTView()
        await interaction.response.send_message(content=status, view=view)
    else:
        await interaction.response.send_message(content=status)

@bot.tree.command(name="joinparty", description="Entre na party escolhendo sua vocação.", guild=GUILD)
@app_commands.describe(voc="Escolha entre EK, ED, MS ou RP")
@app_commands.choices(voc=[
    app_commands.Choice(name="EK", value="EK"),
    app_commands.Choice(name="ED", value="ED"),
    app_commands.Choice(name="MS", value="MS"),
    app_commands.Choice(name="RP", value="RP"),
])
async def joinparty(interaction: discord.Interaction, voc: app_commands.Choice[str]):
    user = interaction.user
    if party_slots[voc.value]:
        await interaction.response.send_message(f"A vaga de {voc.value} já está preenchida.", ephemeral=True)
        return

    for v, u in party_slots.items():
        if u == user:
            party_slots[v] = None

    party_slots[voc.value] = user
    await show_party(interaction)

def create_voc_command(voc_name):
    @bot.tree.command(name=voc_name.lower(), description=f"Entrar como {voc_name}.", guild=GUILD)
    async def voc_command(interaction: discord.Interaction):
        user = interaction.user
        if party_slots[voc_name]:
            await interaction.response.send_message(f"A vaga de {voc_name} já está preenchida.", ephemeral=True)
            return
        for v, u in party_slots.items():
            if u == user:
                party_slots[v] = None
        party_slots[voc_name] = user
        await show_party(interaction)

for voc in ["EK", "ED", "MS", "RP"]:
    create_voc_command(voc)

@bot.tree.command(name="swapvoc", description="Troque sua vocação na party.", guild=GUILD)
@app_commands.describe(voc="Nova vocação desejada (EK, ED, MS, RP)")
async def swapvoc(interaction: discord.Interaction, voc: str):
    voc = voc.upper()
    user = interaction.user
    if voc not in party_slots:
        await interaction.response.send_message("Vocação inválida. Use EK, ED, MS ou RP.", ephemeral=True)
        return
    if party_slots[voc]:
        await interaction.response.send_message(f"A vaga de {voc} já está preenchida.", ephemeral=True)
        return
    for v, u in party_slots.items():
        if u == user:
            party_slots[v] = None
    party_slots[voc] = user
    await show_party(interaction)

@bot.tree.command(name="delpt", description="Limpa a party e recomeça do zero.", guild=GUILD)
async def delpt(interaction: discord.Interaction):
    for voc in party_slots:
        party_slots[voc] = None
    await interaction.response.send_message("🧹 Party resetada com sucesso!", ephemeral=True)

class JoinPTView(discord.ui.View):
    @discord.ui.button(label="Join PT", style=discord.ButtonStyle.green)
    async def join_pt(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            member: discord.PermissionOverwrite(connect=True, speak=True)
            for member in party_slots.values() if member
        }
        overwrites[guild.default_role] = discord.PermissionOverwrite(connect=False)
        voice_channel = await guild.create_voice_channel("PT Temporária", overwrites=overwrites)
        await interaction.response.send_message(f"🔊 Canal de voz criado: {voice_channel.mention}")

# Inicia o bot
bot.run(DISCORD_TOKEN)
