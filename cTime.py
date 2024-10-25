import datetime
import json
import os.path
import time


class Time:
    def __init__(self, playerID):
        self.playerID = playerID
        self.cd_hunt = 0
        self.cd_info = 0
        self.cd_search = 0
        self.cd_daily = 0

        self.getcd()

    def getcd(self):
        file_path = f"data\\dataPlayer\\{self.playerID}.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)
                if "cd" in data:
                    self.cd_hunt = data["cd"]["cd_hunt"]
                    self.cd_info = data["cd"]["cd_info"]
                    self.cd_search = data["cd"]["cd_search"]
                    self.cd_daily = data["cd"]["cd_daily"]

    def savecd(self):
        if os.path.exists(f"data\\dataPlayer\\{self.playerID}.json"):
            with open(f"data\\dataPlayer\\{self.playerID}.json", "r") as file:
                data = json.load(file)
        else:
            data = {}

        data["cd"] = {
            "cd_hunt": self.cd_hunt,
            "cd_info": self.cd_info,
            "cd_search": self.cd_search,
            "cd_daily": self.cd_daily
        }
        with open(f"data\\dataPlayer\\{self.playerID}.json", "w") as file:
            json.dump(data, file, indent=4)

    def testcd(self, type):
        if type == "hunt":
            if self.cd_hunt + 60 <= round(time.time()):
                self.cd_hunt = round(time.time())
                self.savecd()
                return True
            else:
                return False
        if type == "info":
            if self.cd_info + 10 <= round(time.time()):
                self.cd_info = round(time.time())
                self.savecd()
                return True
            else:
                return False
        if type == "search":
            if self.cd_search + 60 <= round(time.time()):
                self.cd_search = round(time.time())
                self.savecd()
                return True
            else:
                return False
        if type == "daily":
            if self.cd_daily != str(datetime.date.today()):
                self.cd_daily = str(datetime.date.today())
                self.savecd()
                return True
            else:
                return False

    def gettimecd(self, type):
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
