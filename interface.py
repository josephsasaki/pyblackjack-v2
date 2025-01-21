import settings
from cards import Card, Deck, Hand
from has_hands import Player, Dealer

from collections.abc import Callable
from rich import box
from rich.table import Table
from rich.console import ConsoleRenderable
from rich.console import Console, Group
from rich.panel import Panel
from rich.align import Align
from rich.padding import Padding
from rich.layout import Layout
from rich.columns import Columns
from time import sleep


CONSOLE_WIDTH = 180
CONSOLE = Console(width=CONSOLE_WIDTH)
TITLE_GRAPHIC = [
    "╭──╮╭╮╭╮.╭────╮.╭╮.....╭────╮.╭────╮.╭╮..╭╮.╭────╮.╭────╮.╭────╮.╭╮..╭╮.",
    "│╭╮││╰╯│.│╭──╮│.││.....│╭──╮│.│╭───╯.││..││.╰──╮╭╯.│╭──╮│.│╭───╯.││..││.",
    "│╰╯│╰─╮│.│╰──╯│.││.....││..││.││.....││.╭╯│....││..││..││.││.....││.╭╯│.",
    "│╭─╯╭╮││.│╭───╯.││.....│╰──╯│.││.....│╰─╯╭╯....││..│╰──╯│.││.....│╰─╯╭╯.",
    "││..│╰╯│.│╰───╮.││.....│╭──╮│.││.....│╭─╮╰╮....││..│╭──╮│.││.....│╭─╮╰╮.",
    "╰╯..╰──╯.│╭──╮│.││.....││..││.││.....││.│.│.╭╮.││..││..││.││.....││.│.│.",
    ".........│╰──╯│.│╰───╮.││..││.│╰───╮.││.│.│.│╰─╯│..││..││.│╰───╮.││.│.│.",
    ".........╰────╯.╰────╯.╰╯..╰╯.╰────╯.╰╯.╰─╯.╰───╯..╰╯..╰╯.╰────╯.╰╯.╰─╯.",
]


# ---------- VALIDATION FUNCTIONS ----------


def is_valid_enter(user_input: str, player: Player) -> bool | None:
    """
    Validation function which always returns true. Is used if the display requires
    the user to press enter to continue, in which case the input does not matter.
    """
    return True, None


def is_valid_deck_quantity(user_input: str, player: Player) -> bool | None:
    """
    Validation function for the number of decks. The number of decks must be
    between 1 and the maximum number of allowed decks.
    """
    if user_input not in [str(n) for n in range(1, settings.MAX_DECK_PACKS+1)]:
        return False, "[bold red]Invalid number of decks. Please try again.[/bold red]"
    return True, None


def is_valid_player_quantity(user_input: str, player: Player) -> bool | None:
    """
    Validation function for the number of players. The number of players must be
    between 1 and the maximum number of allowed players.
    """
    if user_input not in [str(n) for n in range(1, settings.MAX_PLAYERS+1)]:
        return False, "[bold red]Invalid number of players. Please try again.[/bold red]"
    return True, None


def is_valid_name(user_input: str, player: Player) -> bool:
    """
    Validation function for a player name. Must not be an empty string.
    """
    if user_input == "":
        return False, "[bold red]Invalid name. Please try again.[/bold red]"
    return True, None


def is_valid_purse_amount(user_input: str, player: Player) -> bool:
    """
    Validation function for a player's purse amount. This must be numeric, and greater
    than or equal to the minimum bet, to ensure the player can play at least one round.
    """
    if not user_input.isnumeric():
        return False, "[bold red]Invalid purse amount. Please try again.[/bold red]"
    amount = int(user_input)
    if amount < settings.MINIMUM_BET/100:
        return False, "[bold red]Invalid purse amount. Please try again.[/bold red]"
    return True, None


def is_valid_bet(user_input: str, player: Player) -> bool:
    """
    Validation function for a hand bet. This must be greater than the minimum bet, but less
    than the player's purse.
    """
    if not user_input.isnumeric():
        return False, "[bold red]Invalid bet amount. Please try again.[/bold red]"
    amount = int(user_input)
    if amount < settings.MINIMUM_BET/100:
        return False, "[bold red]Invalid bet amount. Please try again.[/bold red]"
    if amount > player.get_purse():
        return False, "[bold red]Invalid bet amount. Please try again.[/bold red]"
    return True, None


def is_valid_action(user_input: str, player: Player) -> bool:
    """
    Validation function for a player's action choice. The player must have chosen a 
    valid action given the hand.
    """
    action_choices = player.get_action_choices()
    if user_input not in action_choices:
        return False, "[bold red]Invalid action. Please try again.[/bold red]"
    return True, None


# ---------- GENERAL DISPLAY FUNCTIONS ----------


def _display_ask(content: list[ConsoleRenderable], invalid_message: str, validity_checker: Callable, is_valid: bool, player: Player) -> str:
    # Clear the screen
    CONSOLE.clear()
    # Check whether error message should be added at end of content, and it isn't already there.
    if not is_valid:
        if content[-1] != invalid_message:
            content.append(invalid_message)
    # Group content and display
    grouped_content = Group(*content)
    CONSOLE.print(grouped_content)
    # Take user input
    user_input = input("> ")
    # Validate user input using validation function
    is_valid, invalid_message = validity_checker(user_input, player=player)
    if not is_valid:
        return _display_ask(content, invalid_message, validity_checker, is_valid=False, player=player)
    else:
        return user_input


def _display_timed(content: list[ConsoleRenderable], delay: int) -> None:
    # Clear the screen
    CONSOLE.clear()
    # Group content and display
    grouped_content = Group(*content)
    CONSOLE.print(grouped_content)
    # Wait
    sleep(delay)
    return None


# ---------- SPECIFIC DISPLAY FUNCTIONS ----------


def display_title() -> str:
    title_content = [
        make_title_renderable(),
        Align.center("Welcome!", vertical="middle", style="bold"),
        make_padding(),
        "Please ensure your console window is large enough to fit the content.",
        make_padding(),
        "Once you are ready to proceed, please press [bold]ENTER[/bold].",
    ]
    _ = _display_ask(title_content, None, is_valid_enter, True, player=None)
    return None


# ---------- RENDERABLE MAKER FUNCTIONS ----------


def make_title_renderable() -> ConsoleRenderable:
    """
    Takes the title graphic and converts to a formatted string.
    """
    return Align.center("\n".join(TITLE_GRAPHIC).replace(".", " "), vertical="middle")


def make_padding() -> ConsoleRenderable:
    """
    Returns a 1 line padding object to place between renderable.
    """
    return Padding("", (1, 0, 0, 0))
