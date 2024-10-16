class Enemy:
    def __init__(self, enemy_type: str, rarity: str, ep: int, att_dmg_min: int, att_dmg_max: int):
        self.enemy_type = enemy_type
        self.rarity = rarity
        self.ep = ep
        self.att_dmg_min = att_dmg_min
        self.att_dmg_max = att_dmg_max

    def __repr__(self):
        return (f"Enemy(Type: {self.enemy_type}, Rarity: {self.rarity}, EP: {self.ep}, "
                f"Attack Damage: {self.att_dmg_min} - {self.att_dmg_max})")