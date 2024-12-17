'''
Erstelle Klasse Gegner

Hier werden alle wichtigen bereiche der klasse Gegner abgearbeitet
'''
import json
import random

import discord

from cDirectory import Directory


class Enemy:
    def __init__(self, stage):
        self.directory = Directory()
        self.file_path = self.get_file_path(stage)
        self.stage = stage
        self.type = ""
        self.hp = 0
        self.hp_max = 0
        self.exp = 0
        self.dmg_min = 0
        self.dmg_max = 0
        self.rarity = ""
        self.enemy_color = discord.Color.dark_gray()

        self.get_rarity()
        self.get_enemy()

    def get_file_path(self, stage):
        if stage == 1:
            return self.directory.stage1
        elif stage == 2:
            return self.directory.stage2

    def get_enemy(self):
        with open(self.file_path, "r") as file:
            data = json.load(file)
            rand = random.randint(1, 100)
            if rand <= 30:
                e = 1
            elif rand <= 60:
                e = 2
            elif rand <= 85:
                e = 3
            elif rand <= 95:
                e = 4
            else:
                e = 5
            # set Values
            self.type = data[f"enemy{e}"]["name"]
            self.hp = data[f"enemy{e}"]["hp"]
            self.hp_max = self.hp
            self.exp = random.randint(data[f"enemy{e}"]["exp_min"], data[f"enemy{e}"]["exp_max"])
            self.dmg_min = data[f"enemy{e}"]["dmg_min"]
            self.dmg_max = data[f"enemy{e}"]["dmg_max"]

            # set values from rarity
            if self.rarity == "Uncommon":
                self.exp = round(self.exp * 1.1)
                self.enemy_color = discord.Color.light_grey()
            elif self.rarity == "Rare":
                self.exp = round(self.exp * 1.2)
                self.enemy_color = discord.Color.green()
            elif self.rarity == "Epic":
                self.exp = round(self.exp * 1.5)
                self.enemy_color = discord.Color.purple()
            elif self.rarity == "Legendary":
                self.exp = round(self.exp * 2)
                self.enemy_color = discord.Color.gold()
            elif self.rarity == "Mythic":
                self.exp = round(self.exp * 5)
                self.enemy_color = discord.Color.pink()



    def get_rarity(self):
        random_rarity = random.randint(1, 1000)

        if random_rarity <= 500:
            self.rarity = "Common"
        elif random_rarity <= 700:
            self.rarity = "Uncommon"
        elif random_rarity <= 850:
            self.rarity = "Rare"
        elif random_rarity <= 950:
            self.rarity = "Epic"
        elif random_rarity <= 999:
            self.rarity = "Legendary"
        else:
            self.rarity = "Mythic"
