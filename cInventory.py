# Klasse Inventory
import json
import os.path


class Inventory:
    def __init__(self, playerID):
        self.playerID = str(playerID)
        self.coin = 0
        self.load_inventory()

    def load_inventory(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                if "inv" in data:
                    self.coin = data["inv"]["coin"]

    def save_inventory(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
        else:
            data = {}

        data["inv"] = {
            "coin": self.coin
        }

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
