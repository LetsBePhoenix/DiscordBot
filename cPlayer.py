class Player:
    def __init__(self, exp: int, hp: int, mp: int, armor: Armor):
        self.exp = exp
        self.hp = hp
        self.mp = mp
        self.armor = armor

    def __repr__(self):
        return (f"Player(Exp: {self.exp}, HP: {self.hp}, MP: {self.mp}, "
                f"Armor: {self.armor})")