import json
import os


# Klasse SPIELER
class Player:
    def __init__(self, playerID, playerName):
        self.playerID = str(playerID)
        self.playerName = str(playerName)
        self.lvl = 1
        self.hp = 10
        self.mp = 20
        self.exp = 0
        self.stage_max = 3
        self.stage = 1
        self.load_player()

    # Spieler-Daten aus JSON laden
    def load_player(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                if "stats" in data:
                    self.hp = data["stats"]["hp"]
                    self.mp = data["stats"]["mp"]
                    self.lvl = data["stats"]["lvl"]
                    self.exp = data["stats"]["exp"]
                    self.stage = data["stats"]["stage"]
                    self.stage_max = data["stats"]["stage_max"]
        else:
            # Spieler existiert nicht, daher neue Datei mit Standardwerten erstellen
            self.save_player()

            # Füge spieler in die playerLibrary hinzu
            library_file_path = "data\\dataLibrary\\playerLibrary.json"
            if os.path.exists(library_file_path):
                with open(library_file_path, "r") as file:
                    try:
                        data = json.load(file)
                    except json.JSONDecodeError:
                        data = {}  # Falls die Datei leer oder beschädigt ist
            else:
                data = {}
            data[self.playerID] = self.playerName
            with open(library_file_path, "w") as file:
                json.dump(data, file, indent=4)

    def save_player(self):
        if os.path.exists(f"data\\dataPlayer\\{self.playerID}.json"):
            with open(f"data\\dataPlayer\\{self.playerID}.json", "r") as file:
                data = json.load(file)
        else:
            data = {}

        data["stats"] = {
            "hp": self.hp,
            "mp": self.mp,
            "lvl": self.lvl,
            "exp": self.exp,
            "stage": self.stage,
            "stage_max": self.stage_max
        }

        with open(f"data\\dataPlayer\\{self.playerID}.json", "w") as file:
            json.dump(data, file, indent=4)

    def try_levelup(self, lvl):
        level_file_path = f"data\\dataLibrary\\playerLevel.json"
        with open(level_file_path, "r") as file:
            data = json.load(file)
            nextLevel = f"lvl{lvl}"

            if int(data[nextLevel]) <= self.exp:
                self.exp -= data[nextLevel]
                self.lvl += 1
