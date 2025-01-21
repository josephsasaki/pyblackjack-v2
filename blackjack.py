import settings
from cards import Card, Deck, Hand
from has_hands import Player, Dealer
import interface


class Blackjack():
    """Class representing a game of blackjack."""

    def __init__(self):
        self.deck = None
        self.player = None
        self.dealer = Dealer()

    def play(self):
        interface.display_title()


if __name__ == "__main__":
    blackjack = Blackjack()
    blackjack.play()
