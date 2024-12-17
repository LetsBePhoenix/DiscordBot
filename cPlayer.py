'''
Klasse Spieler

Erzeugt und verwaltet den Spieler
'''
import json
import time
import datetime

from cDirectory import Directory


class Player:
    def __init__(self, playerName, playerID):
        self.directory = Directory()
        self.playerName = playerName
        self.playerID = playerID
        self.stats = Stats(playerID)
        self.cooldown = CoolDown(playerID)
        self.inventory = Inventory(playerID)

        self.get_player_id()
        self.player_load()

    def get_player_id(self):
        try:
            with open(self.directory.playerLibrary, "r") as file:
                data = json.load(file)
                if data[self.playerName] != self.playerID:
                    print("Fehler beim PlayerID lesen!")
                    self.create_player()
        except:
            print(f"{self.playerName}:{self.playerID}, existiert noch nicht.")
            self.create_player()

    def create_player(self):
        # Lade und speicher Spieler ID/Name in Library
        with open(self.directory.playerLibrary, "r") as file:
            data = json.load(file)

        data [self.playerName] = self.playerID

        with open(self.directory.playerLibrary, "w") as file:
            json.dump(data, file, indent=4)

        # Erstelle Stats und Inv
        self.stats.save()
        self.cooldown.save()
        self.inventory.save()

    def player_load(self):
        self.stats.load()
        self.cooldown.load()
        self.inventory.load()



class Stats:
    def __init__(self, playerID):
        self.playerID = playerID
        self.hp = 10
        self.hp_max = None
        self.mp = 20
        self.dmg = 5
        self.exp = 0
        self.lvl = 1
        self.stage_current = 1
        self.stage_max = 1

    def save(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
        except:
            data = {}
        data["stats"] = {
            "hp": self.hp,
            "mp": self.mp,
            "exp": self.exp,
            "lvl": self.lvl,
            "stage_current": self.stage_current,
            "stage_max": self.stage_max
        }
        with open (file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load(self):
        # Lade daten aus player
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            self.hp = data["stats"]["hp"]
            self.mp = data["stats"]["mp"]
            self.exp = data["stats"]["exp"]
            self.lvl = data["stats"]["lvl"]
            self.stage_current = data["stats"]["stage_current"]
            self.stage_max = data["stats"]["stage_max"]

        # Try levelup
        while self.exp >= self.next_level():
            self.exp -= self.next_level()
            self.lvl += 1

        # Lade daten aus Level
        file_path = "data\\dataLibrary\\playerDefaultStats.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            self.hp_max = data[f"lvl{self.lvl}"]["hp"]


    def next_level(self):
        level_file_path = f"data\\dataLibrary\\playerLevel.json"
        with open(level_file_path, "r") as file:
            data = json.load(file)
            nextLevel = f"lvl{self.lvl + 1}"
            return data[nextLevel]

class Inventory:
    def __init__(self, playerID):
        self.playerID = playerID
        self.coin = 0
        self.potion_healing = 0
        self.key_dungeon = 0

    def save(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
        data["inventory"] = {
            "coin": self.coin,
            "potion_healing": self.potion_healing,
            "key_dungeon": self.key_dungeon
        }
        with open (file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            self.coin = data["inventory"]["coin"]
            self.potion_healing = data["inventory"]["potion_healing"]
            self.key_dungeon = data["inventory"]["key_dungeon"]

class CoolDown:
    def __init__(self, playerID):
        self.playerID = playerID
        self.cd_hunt = 0
        self.cd_info = 0
        self.cd_search = 0
        self.cd_mine = 0
        self.cd_daily = 0
        self.cd_boss = 0

    def save(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
        data["cd"] = {
            "cd_hunt": self.cd_hunt,
            "cd_info": self.cd_info,
            "cd_search": self.cd_search,
            "cd_mine": self.cd_mine,
            "cd_daily": self.cd_daily,
            "cd_boss": self.cd_boss
        }
        with open (file_path, "w") as file:
            json.dump(data, file, indent=4)

    def load(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        with open(file_path, "r") as file:
            data = json.load(file)
            self.cd_hunt = data["cd"]["cd_hunt"]
            self.cd_info = data["cd"]["cd_info"]
            self.cd_search = data["cd"]["cd_search"]
            self.cd_mine = data["cd"]["cd_mine"]
            self.cd_daily = data["cd"]["cd_daily"]
            self.cd_boss = data["cd"]["cd_boss"]

    def test_cd(self, type):
        if type == "hunt":
            if self.cd_hunt + 60 <= round(time.time()):
                self.cd_hunt = round(time.time())
                self.save()
                return True
            else:
                return False
        if type == "info":
            if self.cd_info + 10 <= round(time.time()):
                self.cd_info = round(time.time())
                self.save()
                return True
            else:
                return False
        if type == "search":
            if self.cd_search + 60 <= round(time.time()):
                self.cd_search = round(time.time())
                self.save()
                return True
            else:
                return False
        if type == "daily":
            if self.cd_daily != str(datetime.date.today()):
                self.cd_daily = str(datetime.date.today())
                self.save()
                return True
            else:
                return False
        if type == "boss":
            if self.cd_boss + 10 <= round(time.time()):
                self.cd_boss = round(time.time())
                self.save()
                return True
            else:
                return False

    def get_time_cd(self, type):
        if type == "hunt":
            cd = 60
            if self.cd_hunt + cd <= round(time.time()):
                return "Ready"
            else:
                return f"{self.cd_hunt + cd - round(time.time())}s"
        if type == "info":
            cd = 10
            if self.cd_info + cd <= round(time.time()):
                return "Ready"
            else:
                return f"{self.cd_info + cd - round(time.time())}s"
        if type == "search":
            cd = 60
            if self.cd_search + cd <= round(time.time()):
                return "Ready"
            else:
                return f"{self.cd_search + cd - round(time.time())}s"
        if type == "daily":
            if self.cd_daily == str(datetime.date.today()):
                return "Already collected"
            else:
                return "Ready"
        if type == "boss":
            cd = 10
            if self.cd_boss + cd <= round(time.time()):
                return "Ready"
            else:
                return f"{self.cd_boss + cd - round(time.time())}"
