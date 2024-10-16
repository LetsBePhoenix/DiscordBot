class Armor:
    def __init__(self, toughness: int):
        self.toughness = toughness

    def __repr__(self):
        return f"Armor(Toughness: {self.toughness})"