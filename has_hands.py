import settings
from cards import Card, Deck, Hand
from abc import ABC, abstractmethod


class HasHands(ABC):
    """Object representing a person who can have hands."""

    HIT = "hit"
    STICK = "stick"
    SPLIT = "split"
    DOUBLE_DOWN = "double-down"

    @abstractmethod
    def get_hand(self) -> Hand:
        """Abstract method for getting hand, with different implementations depending on whether
        is a player or dealer."""
        pass

    @abstractmethod
    def give_hand(self) -> None:
        """Abstract method for giving a hand. For players, this means appending, and for the dealer
        this means setting."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Abstract method for resetting after a round has been completed."""
        pass

    def hit(self, deck: Deck, hand: Hand = None) -> None:
        """Method for hitting, where a card is drawn from the deck and added to the next hand.
        Also checks whether the hand is now inactive."""
        if hand is None:
            hand = self.get_hand()
        drawn_card = deck.draw()
        hand.add_card(drawn_card)
        if hand.is_bust() or len(hand.get_cards()) == 5:
            hand.deactivate()

    def stick(self, hand: Hand = None) -> None:
        """Get the next active hand and deactivate it."""
        if hand is None:
            hand = self.get_hand()
        hand.deactivate()


class Player(HasHands):
    """
    Object representing a player. Unlike the dealer, players can have multiple hands.
    """

    def __init__(self, name: str, purse: int):
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        if name == "":
            raise ValueError("Name cannot be empty.")
        if not isinstance(purse, int):
            raise TypeError("Purse amount must be an integer.")
        self.__name = name
        self.__purse = purse
        self.__hands = []
        self.__split_count = 0

    def get_all_hands(self):
        """Method which returns all the player's hands."""
        return self.__hands

    def get_name(self) -> str:
        """Get the player's name."""
        return self.__name

    def get_purse(self) -> int:
        """Return's the player's purse amount."""

    def get_hand(self) -> Hand | None:
        """Implementation of the abstract method. For a player, getting a hand means getting the
        first active hand in the list of hands. If there are no active hands, None is returned."""
        for hand in self.__hands:
            if hand.is_active():
                return hand
        return None

    def give_hand(self, hand: Hand) -> None:
        """Give a hand to the player, and append to list of hands."""
        if not isinstance(hand, Hand):
            raise ValueError("Hand object not passed.")
        self.__hands.append(hand)

    def can_split(self, hand: Hand = None):
        """Check whether the player's current hand can split."""
        if hand is None:
            hand = self.get_hand()
        if self.__purse < hand.get_bet():
            return False
        if self.__split_count >= settings.MAX_SPLITS:
            return False
        return hand.has_pair()

    def split(self, deck: Deck, hand: Hand = None):
        """Method which splits the player's current hand."""
        if hand is None:
            hand = self.get_hand()
        self.__split_count += 1
        # Take a further bet from the player
        self.__purse -= hand.get_bet()
        # Take the second card and produce a new hand
        second_card = hand.get_cards().pop()
        split_hand = Hand(cards=[second_card])
        split_hand.set_bet(hand.get_bet())
        # Hit each hand with a new card
        self.hit(deck, hand)
        self.hit(deck, split_hand)
        # give player the new hand
        self.give_hand(split_hand)

    def can_double_down(self, hand: Hand = None):
        """Check whether the player can double-down, meaning the player has enough
        money and they haven't hit yet."""
        if hand is None:
            hand = self.get_hand()
        return self.__purse >= hand.get_bet() and len(hand.get_cards()) == 2

    def double_down(self, deck: Deck, hand: Hand = None):
        """Double-down on a hand, where the bet doubles and hit once more and then stuck."""
        # Take the further bet from the player
        if hand is None:
            hand = self.get_hand()
        self.__purse -= hand.get_bet()
        self.hit(deck, hand)
        hand.double_bet()
        hand.deactivate()

    def get_action_choices(self, hand: Hand = None):
        """Get the choices of actions for a hand."""
        if hand is None:
            hand = self.get_hand()
        actions = [HasHands.HIT, HasHands.STICK]
        if self.can_split(hand):
            actions.append(HasHands.SPLIT)
        if self.can_double_down(hand):
            actions.append(HasHands.DOUBLE_DOWN)
        return actions

    def reset(self) -> None:
        """Resets the player's round attributes."""
        self.__hands = []
        self.__split_count = 0


class Dealer(HasHands):
    """
    Object representing a dealer. Unlike a player, the dealer only has one hand.
    """

    def __init__(self):
        self.__hand = None

    def give_hand(self, hand: Hand) -> None:
        """Give a hand to the dealer"""
        if not isinstance(hand, Hand):
            raise ValueError("Hand object not passed.")
        self.__hand = hand

    def get_hand(self) -> Hand | None:
        """Implementation of the abstract method. For the dealer, there is only one hand,
        which is returned from this method."""
        return self.__hand

    def reset(self) -> None:
        """Resets the dealer's round attributes"""
        self.__hand = None

    def upcard(self) -> Card:
        """Returns the dealer's upcard."""
        return self.__hand.get_card_by_index(1)

    def hole_card(self) -> Card:
        """Returns the dealer's hold card."""
        return self.__hand.get_card_by_index(0)

    def can_offer_insurance(self) -> bool:
        """Check whether the dealer is in a position to offer insurance bet."""
        return self.upcard().get_rank() == "A"
