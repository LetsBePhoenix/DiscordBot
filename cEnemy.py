import json
import os
import random

import discord


# Klasse GEGNER
class Enemy:
    def __init__(self, stage):
        self.type = ""
        self.name = ""
        self.stage = stage
        self.rarity = ""
        self.hp = 1
        self.hp_max = 1
        self.exp_min = 0
        self.exp_max = 0
        self.dmg_min = 0
        self.dmg_max = 0
        self.enemy_color = discord.Color.dark_grey()
        self.load_enemy_data()

    def load_enemy_data(self):
        self.get_enemy_from_stage()
        self.get_rarity()

        file_name = f"data\\dataEnemy\\stage{self.stage}.json"

        with open(file_name, "r") as file:
            data = json.load(file)
            self.name = data[self.type]["name"]
            self.hp_max = data[self.type]["hp"]
            self.hp = self.hp_max
            self.exp_min = data[self.type]["exp_min"]
            self.exp_max = data[self.type]["exp_max"]
            self.dmg_min = data[self.type]["dmg_min"]
            self.dmg_max = data[self.type]["dmg_max"]

        # set values from rarity
        if self.rarity == "Uncommon":
            self.exp_min = round(self.exp_min * 1.1)
            self.exp_max = round(self.exp_max * 1.1)
            self.enemy_color = discord.Color.light_grey()
        elif self.rarity == "Rare":
            self.exp_min = round(self.exp_min * 1.2)
            self.exp_max = round(self.exp_max * 1.2)
            self.enemy_color = discord.Color.green()
        elif self.rarity == "Epic":
            self.exp_min = round(self.exp_min * 1.5)
            self.exp_max = round(self.exp_max * 1.5)
            self.enemy_color = discord.Color.purple()
        elif self.rarity == "Legendary":
            self.exp_min = round(self.exp_min * 2)
            self.exp_max = round(self.exp_max * 2)
            self.enemy_color = discord.Color.gold()
        elif self.rarity == "Mythic":
            self.exp_min = round(self.exp_min * 5)
            self.exp_max = round(self.exp_max * 5)
            self.enemy_color = discord.Color.pink()

    def get_enemy_from_stage(self):
        if self.stage == 1:
            randtype = random.randint(1, 100)
            if randtype <= 40:
                self.type = "deer"
            elif randtype <= 80:
                self.type = "boar"
            else:
                self.type = "wolf"
        if self.stage == 2:
            randtype = random.randint(1, 100)
            if randtype <= 40:
                self.type = "slime"
            elif randtype <= 80:
                self.type = "living_rock"
            else:
                self.type = "rock_wolf"
        if self.stage == 3:
            randtype = random.randint(1, 100)
            if randtype <= 40:
                self.type = "ice_slime"
            elif randtype <= 80:
                self.type = "ice_wolf"
            else:
                self.type = "ice_worm"

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
