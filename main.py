import os
import base64
import hashlib
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv

# Detecta se está rodando no Render
if os.environ.get("RENDER"):
    base_dir = os.getcwd()  # No Render, use o diretório atual
else:
    base_dir = r"C:\Users\minor\OneDrive\Documents\workspace\key bot disc"

# Função para gerar a chave a partir da senha
def gerar_chave_da_senha(senha: str) -> bytes:
    return base64.urlsafe_b64encode(hashlib.sha256(senha.encode()).digest())

# Função para descriptografar um arquivo
def descriptografar_arquivo(caminho_enc: str, caminho_saida: str, senha: str):
    chave = gerar_chave_da_senha(senha)
    fernet = Fernet(chave)

    with open(caminho_enc, 'rb') as file_enc:
        dados_criptografados = file_enc.read()

    try:
        dados = fernet.decrypt(dados_criptografados)
        with open(caminho_saida, 'wb') as file_out:
            file_out.write(dados)
        print(f"✅ Descriptografado com sucesso: {caminho_saida}")
    except InvalidToken:
        print("❌ Erro: Senha inválida ou arquivo corrompido.")
        exit(1)

# Descriptografar .env antes de carregar variáveis
senha = os.getenv("SENHA_ENV")
if not senha:
    print("❌ Erro: SENHA_ENV não definida nas variáveis de ambiente.")
    exit(1)

env_criptografado = os.path.join(base_dir, ".env.enc")
env_temporario = os.path.join(base_dir, ".env")
descriptografar_arquivo(env_criptografado, env_temporario, senha)

# Carregar variáveis do .env
load_dotenv(dotenv_path=env_temporario)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Importações do Discord após carregar o token
import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)
party_slots = {"EK": None, "ED": None, "MS": None, "RP": None}

voc_emojis = {
    "EK": "⚔️", "ED": "🧙‍♂️", "MS": "🧙", "RP": "🌽"
}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")

@bot.tree.command(name="pt", description="Mostra a composição atual da party.")
async def pt(interaction: discord.Interaction):
    status = ""
    for voc, member in party_slots.items():
        emoji = voc_emojis.get(voc, "")
        status += f"**{emoji} {voc}:** {member.mention if member else '🔄 Aguardando membro...'}\n"

    if all(party_slots.values()):
        view = JoinPTView()
        await interaction.response.send_message(content=status, view=view)
    else:
        await interaction.response.send_message(content=status)

@bot.tree.command(name="joinparty", description="Entre na party escolhendo sua vocação.")
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
    await interaction.response.send_message(f"Você entrou como {voc.value}.")

def create_voc_command(voc_name):
    @bot.tree.command(name=voc_name.lower(), description=f"Entrar como {voc_name}.")
    async def voc_command(interaction: discord.Interaction):
        user = interaction.user
        if party_slots[voc_name]:
            await interaction.response.send_message(f"A vaga de {voc_name} já está preenchida.", ephemeral=True)
            return
        for v, u in party_slots.items():
            if u == user:
                party_slots[v] = None
        party_slots[voc_name] = user
        await interaction.response.send_message(f"Você entrou como {voc_name}.")

for voc in ["EK", "ED", "MS", "RP"]:
    create_voc_command(voc)

@bot.tree.command(name="swapvoc", description="Troque sua vocação na party.")
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
    await interaction.response.send_message(f"Você mudou para {voc}.")

class JoinPTView(discord.ui.View):
    @discord.ui.button(label="Join PT", style=discord.ButtonStyle.green)
    async def join_pt(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            member: discord.PermissionOverwrite(connect=True, speak=True)
            for member in party_slots.values()
        }
        overwrites[guild.default_role] = discord.PermissionOverwrite(connect=False)
        voice_channel = await guild.create_voice_channel("PT Temporária", overwrites=overwrites)
        await interaction.response.send_message(f"Canal de voz criado: {voice_channel.mention}")

# Inicia o bot
bot.run(DISCORD_TOKEN)

# (Opcional) Apaga o .env temporário após uso (só se não for usar mais)
# os.remove(env_temporario)
