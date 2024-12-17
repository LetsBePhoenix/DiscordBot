from cDirectory import Directory
from cEnemy import Enemy
from cPlayer import Player
from cBoss import Boss

directory = Directory()
print(f"test {directory.globals}")

player = Player("letsphoenix", 237)
print(player.playerID)
print(player.stats.hp)
print(player.cooldown.test_cd("hunt"))

enemy = Enemy(2)
print(f"{enemy.type} : {enemy.rarity}")

boss = Boss(1)
print(boss.name)






import discord
from discord.ext import commands

# Ersetze 'DEIN_BOT_TOKEN' mit deinem echten Bot-Token
TOKEN = 'DEIN_BOT_TOKEN'

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)


# Event, wenn der Bot bereit ist
@bot.event
async def on_ready():
    print(f'Bot ist bereit! Eingeloggt als {bot.user}')


# Befehl zum Senden einer Bestätigungsnachricht
@bot.command()
async def bestätigen(ctx):
    message = await ctx.send("Bitte bestätige, indem du auf die ✅ Reaktion klickst.")
    await message.add_reaction("✅")

    def check(reaction, user):
        return user != bot.user and str(reaction.emoji) == '✅' and reaction.message.id == message.id

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
        await ctx.send(f'{user.mention} hat die Bestätigung durchgeführt! 🎉')
    except TimeoutError:
        await ctx.send("Bestätigungszeit abgelaufen. ⌛")


# Starte den Bot
bot.run("")







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
