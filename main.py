import asyncio
import random
from asyncio import Timeout
from dis import disco
from email.policy import default
from threading import Timer

import discord
from discord.ext import commands

from cPlayer import Player
from cEnemy import Enemy
from cBoss import Boss

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="/", intents=intents, activity=discord.Game(name="/help"))

global player

def player_create(playerID, playerName):
    global player
    player = Player(playerName, playerID)


def player_save():
    player.inventory.save()
    player.stats.save()
    player.cooldown.save()


@bot.event
async def on_ready():
    print(f"logged on as {bot.user}!")
    await bot.tree.sync()


@bot.tree.command(name="help", description="Here you can see how to play")
async def help(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    embed = discord.Embed(title=f"HELP", color=discord.Color.red())
    embed.add_field(name="</stats:1300464101247553637>", value="Used to show your stats and other important things", inline=False)
    embed.add_field(name="/inv", value="There you can see your Inventory", inline=False)
    embed.add_field(name="/heal", value="If you have some Heal-Potions you can heal yourself. If not, use the next Command", inline=False)
    embed.add_field(name="/shop", value="Here you can buy some important things", inline=False)
    embed.add_field(name="/hunt", value="With that, you can hunt after Enemys. But you need to check your health", inline=False)
    embed.add_field(name="/cd", value="Shows you your cooldowns", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="stats", description="Here you can see your stats")
async def stats(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    if player.cooldown.test_cd("info"):
        # Zeige Spieler-Daten in Discord
        embed = discord.Embed(title=f"{player.playerName}", color=discord.Color.blue())
        embed.add_field(name="🎖️: Level", value=player.stats.lvl, inline=False)
        embed.add_field(name="🔘: Exp", value=f"{player.stats.exp}/{player.stats.next_level()}", inline=False)
        embed.add_field(name="❤️: HP", value=f"{player.stats.hp}/{player.stats.hp_max}", inline=False)
        embed.add_field(name="<:Symbol_Mana:1306891900460204114>: MP", value=player.stats.mp, inline=False)
        embed.add_field(name="🗡️: Dmg", value=player.stats.dmg, inline=False)
        embed.add_field(name="🏞️: Stage", value=f"{player.stats.stage_current}/{player.stats.stage_max}", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        # Speichere Spieler-Daten
        player_save()
    else:
        embed = discord.Embed(title="Wait there is a CoolDown!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="inv", description="Shows the Inventory")
async def inv(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    embed = discord.Embed(title=f"{player.playerName}", color=discord.Color.blue())
    embed.add_field(name="🪙: Coin", value=player.inventory.coin, inline=False)
    embed.add_field(name="<:Potion_Healing:1306891850090545164>: Heal-Potion", value=player.inventory.potion_healing, inline=False)
    embed.add_field(name="🔑: Key-Dungeon", value=player.inventory.key_dungeon, inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)


@bot.tree.command(name="heal", description="Heals the Player")
async def heal(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    if player.inventory.potion_healing > 0:
        embed = discord.Embed(title=f"Healing", color=discord.Color.blue())
        player.stats.hp = player.stats.hp_max
        player.inventory.potion_healing -= 1
        embed.add_field(name="You are now at full health", value=player.stats.hp, inline=False)
        embed.add_field(name=f"There are {player.inventory.potion_healing} Potions left", value="", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        player_save()
    else:
        embed = discord.Embed(title=f"Healing", color=discord.Color.red())
        embed.add_field(name=f"There are no Potions left", value="Please buy new Potions", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="hunt", description="Hunts enemies on your stage")
async def hunt(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    if player.cooldown.test_cd("hunt"):
        enemy = Enemy(player.stats.stage_current)
        dmg = 0
        run_one = True
        if player.stats.dmg >= enemy.hp:
            embed = discord.Embed(title=f"{enemy.type}: {enemy.rarity}", color=enemy.enemy_color)
            embed.add_field(name="Congratulations you won!", value="", inline=False)
            embed.add_field(name="HP", value=f"{enemy.hp_max}")
            embed.add_field(name="Exp", value=f"{enemy.exp}")
            embed.add_field(name=f"You took {dmg} damage!", value="", inline=False)
        else:
            enemy.hp -= player.stats.dmg
            while player.stats.dmg < enemy.hp:
                # Erstelle Schaden und füge schaden allgemeinem schaden zu
                dmg_now = random.randint(enemy.dmg_min, enemy.dmg_max)
                dmg += dmg_now
                # Füge den schaden von spieler Gegner zu und andersrum
                enemy.hp -= player.stats.dmg
                player.stats.hp -= dmg_now
                # Prüfe ob spieler tot ist
                if player.stats.hp <= 0:
                    if run_one:
                        embed = discord.Embed(title="You died!", color=discord.Color.red())
                        player.inventory.coin -= round(player.inventory.coin / 2)
                        embed.add_field(name=f"You lost {player.inventory.coin} Coins", value="")
                        run_one = False
                    try:
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        player.stats.hp = player.stats.hp_max
                        print(f"{player.playerName} died and lost {player.inventory.coin} Coins")
                        player_save()
                    except:
                        pass
                else:
                    embed = discord.Embed(title=f"{enemy.type}: {enemy.rarity}", color=enemy.enemy_color)
                    embed.add_field(name="Congratulations you won!", value="", inline=False)
                    embed.add_field(name="HP", value=f"{enemy.hp_max}")
                    embed.add_field(name="Exp", value=f"{enemy.exp}")
                    embed.add_field(name=f"You took {dmg} damage!", value="", inline=False)

        if player.stats.hp > 0:
            if enemy.rarity == "Legendary" or enemy.rarity == "Mythic":
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                except:
                    pass
            else:
                try:
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                except:
                    pass
            player.stats.exp += enemy.exp

        # Speichere Spieler-Daten
        player_save()
    else:
        embed = discord.Embed(title="Wait there is a CoolDown!", color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="shop", description="This is a shop")
async def shop(interaction: discord.Interaction):
    # Spieler erstellen
    player_create(interaction.user.id, interaction.user.name)

    # Einbettung für den Shop
    embed = discord.Embed(title="Shop", color=discord.Color.blue())
    embed.add_field(name="<:Potion_Healing:1306891850090545164>: Potion-Healing", value=f"10 Coins", inline=False)
    embed.add_field(name="🔑: Dungeon-Key", value=f"10000 Coins", inline=False)

    # Nachricht senden (nicht ephemeral)
    await interaction.response.send_message(embed=embed)

    # Hole die gesendete Nachricht
    sent_message = await interaction.original_response()

    # Füge eine Reaktion hinzu
    await sent_message.add_reaction("<:Potion_Healing:1306891850090545164>")
    await sent_message.add_reaction("🔑")

    # Funktion zum Überprüfen der Reaktion
    def check(reaction, user):
        return user != bot.user and reaction.message.id == sent_message.id and str(reaction.emoji) in ['<:Potion_Healing:1306891850090545164>', '🔑']
    while True:
        try:
            # Warte auf eine Reaktion
            reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
            if str(reaction.emoji == "<:Potion_Healing:1306891850090545164>"):
                # Überprüfe, ob der Spieler genügend Münzen hat
                if player.inventory.coin >= 10:
                    player.inventory.coin -= 10
                    player.inventory.potion_healing += 1
                    confirmation_msg = await interaction.followup.send(f"You bought a healing potion", ephemeral=True)
                else:
                    confirmation_msg = await interaction.followup.send("Not enough Coins", ephemeral=True)
            elif str(reaction.emoji == "🔑"):
                # Überprüfe, ob der Spieler genügend Münzen hat
                if player.inventory.coin >= 10000:
                    player.inventory.coin -= 10000
                    player.inventory.key_dungeon += 1
                    confirmation_msg = await interaction.followup.send(f"You bought a Dungeon-Key", ephemeral=True)
                else:
                    confirmation_msg = await interaction.followup.send("Not enough Coins", ephemeral=True)
            player_save()
            # Entferne die Reaktion des Benutzers
            await sent_message.remove_reaction(reaction.emoji, user)
            await asyncio.sleep(0.5)
            await confirmation_msg.delete()

        except TimeoutError:
            # Entferne alle Reaktionen, wenn der Timeout erreicht ist
            await sent_message.clear_reactions()
            break


@bot.tree.command(name="daily", description="Get your free daily reward")
async def daily(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    if player.cooldown.test_cd("daily"):
        player_create(interaction.user.id, interaction.user.name)

        rand_coin = random.randint(1000, 2000)

        embed = discord.Embed(title="Daily Reward", color=discord.Color.blue())
        embed.add_field(name=f"You have collected your daily reward", value=f"🪙 +{rand_coin}\n🔘 +100", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=False)

        player.inventory.coin += rand_coin
        player.stats.exp += 100
    else:
        embed = discord.Embed(title="Daily Reward", color=discord.Color.red())
        embed.add_field(name="You have already collected your daily reward", value="", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    player_save()

@bot.tree.command(name="cd", description="Shows you your cooldowns")
async def cd(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    embed = discord.Embed(title="Cooldowns", color=discord.Color.blue())
    embed.add_field(name="Hunt", value=player.cooldown.get_time_cd("hunt"), inline=False)
    embed.add_field(name="Daily", value=player.cooldown.get_time_cd("daily"), inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=False)


bot.run("")
