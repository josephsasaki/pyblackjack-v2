import settings
from random import Random


class Card():
    """
    Class representing a single card. Each card has a rank and suit.
    """

    SUITS = ["♠", "♦", "♥", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6",
                  "7", "8", "9", "10", "J", "Q", "K"]

    def __init__(self, rank: str, suit: str) -> None:
        if rank not in Card.RANKS:
            raise ValueError("Invalid rank passed.")
        if suit not in Card.SUITS:
            raise ValueError("Invalid suit passed.")
        self.__rank = rank
        self.__suit = suit

    def get_rank(self) -> str:
        """Returns the rank of the card."""
        return self.__rank

    def get_suit(self) -> str:
        """Returns the suit of the card"""
        return self.__suit

    def get_string(self) -> str:
        """Returns a formatted string representation of the card."""
        return self.__rank + self.__suit


class Deck():
    """
    Class representing a deck of cards. A deck of cards can be made by either 
    specifying the number of packs of cards (lots of 52), or by directly passing
    a list of cards (used for testing purposes.)
    """

    def __init__(self, number_of_decks: int):
        if not isinstance(number_of_decks, int):
            raise ValueError("Invalid number of decks passed.")
        if number_of_decks < 0 or number_of_decks > settings.MAX_DECK_PACKS:
            raise ValueError("Invalid number of decks passed.")
        self.__cards = []
        for _ in range(number_of_decks):
            for suit in Card.SUITS:
                for rank in Card.RANKS:
                    self.__cards.append(Card(rank, suit))

    @classmethod
    def pass_cards(cls, cards: list[Card]) -> "Deck":
        """
        Alternative constructor for making a deck of cards, used usually
        for testing purposes.
        """
        if not all(isinstance(card, Card) for card in cards):
            raise ValueError("All passed cards must be Card objects.")
        if len(cards) == 0:
            raise ValueError("Deck cannot be empty.")
        deck = cls(0)
        deck.__Deck_cards = cards
        return deck

    def draw(self) -> Card:
        """Draw a card from the deck. Takes the card in the zero index."""
        if len(self.__cards) == 0:
            raise ValueError("Taking card from empty deck.")
        return self.__cards.pop(0)

    def shuffle(self, seed: int) -> None:
        """Randomizes the deck of cards"""
        Random(seed).shuffle(self.__cards)


class Hand():
    """
    Object representing a person's hand, a collection of cards with an
    assigned bet amount. 
    """

    BLACKJACK = "blackjack"
    BUST = "bust"
    STUCK = "stuck"
    ACTIVE = "active"
    CURRENT = "current"

    def __init__(self, cards: list[Card] = None):
        if cards is None:
            self.__cards = []
        else:
            if not all(isinstance(card, Card) for card in cards):
                raise ValueError("All passed cards must be Card objects.")
            self.__cards = cards
        self.__bet = None
        self.__is_active = True

    def get_cards(self) -> list[Card]:
        """Get the cards in the hand."""
        return self.__cards

    def get_bet(self) -> int:
        """Get the bet associated with the hand."""
        return self.__bet

    def is_active(self) -> bool:
        """Get whether the hand is active."""
        return self.__is_active

    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        if not isinstance(card, Card):
            raise ValueError("Invalid card object passed.")
        self.__cards.append(card)

    def set_bet(self, bet: int):
        """Set the bet of a hand."""
        if not isinstance(bet, int):
            raise ValueError("Bet must be an integer.")
        if bet < settings.MINIMUM_BET:
            raise ValueError("Bet must be greater than minimum bet.")
        self.__bet = bet

    def deactivate(self) -> None:
        """Change a hand from active to inactive."""
        self.__is_active = False

    def get_score(self) -> int:
        """Returns the score of a hand."""
        hand = self.__cards
        # Check list is empty
        if len(hand) == 0:
            return 0
        # First, extract the ranks from the hand
        ranks = [card.get_rank() for card in hand]
        # Replace the jacks, queens and kings with a ten
        ranks = list(map(lambda rank: "10" if rank in {
            "J", "Q", "K"} else rank, ranks))
        # Get how many aces and remove from list
        aces_quantity = ranks.count("A")
        number_ranks = [int(rank) for rank in ranks if rank != "A"]
        # Add up the number ranks
        score = sum(number_ranks)
        # Check whether there are aces
        if aces_quantity == 0:
            return score
        # Add aces such that score is maximized but <= 21
        eleven_counter = aces_quantity
        aces_score = [11]*eleven_counter
        while sum(aces_score) + score > 21 and eleven_counter > 0:
            eleven_counter -= 1
            aces_score = [11]*eleven_counter + \
                [1]*(aces_quantity-eleven_counter)
        # Return final score
        return sum(aces_score) + score

    def is_blackjack(self) -> bool:
        """Returns whether a hand is a blackjack."""
        if self.get_score() != 21:
            return False
        if len(self.__cards) != 2:
            return False
        return True

    def is_bust(self) -> bool:
        """Check whether the hand has gone bust."""
        return self.get_score() > 21

    def has_pair(self) -> bool:
        """Check whether the hand has a pair. Used for splitting."""
        if self.number_of_cards() != 2:
            return False
        if self.__cards[0].get_rank() != self.__cards[1].get_rank():
            return False
        return True

    def split(self) -> Card:
        """Used for splitting a hand. Checks whether valid, and then pops one card."""
        if not self.has_pair():
            raise ValueError("Hand cannot be split.")
        return self.__cards.pop()

    def double_bet(self) -> None:
        """Doubles the bet of a hand, used for doubling-down."""
        self.__bet *= 2

    def get_card_by_index(self, index: int) -> Card:
        """Used specifically for getting the dealer's upcard and hole card."""
        if index not in {0, 1}:
            raise ValueError(
                "get_card_by_index method being used incorrectly.")
        return self.__cards[index]

    def get_string(self) -> str:
        """Returns a formatted string representing the cards in a hand."""
        return ", ".join([card.get_string() for card in self.__cards])
