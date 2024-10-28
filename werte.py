import json

# Initialisieren der Werte
levels = {}
levels[1] = 10

# Schleife über die Level bis 100
for level in range(2, 501):
    if level <= 5:
        # Steigerung um 100%
        levels[level] = levels[level - 1] * 2
    elif 6 <= level <= 15:
        # Steigerung um 50%
        levels[level] = int(levels[level - 1] * 1.5)
    elif 16 <= level <= 100:
        # Steigerung um 10%
        levels[level] = int(levels[level - 1] * 1.1)
    else:
        # Steigerung um 5%
        levels[level] = int(levels[level -1] * 1.05)

# JSON formatieren
levels_json = json.dumps(levels, indent=4)
print(levels_json)