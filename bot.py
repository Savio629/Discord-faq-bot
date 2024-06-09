import discord
from discord.ext import commands
from discord.ui import Button, View
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from the environment variable
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNELID = int(os.getenv('CHANNELID'))
# Define your API endpoint
API_URL = 'http://127.0.0.1:5000/chatbot'

# Initialize the bot with the required intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

# Initialize bot with command prefix
bot = commands.Bot(command_prefix='/', intents=intents)

# Read options data from JSON file
with open('menu_structure.json', 'r', encoding='utf-8') as file:
    options_data = json.load(file)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if not message.content.startswith('/'):
        await message.channel.send("Please type commands only.", delete_after=10)
        await message.delete()
        return

    await bot.process_commands(message)

@bot.tree.command(name="menu")
async def menu(interaction: discord.Interaction):
    await interaction.response.send_message("Please select an option from the menu:", ephemeral=True)
    await show_menu(interaction, "menu")

async def show_menu(interaction, menu_key):
    # Fetch options from the options data
    options = options_data.get(menu_key, [])

    if not options:
        await interaction.followup.send("No options available.", ephemeral=True)
        return

    view = View()
    for option in options:
        view.add_item(OptionButton(label=option))

    await interaction.followup.send(f"Please choose an option from {menu_key}:", view=view, ephemeral=True)

class OptionButton(Button):
    def __init__(self, label):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        option_key = self.label
        # Fetch data for the selected option from JSON file
        data = options_data.get(option_key)
        if data:
            if isinstance(data, list):
                # If data is a list, send options menu for the selected option
                await show_menu(interaction, option_key)
            else:
                # If data is not a list, send it as plain text
                await interaction.followup.send(data, ephemeral=True)
        else:
            await interaction.followup.send("Data not available for this option.", ephemeral=True)

# Run the bot with your token
bot.run(DISCORD_TOKEN)
