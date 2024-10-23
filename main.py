import os
import random
import discord
from discord.ext import commands

from cPlayer import Player
from cEnemy import Enemy

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents, activity=discord.Game(name="/help"))

players = {}


def player_create(playerID, playerName):
    global player
    player = Player(playerID, playerName)


def player_save():
    player.try_levelup(player.lvl)
    player.save_player()


# Dateipfade
directory_data_player = "data/dataPlayer"
directory_data_enemy = "data/dataEnemy"

# Prüfe, ob die dateipfade Existieren
os.makedirs(directory_data_player, exist_ok=True)


@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')
    await bot.tree.sync()


@bot.tree.command(name="help", description="All you can do")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="HelpCenter", color=discord.Color.red())
    embed.add_field(name="/info", value="Here you can see your stats", inline=False)
    embed.add_field(name="/hunt", value="Here you can fight against an enemy on your stage", inline=False)
    embed.add_field(name="/cs", value="With that, you can change your stage", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="info", description="Here you can see YOUR stats")
async def info(interaction: discord.Interaction):

    # Erstelle und lade Spieler-Daten
    player_create(interaction.user.id, interaction.user.name)

    # Zeige Spieler-Daten in Discord
    embed = discord.Embed(title=f"{interaction.user.name}", color=discord.Color.blue())
    embed.add_field(name="Level", value=player.lvl, inline=False)
    embed.add_field(name="Exp", value=player.exp, inline=False)
    embed.add_field(name="HP", value=player.hp, inline=False)
    embed.add_field(name="MP", value=player.mp, inline=False)
    embed.add_field(name="Stage", value=f"{player.stage}/{player.stage_max}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    # Speichere Spieler-Daten
    player_save()


@bot.tree.command(name="hunt", description="Hunts enemies on your stage")
async def hunt(interaction: discord.Interaction):

    # Erstelle und lade Spieler-Daten
    player_create(interaction.user.id, interaction.user.name)

    # Code
    enemy = Enemy(player.stage)
    enemy_exp = random.randint(enemy.exp_min, enemy.exp_max)
    enemy_dmg = random.randint(enemy.dmg_min, enemy.dmg_max)
    embed = discord.Embed(title=f"{enemy.name}: {enemy.rarity}", color=enemy.enemy_color)
    embed.add_field(name="HP", value=f"{enemy.hp}/{enemy.hp_max}", inline=False)
    embed.add_field(name="Exp", value=f"{enemy_exp}", inline=False)
    embed.add_field(name="Dmg", value=f"{enemy_dmg}", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    player.exp += enemy_exp

    # Speichere Spieler-Daten
    player_save()


@bot.tree.command(name="cs", description="Changes Stage +1")
async def cs(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)

    if player.stage + 1 > player.stage_max:
        player.stage = 1
    else:
        player.stage += 1

    embed = discord.Embed(title=f"Your stage is changed to {player.stage}", color=discord.Color.blue())
    embed.add_field(name=f"{player.stage}/{player.stage_max}", value="", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    player_save()


bot.run("DiscordToken")
