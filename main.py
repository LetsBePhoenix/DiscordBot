import datetime
import json
import os
import random
import time

import discord
from discord.ext import commands

from cPlayer import Player
from cEnemy import Enemy
from cTime import Time

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
    embed.add_field(name="/daily", value="You can claim your daly reward", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="info", description="Here you can see YOUR stats")
async def info(interaction: discord.Interaction):
    cdTime = Time(interaction.user.id)
    if cdTime.testcd("info"):
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
    else:
        embed = discord.Embed(title="Wait there is a CoolDown!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="hunt", description="Hunts enemies on your stage")
async def hunt(interaction: discord.Interaction):
    cdTime = Time(interaction.user.id)
    if cdTime.testcd("hunt"):
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
        if enemy.rarity == "Legendary" or enemy.rarity == "Mythic":
            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

        player.exp += enemy_exp

        # Speichere Spieler-Daten
        player_save()
    else:
        embed = discord.Embed(title="Wait there is a CoolDown!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


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


@bot.tree.command(name="cd", description="Cooldown")
async def cd(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    cdTime = Time(interaction.user.id)

    embed = discord.Embed(title="Your cool downs:", color=discord.Color.blue())
    embed.add_field(name="Hunt", value=cdTime.gettimecd("hunt"), inline=False)
    embed.add_field(name="Info", value=cdTime.gettimecd("info"), inline=False)
    embed.add_field(name="Search", value=cdTime.gettimecd("search"), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="daily", description="Get your free daily reward")
async def daily(interaction: discord.Interaction):
    cdTime = Time(interaction.user.id)
    if cdTime.testcd("daily"):
        player_create(interaction.user.id, interaction.user.name)
        embed = discord.Embed(title="Daily Reward", color=discord.Color.blue())
        embed.add_field(name="You have collected your daily reward", value="+1000exp", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        player.exp += 1000
    else:
        embed = discord.Embed(title="Daily Reward", color=discord.Color.red())
        embed.add_field(name="You have already collected your daily reward", value="", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    player_save()


@bot.tree.command(name="gamble", description="You can gamble")
async def gamble(interaction: discord.Interaction, ammount: int):
    player_create(interaction.user.id, interaction.user.name)
    # Lade jackpot aus globals
    with open(f"data\\dataLibrary\\globals.json", "r") as file:
        data = json.load(file)
        if "casino" in data:
            jackpot = data["casino"]["jackpot"]
    # Lade coins aus player
    with open(f"data\\dataPlayer\\{player.playerID}.json") as file:
        data_coin = json.load(file)
        if "inv" in data_coin:
            player_coins = data_coin["inv"]["coin"]
        else:
            player_coins = 0

    if ammount <= player_coins:
        if ammount > 0:
            gamble_rand = random.randint(1, 1000)
            embed = discord.Embed(title="Gamble", color=discord.Color.dark_magenta())
            if gamble_rand == 1:
                player_coins += jackpot
                jackpot = 0
                embed.add_field(name=f"Jackpot!!! {player.playerName} earned:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=False)
            elif gamble_rand <= 300:
                player_coins += (ammount * 2)
                embed.add_field(name="You have won! You earned:", value=f"{ammount * 2}", inline=False)
                embed.add_field(name="The jackpot is:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                player_coins -= ammount
                jackpot += round(ammount / 2)
                embed.add_field(name="You lost!", value="Try again!", inline=False)
                embed.add_field(name="The jackpot is:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Gamble", color=discord.Color.dark_magenta())
        embed.add_field(name="Not enough coins", value="You don't have enough coins to gamble with that amount", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Write data back to globals
    data["casino"] = {
        "jackpot": jackpot
    }
    with open(f"data\\dataLibrary\\globals.json", "w") as file:
        json.dump(data, file, indent=4)

    # Write data back to inventory
    data_coin["inv"] = {
        "coin": player_coins
    }
    with open(f"data\\dataPlayer\\{player.playerID}.json", "w") as file:
        json.dump(data_coin, file, indent=4)


@bot.tree.command(name="casinohelp", description="There are the Casino-Functions")
async def casinohelp(interaction: discord.Interaction):
    embed = discord.Embed(title="Casino-HelpCenter", color=discord.Color.red())
    embed.add_field(name="/gamble", value="Here you can gamble with your coins", inline=False)
    embed.add_field(name="Info", value="Casinos have a high risk of addiction and are only for entertainment", inline=False)
    embed.add_field(name="Specs", value="0,1% Jackpot\n30% Winning\nRest Loosing", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run("MTI5NTMwMjU1MzYxMjg0NTExOQ.Go3XdD.nZj30NeRy1VzzFWIs7z0SiK-F0kQDSZ-BbGhNI")
