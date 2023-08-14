#!/usr/bin/env python3

# TODO:
#  - only be able to end game on the second round
#  - only be able to use power cards if you get them from the deck, not the discard pile
#  - make AI smarter
#  - color code cards based on value/power
#  - make UI better overall?
#  - during SWAP, the person who used it can see what card they got


import os
import random
import time

from colorama import *

init(autoreset=True)  # for colorama library

# initialize the deck
deck = []
for i in range(4):
    for value in range(9):
        deck.append(str(value))
for i in range(3):
    deck.append("PEEK")
    deck.append("SWAP")
    deck.append("DRAW2")
for i in range(9):
    deck.append("9")


# function to draw a random card from the deck
def draw_card():
    idx = random.randint(0, len(deck) - 1)
    return_val = deck[idx]
    deck.pop(idx)
    return return_val


# the top of the discard pile is a global variable; every player should be able to see it
top_discard = draw_card()


def clear():
    os.system('clear')


def rules():
    print(
        "Rat-a-tat-cat is a memory card game where the lowest points wins. Throughout the game, your hand will be "
        "facedown, although you can look at two of your cards before the game starts.\n\nEach turn, you'll draw a card,"
        " and exchange it for a card in your hand. You can look at the cards you're exchanging, but no other cards!\n\n"
        "When you feel like you have a lower score than everybody else, type 'CAT' to end the round, reveal everyone's"
        " cards, and tally up the points.\n\n\nThe deck is made up of cards 0-9, along with DRAW2, SWAP, and PEEK.\n\n"
        "DRAW2: discard this card and draw two cards from the deck. You can look at them both and decide which one to "
        "exchange.\n\nSWAP: you must swap one of your cards with another player's cards.\n\nPEEK: you may look at one "
        "of your cards\n\n(If you have any of these cards in your hand when the round ends, they will be replaced with "
        "a random card from the deck.)")


# interface ExchangeFunction
# void run_func(Player p, int playerIndex);

# Normal exchange. First you pick which existing card you want to discard, then add the new card to your hand,
# replacing that discarded one.
class Normal:
    def __init__(self, new_card, player, player_index, all_players, hidden):
        self.new_card = new_card
        self.player = player
        self.player_index = player_index
        self.all_players = all_players
        self.hidden = hidden

    # runs this function object on the given player
    def run_func(self):
        global top_discard
        # idx is the index of the old card that is being discarded
        idx = -1
        while idx < 0 or idx > 3:  # keep prompting them to pick a number until it's valid
            if self.player.is_bot():
                idx = random.randint(0, 3)
            else:
                try:
                    idx = int(input("Type which card in your hand you want to discard (1-4)\n\n")) - 1
                except TypeError:  # in case they type a string
                    print("\n\nERROR: please type an integer between 1 and 4\n\n")
            if idx < 0 or idx > 3:  # in case they type a number out of bounds
                print("\n\nERROR: please type an integer between 1 and 4\n\n")

        hand = self.player.get_hand()
        old_card = hand[idx]
        hand[idx] = self.new_card  # mutates this player's hand (tbh I'm not sure why this works)
        top_discard = old_card
        if self.hidden:
            bot_hand_printed = "?? " * idx + "%s " % (Fore.LIGHTBLUE_EX + "??" + Style.RESET_ALL) + "?? " * \
                               (3 - idx) + "\t"
        else:
            bot_hand_printed = "?? " * idx + "%s " % (Fore.LIGHTBLUE_EX + hand[idx] + Style.RESET_ALL) + "?? " * \
                               (3 - idx) + "\t"
        human_hand_printed = "??\t" * idx + "%s\t" % (Fore.CYAN + hand[idx] + Style.RESET_ALL) + "??\t" * \
                             (3 - idx)
        if not self.player.is_bot():
            print("\n\n" + human_hand_printed + "\n\n")
        else:
            print("\n\n" + "?? ?? ?? ?? \t" * self.player_index + bot_hand_printed +
                  "?? ?? ?? ?? \t" * (len(self.all_players) - self.player_index - 1) + "\n\n")
        if self.hidden:
            new = "??"
        else:
            new = self.new_card
        print("%s exchanged %s for %s\n\n" % (self.player.get_name(), Fore.LIGHTBLUE_EX + old_card + Style.RESET_ALL,
                                              Fore.LIGHTBLUE_EX + new))


# Peek: choose a card in your hand to reveal, then hide it again
class Peek:
    def __init__(self, new_card, player):
        self.new_card = new_card
        self.player = player

    # runs this function object on the given player
    def run_func(self):
        global top_discard
        if self.player.is_bot():  # only execute this function if this player is human
            print("%s played a PEEK card\n\n" % self.player.get_name())
        else:
            # idx is the index of the card that's being looked at
            idx = -1
            while idx < 0 or idx > 3:  # keep prompting them to pick a number until it's valid
                try:
                    idx = int(input("Type which card in your hand you want to look at (1-4)\n\n")) - 1
                except TypeError:
                    print("\n\nERROR: please type an integer between 1 and 4\n\n")
                if idx < 0 or idx > 3:
                    print("\n\nERROR: please type an integer between 1 and 4\n\n")

            hand = self.player.get_hand()
            top_discard = self.new_card  # discard the peek card
            hand_printed = "\n\n" + "??\t" * idx + "%s\t" % (Fore.CYAN + hand[idx] + Style.RESET_ALL) + "??\t" * \
                           (3 - idx) + "\n\n"
            print(hand_printed)


# Draw 2: draw two new cards from the deck, choose which one to keep, and perform a normal exchange with that one.
class Draw2:
    def __init__(self, new_card, player, player_index, all_players, hidden):
        self.player = player
        self.new_card = new_card
        self.player_index = player_index
        self.all_players = all_players
        self.hidden = hidden

    # runs this function object on the given player
    def run_func(self):
        global top_discard
        top_discard = self.new_card
        card_one = draw_card()
        card_two = draw_card()
        if self.player.is_bot():  # bot randomly chooses which card to draw
            choice = str(random.randint(1, 2))
        else:
            choice = input("\nYour new cards are:\n1) %s\n2) %s\n\nWhich would you like to keep? (1-2)" %
                           (card_one, card_two))
        if choice == "1":
            print("%s is playing first card: %s" % (self.player.get_name(), card_one))
            self.player.play(card_one, self.player_index, self.all_players, self.hidden)
        if choice == "2":
            print("%s playing second card: %s" % (self.player.get_name(), card_two))
            self.player.play(card_two, self.player_index, self.all_players, self.hidden)


# Swap: choose a card in your hand, then a card in some other player's hand, and swap them with each other.
class Swap:
    def __init__(self, new_card, player, player_index, all_players):
        self.player = player
        self.new_card = new_card
        self.player_index = player_index
        self.all_players = all_players

    # runs this function object on the given player
    def run_func(self):
        global top_discard
        # TODO: make this method less stupid
        # first ask for which card to swap (1-4)
        idx_1 = -1
        while idx_1 < 0 or idx_1 > 3:  # keep prompting them to pick a number until it's valid
            if self.player.is_bot():
                idx_1 = random.randint(0, 3)
            else:
                try:
                    idx_1 = int(input("Type which card in your hand you want to swap (1-4)\n\n")) - 1
                except TypeError:  # in case they type a string
                    print("\n\nERROR: please type an integer between 1 and 4\n\n")
            if idx_1 < 0 or idx_1 > 3:  # in case they type a number out of bounds
                print("\n\nERROR: please type an integer between 1 and 4\n\n")
        this_hand = self.player.get_hand()
        this_card = this_hand[idx_1]

        # ask for which player to swap with (2-4)
        idx_2 = -1
        while idx_2 < 1 or idx_2 > 3:  # keep prompting them to pick a number until it's valid
            if self.player.is_bot():
                idx_2 = random.randint(1, 3)
            else:
                try:
                    idx_2 = int(input("Type which player you'd like to swap with (2-4)\n\n")) - 1
                except TypeError:  # in case they type a string
                    print("\n\nERROR: please type an integer between 2 and 4\n\n")
            if idx_2 < 0 or idx_2 > 3:  # in case they type a number out of bounds
                print("\n\nERROR: please type an integer between 2 and 4\n\n")
        other_player = self.all_players[idx_2]
        other_hand = other_player.get_hand()

        # then ask which card of the other player's to take (1-4)
        idx_3 = -1
        while idx_3 < 0 or idx_3 > 3:  # keep prompting them to pick a number until it's valid
            if self.player.is_bot():
                idx_3 = random.randint(0, 3)
            else:
                try:
                    idx_3 = int(input("Type which card of theirs you'd like to take (1-4)\n\n")) - 1
                except TypeError:  # in case they type a string
                    print("\n\nERROR: please type an integer between 1 and 4\n\n")
            if idx_3 < 0 or idx_3 > 3:  # in case they type a number out of bounds
                print("\n\nERROR: please type an integer between 1 and 4\n\n")
        other_card = other_hand[idx_3]

        # then mutate each player's hand, and make top_discard the swap card
        this_hand[idx_1] = other_card
        other_hand[idx_3] = this_card
        top_discard = self.new_card

        # then print a screen showing the swap
        this_hand_printed = "??\t" * idx_1 + (Fore.CYAN + "??\t" + Style.RESET_ALL) + "??\t" * (3 - idx_1)
        other_hand_printed = "??\t" * idx_3 + (Fore.LIGHTBLUE_EX + "??\t" + Style.RESET_ALL) + "??\t" * (3 - idx_3)
        names = self.player.get_name() + ("\t" * 5) + other_player.get_name()
        print("\n\n" + names + "\n\n" + this_hand_printed + "\t" + other_hand_printed + "\n\n")


# Represents a game player, either human or AI
class Player:
    def __init__(self, name, isBot=True):
        self.name = name
        self.hand = [draw_card(), draw_card(), draw_card(), draw_card()]
        self.bot = isBot

    # Perform a normal exchange, or one of the power cards, based on what card you drew
    def play(self, new_card, player_index, all_players, hidden=False):
        if new_card == "PEEK":
            Peek(new_card, self).run_func()
        elif new_card == "DRAW2":
            Draw2(new_card, self, player_index, all_players, hidden).run_func()
        elif new_card == "SWAP":
            Swap(new_card, self, player_index, all_players).run_func()
        else:
            Normal(new_card, self, player_index, all_players, hidden).run_func()
        blah = input("Press ENTER to continue")
        if blah == "":
            pass

    # Returns the card at the given index as a String
    def get_card(self, idx):
        return self.hand[idx]

    # Calculates this player's score by adding up the values of each card in their hand. Power cards are replaced with
    # a random card from the deck.
    def calc_score(self):
        # print("%s's hand before: %s" % (self.get_name(), self.get_hand()))
        self.hand = [finalize_hand(card) for card in self.hand]
        hand_as_ints = [int(card) for card in self.hand]
        score = 0
        for card in hand_as_ints:
            score += card
        return score

    # I've been told getters and setters are cringe so lmk if you have any better ideas

    def get_name(self):
        return self.name

    def get_hand(self):
        return self.hand

    def is_bot(self):
        return self.bot

    def set_name(self, new_name):
        self.name = new_name


# Exchanges this card with a random one from the deck if it's a power card
def finalize_hand(card):
    next_card = card
    while next_card == "SWAP" or next_card == "DRAW2" or next_card == "PEEK":  # loop until you get a number card
        next_card = draw_card()
    return next_card


# End the game and print each player's hands and scores
def end_game(players):
    print("\nGAME OVER")
    for x in players:
        print("%s: %s points\t%s" % (x.get_name(), x.calc_score(), x.get_hand()))
    lowest_score = min([x.calc_score() for x in players])
    winner = [x.get_name() for x in players if x.calc_score() == lowest_score]  # could have multiple winners
    winner = ' '.join(map(str, winner))
    win_screen = "\nWinner(s): %s!!\n\n" % winner
    print(win_screen)


wait_time = 2


# Run the game
def run_game(players):
    global top_discard
    turn_order = {}  # A map of player names to numbers, representing what order they do their turn
    for count, player in enumerate(players):
        turn_order[count] = player
    turn_counter = 0

    while True:
        clear()
        current_player = turn_order[turn_counter % len(players)]
        if current_player.is_bot():  # Runs code for bots
            boolean = random.randint(0, 1)
            if boolean == 0:
                print("%s is playing the discard card, %s\n" % (current_player.get_name(), top_discard))
                current_player.play(top_discard, turn_counter % len(players), players)
            else:
                print("%s is playing a card they drew from the deck\n" % current_player.get_name())
                current_player.play(draw_card(), turn_counter % len(players), players, hidden=True)
            turn_counter += 1
            continue
        print("%s'S TURN" % (Style.BRIGHT + current_player.get_name().upper()))
        print("Your cards are:\t\t??\t??\t??\t??\n")
        first_input = input(Style.BRIGHT + "\nTop discard card is: \n\n%s\n\nPress Y and ENTER to take card, "
                                           "N and ENTER to draw from the deck instead\n\n" % top_discard +
                            Style.RESET_ALL)
        if first_input.upper() == "Y":  # Take the discard card
            clear()
            current_player.play(top_discard, turn_counter % len(players), players)
        if first_input.upper() == "N":  # Look at the top card of the deck instead
            top_deck = draw_card()
            print(Style.BRIGHT + "\nTop deck card: %s\n\n" % top_deck)
            second_input = input("Y to take card, N to leave it\n\n")
            if second_input.upper() == "Y":  # Take the top card of the deck
                clear()
                current_player.play(top_deck, turn_counter % len(players), players)
            if second_input.upper() == "N":  # Don't take either card
                print("\n\n%s did not take any cards\n\n" % current_player.get_name())
                time.sleep(wait_time)
                clear()
                top_discard = top_deck  # still discard the top deck card
        if first_input.upper() == "CAT":  # End game
            end_game(players)
            break
        turn_counter += 1  # Next player's turn


# Print the rules, initial hand reveal, etc
def start_screen(*args):
    global deck
    global top_discard
    num_of_players = len(args)
    clear()
    players = [x for x in args]
    rules()
    blah = input("\n\n\nTwo cards in your hand will display now. Take a good look, because they'll be hidden "
                 "after that! Press ENTER to continue")
    if blah == "":
        clear()
        print(
            "\nYour cards are:\t\t%s\t??\t??\t%s\n" % (
                Fore.CYAN + players[0].get_card(0) + Style.RESET_ALL, Fore.CYAN +
                players[0].get_card(3) + Style.RESET_ALL))
        blah = input("\n\nReady to play? Type your name, then press ENTER to continue 😻\n\n")
        if blah.isspace() or blah == "":
            pass  # name defaults to Luke 😎
        else:
            players[0].set_name(blah)
        run_game(players)


start_screen(Player("Luke", isBot=False), Player("Bot1"), Player("Bot2"), Player("Bot3"))
