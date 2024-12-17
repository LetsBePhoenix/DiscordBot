'''
Klasse cDirectory

Überprüft, ob die notwendigen Dateipfade vorhanden sind.
Gibt Dateipfade zurück
'''
import json
import os.path


class Directory:
    def __init__(self):
        # dataEnemy
        self.stage1 = ""
        self.stage2 = ""
        # dataPlayer
        self.playerLibrary = ""
        self.playerLevel = ""
        self.playerDefaultStats = ""
        # dataLibrary
        self.globals = ""

        self.try_file_paths()

    def try_file_paths(self):
        file_path = "data\\dataLibrary\\directory.json" # Dateipfad des Directory
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                data = json.load(file)

                # Erstelle Arrays
                paths_enemy = ["", ""]
                paths_player = ["", "", ""]
                paths_library = [""]

                # dataEnemy
                self.stage1 = data["dataEnemy"]["stage1"]
                self.stage2 = data["dataEnemy"]["stage2"]
                paths_enemy[0] = self.stage1
                paths_enemy[1] = self.stage2

                # dataPlayer
                self.playerLibrary = data["dataPlayer"]["playerLibrary"]
                self.playerLevel = data["dataPlayer"]["playerLevel"]
                self.playerDefaultStats = data["dataPlayer"]["playerDefaultStats"]
                paths_player[0] = self.playerLibrary
                paths_player[1] = self.playerLevel
                paths_player[2] = self.playerDefaultStats

                # dataLibrary
                self.globals = data["dataLibrary"]["globals"]
                paths_library[0] = self.globals

            # Überprüfe, ob die Pfade existieren
            for i in paths_enemy:
                if not os.path.exists(i):
                    print(f"{i}, existiert nicht!")

            for i in paths_player:
                if not os.path.exists(i):
                    print(f"{i}, existiert nicht!")

            for i in paths_library:
                if not os.path.exists(i):
                    print(f"{i}, existiert nicht!")


