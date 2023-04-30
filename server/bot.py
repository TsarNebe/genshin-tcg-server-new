import random

class Bot:
    def __init__(self, deck):
        self.deck = deck
        self.health = 10
        self.energy = 0

    def play_card(self):
        hand = self.deck.draw(1)
        if hand:
            card = random.choice(hand)
            self.energy += card.cost
            self.health += card.damage
            return card
        return None

    def start_game(self):
        while self.health > 0:
            card = self.play_card()
            if not card:
                break
            print(f"Bot played {card.name}, energy: {self.energy}, health: {self.health}")
