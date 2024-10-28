import datetime
import json
import os
import random
import time
from email.policy import default

import discord
from discord.ext import commands

from cPlayer import Player
from cEnemy import Enemy
from cTime import Time

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents, activity=discord.Game(name="/help"))

players = {}
global player

def player_create(playerID, playerName):
    global player
    player = Player(playerID, playerName)


def player_save():
    player.try_levelup(player.lvl)
    player.save_player()


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
    embed.add_field(name="/casino_help", value="Here you can see the Casino-Functions", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="stats", description="Here you can see YOUR stats")
async def stats(interaction: discord.Interaction):
    cdTime = Time(interaction.user.id)
    if cdTime.testcd("info"):
        # Erstelle und lade Spieler-Daten
        player_create(interaction.user.id, interaction.user.name)

        # Zeige Spieler-Daten in Discord
        embed = discord.Embed(title=f"{interaction.user.name}", color=discord.Color.blue())
        embed.add_field(name="Level", value=player.lvl, inline=False)
        embed.add_field(name="Exp", value=f"{player.exp}/{player.next_level()}", inline=False)
        embed.add_field(name="HP", value=player.hp, inline=False)
        embed.add_field(name="MP", value=player.mp, inline=False)
        embed.add_field(name="Stage", value=f"{player.stage}/{player.stage_max}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        # Speichere Spieler-Daten
        player_save()
    else:
        embed = discord.Embed(title="Wait there is a CoolDown!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=False)


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
    player_create(interaction.user.id, interaction.user.name)
    cdTime = Time(interaction.user.id)
    if cdTime.testcd("daily"):
        player_create(interaction.user.id, interaction.user.name)

        rand_coin = random.randint(1000, 2000)

        embed = discord.Embed(title="Daily Reward", color=discord.Color.blue())
        embed.add_field(name=f"You have collected your daily reward", value=f"+{rand_coin} Coins\n+100 Exp", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        player.inventory.coin += rand_coin
        player.exp += 100
    else:
        embed = discord.Embed(title="Daily Reward", color=discord.Color.red())
        embed.add_field(name="You have already collected your daily reward", value="", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    player_save()
    player.inventory.save_inventory()


@bot.tree.command(name="casino_gamble", description="You can gamble")
async def casino_gamble(interaction: discord.Interaction, ammount: int):
    player_create(interaction.user.id, interaction.user.name)
    # Lade jackpot aus globals
    with open(f"data\\dataLibrary\\globals.json", "r") as file:
        data = json.load(file)
        if "casino" in data:
            jackpot = data["casino"]["jackpot"]

    if ammount <= player.inventory.coin:
        if ammount > 0:
            gamble_rand = random.randint(1, 1000)
            embed = discord.Embed(title="Gamble", color=discord.Color.dark_magenta())
            if gamble_rand == 1:
                print(f"{player.playerName} got the jackpot: {jackpot}")
                player.inventory.coin += jackpot
                jackpot = 0
                embed.add_field(name=f"Jackpot!!! {player.playerName} earned:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=False)
            elif gamble_rand <= 300:
                player.inventory.coin += (ammount)
                embed.add_field(name="You have won! You earned:", value=f"{ammount * 2}", inline=False)
                embed.add_field(name="The jackpot is:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                player.inventory.coin -= ammount
                jackpot += round(ammount / 2)
                embed.add_field(name="You lost!", value="Try again!", inline=False)
                embed.add_field(name="The jackpot is:", value=jackpot)
                await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Gamble", color=discord.Color.dark_magenta())
        embed.add_field(name="Not enough coins", value="You don't have enough coins to gamble with that amount", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    player.inventory.save_inventory()

    data["casino"] = {
        "jackpot": jackpot
    }
    with open(f"data\\dataLibrary\\globals.json", "w") as file:
        json.dump(data, file, indent=4)


@bot.tree.command(name="casino_dice", description="You can role the Dice")
async def casino_dice(interaction: discord.Interaction, ammount: int, number: int):
    player_create(interaction.user.id, interaction.user.name)
    if 0 < number < 7:
        if 0 < ammount <= player.inventory.coin:
            player.inventory.coin -= ammount
            rand = random.randint(1, 6)
            embed = discord.Embed(title="Dice", color=discord.Color.dark_magenta())
            embed.add_field(name=f"You picked {number}, the dice landed on {rand}.", value="", inline=False)
            if number == rand:
                player.inventory.coin += ammount * 4
                embed.add_field(name="You won!", value=f"You earned {ammount * 4} Coins", inline=False)
            else:
                embed.add_field(name="You lost!", value="Try again!", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    player.inventory.save_inventory()


@bot.tree.command(name="inv", description="Opens the Inventory")
async def inv(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    embed = discord.Embed(title="Inventory", colour=discord.Color.blue())
    player_create(interaction.user.id, interaction.user.name)
    embed.add_field(name="Coins", value=player.inventory.coin, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="casino_help", description="There are the Casino-Functions")
async def casino_help(interaction: discord.Interaction):
    embed = discord.Embed(title="Casino-HelpCenter", color=discord.Color.red())
    embed.add_field(name="Info", value="Casinos have a high risk of addiction and are only for entertainment", inline=False)
    embed.add_field(name="-----", value="", inline=False)
    embed.add_field(name="/casino_gamble", value="Here you can gamble with your coins", inline=False)
    embed.add_field(name="Function", value="The half of a lose will go to the price-pool of the Jackpot!")
    embed.add_field(name="Specs", value="0,1% Jackpot\n30% Winning", inline=False)
    embed.add_field(name="-----", value="", inline=False)
    embed.add_field(name="/casino_dice", value="Here you can role the dice and set your cons", inline=False)
    embed.add_field(name="Specs", value="17% Winrate")
    await interaction.response.send_message(embed=embed, ephemeral=True)


bot.run("")
