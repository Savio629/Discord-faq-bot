import discord
from discord.ext import commands
from discord.ui import Button, View
import json
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token and channel ID from the environment variables
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

    # Generate the menu options directly in the channel
    channel = bot.get_channel(CHANNELID)
    if channel:
        menu_key = "menu"
        options = options_data.get(menu_key, [])
        if options:
            questions_text = "\n".join([f"{idx + 1}. {opt}" for idx, opt in enumerate(options)])
            embed = discord.Embed(title=f"Please choose an option from {menu_key}:", description=questions_text, color=discord.Color.blue())
            view = View()
            for idx in range(len(options)):
                view.add_item(OptionButton(label=str(idx + 1), custom_id=options[idx]))
            await channel.send(embed=embed, view=view)

async def show_menu(interaction, menu_key):
    # Fetch options from the options data
    options = options_data.get(menu_key, [])

    if not options:
        embed = discord.Embed(title="Error", description="No options available.", color=discord.Color.red())
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    questions_text = "\n".join([f"{idx + 1}. {opt}" for idx, opt in enumerate(options)])
    embed = discord.Embed(title=f"Please choose an option from {menu_key}:", description=questions_text, color=discord.Color.blue())

    view = View()
    for idx in range(len(options)):
        view.add_item(OptionButton(label=str(idx + 1), custom_id=options[idx]))

    if menu_key != "menu":  # Add "Back to Main Menu" button if not on the main menu
        view.add_item(BackToMenuButton())

    await interaction.followup.send(embed=embed, view=view, ephemeral=True)

class OptionButton(Button):
    def __init__(self, label, custom_id):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=custom_id)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        option_key = self.custom_id
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

class BackToMenuButton(Button):
    def __init__(self):
        super().__init__(label="Back to Main Menu", style=discord.ButtonStyle.danger)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await show_menu(interaction, "menu")

# Run the bot with your token
bot.run(DISCORD_TOKEN)
