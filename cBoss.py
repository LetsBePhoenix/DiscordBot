import json


class Boss:
    def __init__(self, stage):
        self.name = ""
        self.stage = stage
        self.hp = 0
        self.exp_min = 0
        self.exp_max = 0
        self.dmg_min = 0
        self.dmg_max = 0
        self.load_boss()

    def load_boss(self):
        file_name = f"data\\dataEnemy\\stage{self.stage}.json"
        with open(file_name, "r") as file:
            data = json.load(file)
            self.name = data["boss"]["name"]
            self.hp = data["boss"]["hp"]
            self.exp_min = data["boss"]["exp_min"]
            self.exp_max = data["boss"]["exp_max"]
            self.dmg_min = data["boss"]["dmg_min"]
            self.dmg_max = data["boss"]["dmg_max"]
