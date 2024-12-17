# Erstelle IMPORTS
import asyncio
import json
import random
from asyncio import Timeout, timeout
from dis import disco
from email.policy import default
from threading import Timer

import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View

from cPlayer import Player
from cEnemy import Enemy
from cBoss import Boss

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="/", intents=intents, activity=discord.Game(name="/help"))

global player


# Erstelle Spieler
def player_create(playerID, playerName):
    global player
    player = Player(playerName, playerID)


# Speichere Spieler
def player_save():
    player.inventory.save()
    player.stats.save()
    player.cooldown.save()


@bot.event
# Synchronisiere die Bot-Befehle
async def on_ready():
    print(f"logged on as {bot.user}!")
    await bot.tree.sync()


@bot.tree.command(name="help", description="Here you can see how to play")
async def help(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    embed = discord.Embed(title=f"HELP", color=discord.Color.red())
    embed.add_field(name="</stats:1300464101247553637>", value="Used to show your stats and other important things", inline=False)
    embed.add_field(name="</inv:1306596976997171202>", value="There you can see your Inventory", inline=False)
    embed.add_field(name="</heal:1306542394765742091>", value="If you have some Heal-Potions you can heal yourself. If not, use the next Command", inline=False)
    embed.add_field(name="</shop:1306556610243727392>", value="Here you can buy some important things", inline=False)
    embed.add_field(name="</hunt:1300456261955092652>", value="With that, you can hunt after Enemys. But you need to check your health", inline=False)
    embed.add_field(name="</daily:1306602770811457589>", value="Claim your daily rewards", inline=False)
    embed.add_field(name="</cd:1310559296500662332>", value="Shows you your cooldowns", inline=False)
    embed.add_field(name="</casino:1310590380902711328>", value="Give a f*ck and try it", inline=False)
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
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(name="casino", description="A simple CASINO")
async def casino(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)

    # Einbettung für das Casino
    embed = discord.Embed(title="Casino", color=discord.Color.dark_red())
    embed.add_field(name="🎲: Roll the Dice", value="</cas_dice:1310866999550939167>\nPic a number from 1 to 6 and hope you are lucky", inline=False)
    embed.add_field(name="🎰: Gamble", value="</cas_gamble:1310866999550939168>\nRoll the slot machine and try your best", inline=False)
    embed.add_field(name="〽️ : Upper or Lower", value="</cas_upper_or_lower:1310937738153033741>\nThe mashine will pick a random number between 1 and 50 and you need to guess if the number is higher or lower as your number. The starting cost are 150 Coins and for every right guess you get 50 Coins.\nBut be warned you need to klick out if you want to stopp. If you guess something wrong, you will loose all your won money.")

    # Nachricht senden
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cas_dice", description="Let the Dice roll")
async def cas_dice(interaction: discord.Interaction, coins: int, number: int):
    player_create(interaction.user.id, interaction.user.name)

    embed = discord.Embed(title="Roll the Dice", color=discord.Color.dark_red())
    if 0 < number < 7:
        if 0 < coins <= player.inventory.coin:
            player.inventory.coin -= coins
            embed.add_field(name="Your pick:", value=number)
            rand = random.randint(1, 6)
            embed.add_field(name="Dice number", value=rand)
            if number == rand:
                player.inventory.coin += coins * 4
                embed.add_field(name="You won!", value=f"You earned {coins * 4} Coins", inline=False)
            else:
                embed.add_field(name="You lost!", value="Try again!", inline=False)
            player_save()
        elif coins > 0:
            embed.add_field(name="You dont have enough coins", value=f"Your Coins: {player.inventory.coin}", inline=False)
        else:
            embed.add_field(name="You typed a wrong value", value="You need to pick a normal Number that is higher than 0", inline=False)
    else:
        embed.add_field(name="Wrong number...", value="You need to pick a number between 1 and 6.")

    await interaction.response.send_message(embed=embed, ephemeral=True)
    player_save()


@bot.tree.command(name="cas_gamble", description="Let the sh*t happen")
async def cas_gamble(interaction: discord.Interaction, coins: int):
    player_create(interaction.user.id, interaction.user.name)
    with open("data\\dataLibrary\\directory.json", "r") as file:
        data = json.load(file)
        with open(data["dataLibrary"]["globals"], "r") as file:
            data = json.load(file)
            jackpot = data["casino"]["jackpot_gamble"]

        embed = discord.Embed(title="Gamble", color=discord.Color.dark_red())
        if coins <= player.inventory.coin:
            if coins >= 10:
                gamble_rand = random.randint(1, 1000)
                if gamble_rand == 1:
                    print(f"{player.playerName} got the jackpot: {jackpot}")
                    player.inventory.coin += jackpot
                    embed.add_field(name=f"Jackpot!!! {player.playerName} earned:", value=f"{jackpot} Coins", inline=False)
                    jackpot = 0
                    await interaction.response.send_message(embed=embed, ephemeral=False)
                elif gamble_rand <= 300:
                    player.inventory.coin += coins
                    embed.add_field(name="You have won! You earned:", value=f"{coins * 2} Coins", inline=False)
                    embed.add_field(name="The jackpot is:", value=jackpot)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    player.inventory.coin -= coins
                    jackpot += round(coins / 2)
                    embed.add_field(name="You lost!", value="Try again!", inline=False)
                    embed.add_field(name="The jackpot is:", value=jackpot)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed.add_field(name="You need to gamble at least with 10 Coins", value="Pleas set a higher number of Coins.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed.add_field(name="You dont have enough coins", value=f"Your Coins: {player.inventory.coin}", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)

    player_save()

    data["casino"] = {
        "jackpot_gamble": jackpot
    }
    with open(f"data\\dataLibrary\\globals.json", "w") as file:
        json.dump(data, file, indent=4)


@bot.tree.command(name="cas_upper_or_lower", description="Try your best!")
async def cas_upper_or_lower(interaction: discord.Interaction):
    player_create(interaction.user.id, interaction.user.name)
    if player.inventory.coin >= 150:
        player.inventory.coin -= 150
        global random_number, lost, won_coins
        won_coins = 0
        lost = False
        random_number = random.randint(1, 15)
        embed = discord.Embed(
            title="Upper or Lower",
            description=f"Die aktuelle nummer ist **{random_number}**",
            color=discord.Color.dark_red()
        )
        # Callback-Funktion für die Buttons
        async def button_upper_callback(interaction: discord.Interaction):
            global random_number, won_coins, lost
            new_rand = random.randint(1, 50)
            if new_rand >= random_number and lost == False:
                embed.description = f"**Richtig**, die neue Nummer ist **{new_rand}**"
                won_coins += 50
                random_number = new_rand
            elif lost == False:
                embed.description = f"**Falsch**, die neue Nummer wäre **{new_rand}** gewesen"
                lost = True
            else:
                embed.description = "Du hast schon **verloren**!!!"

            await interaction.response.edit_message(embed=embed)

        async def button_lower_callback(interaction: discord.Interaction):
            new_rand = random.randint(1, 50)
            global random_number, won_coins, lost
            if new_rand <= random_number and lost == False:
                embed.description = f"**Richtig**, die neue Nummer ist **{new_rand}**"
                won_coins += 50
                random_number = new_rand
            elif lost == False:
                embed.description = f"**Falsch**, die neue Nummer wäre **{new_rand}** gewesen"
                lost = True
            else:
                embed.description = "Du hast schon **verloren**!!!"

            await interaction.response.edit_message(embed=embed)

        async def button_out_callback(interaction: discord.Interaction):
            if lost == False:
                embed.description = f"Geld ist **Ausgezahlt**.\nDu hast {won_coins} Coins gewonnen"
                player.inventory.coin += won_coins
            else:
                embed.description = "Du hast schon **verloren**  starte das Spiel neu!!!"
            await interaction.response.edit_message(embed=embed)

        # Buttons erstellen
        button_upper = Button(label="⬆️", style=discord.ButtonStyle.primary)
        button_lower = Button(label="⬇️", style=discord.ButtonStyle.primary)
        button_out = Button(label="Out", style=discord.ButtonStyle.success)

        # Callback-Funktionen den Buttons zuweisen
        button_upper.callback = button_upper_callback
        button_lower.callback = button_lower_callback
        button_out.callback = button_out_callback

        # View erstellen und Buttons hinzufügen
        view = View()
        view.add_item(button_upper)
        view.add_item(button_lower)
        view.add_item(button_out)
        # Nachricht mit Embed und Buttons senden
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    else:
        embed = discord.Embed(title="Upper or Lower", description="You don't have enough Coins", color=discord.Color.dark_red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
    player_save()


bot.run("")
