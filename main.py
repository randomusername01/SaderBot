import discord
from discord.ext import commands
from discord import app_commands
import requests
import toml

config = toml.load('config.toml')

TOKEN = config['discord']['bot_token']
API_KEY = config['api']['apikey']

intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)

async def sync_commands(guild_id):
    guild = discord.Object(id=guild_id)
    await client.tree.sync(guild=guild)
    print(f"Commands synced to guild {guild_id}")

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    await sync_commands('223071993858228224')

@client.tree.command(name="ping", description="Testing")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")
    
@client.command(name="ping", help="Testing")
async def ping(ctx):
    await ctx.send("Pong!")

client.run(TOKEN)
