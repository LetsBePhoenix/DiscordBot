'''
Klasse Boss
'''
import json
from random import randint

from cDirectory import Directory


class Boss:
    def __init__(self, stage):
        self.directory = Directory()
        self.name = ""
        self.hp = 0
        self.exp = 0
        self.dmg_min = 0
        self.dmg_max = 0

        self.create_boss(stage)

    def create_boss(self, stage):
        if stage == 1:
            file_path = self.directory.stage1
        else:
            file_path = self.directory.stage2

        with open(file_path, "r") as file:
            data = json.load(file)
            self.name = data["boss"]["name"]
            self.hp = data["boss"]["hp"]
            self.exp = randint(data["boss"]["exp_min"], data["boss"]["exp_max"])
            self.dmg_min = data["boss"]["dmg_min"]
            self.dmg_max = data["boss"]["dmg_max"]
