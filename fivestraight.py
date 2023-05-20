import random as rand
import numpy as np
import colorama
from colorama import Fore

# Default constants
BLACK = Fore.BLACK
BLUE = Fore.BLUE
CYAN = Fore.CYAN
GREEN = Fore.GREEN
MAGENTA = Fore.MAGENTA
RED = Fore.RED
WHITE = Fore.WHITE
YELLOW = Fore.YELLOW
RESET = Fore.RESET

# Constants upon initialization
VALID_NUM_PLAYERS = [4, 6, 8, 9]
VALID_NUM_TEAMS = [2, 3]
VALID_COLORS = ["WHITE", "BLUE", "CYAN", "GREEN", "MAGENTA", "RED", "YELLOW"]
COLOR_CODES = [WHITE, BLUE, CYAN, GREEN, MAGENTA, RED, YELLOW]
CARDS_PER_PLAYER = 4
ROWS = 10
COLS = 10
WIN_PEGS = 5
BOARD = np.array([
    [73, 72, 71, 70, 69, 68, 67, 66, 65,  0],
    [74, 57, 58, 59, 60, 61, 62, 63, 64, 99],
    [75, 56, 21, 20, 19, 18, 17, 36, 37, 98],
    [76, 55, 22, 13, 14, 15, 16, 35, 38, 97],
    [77, 54, 23, 12,  1,  4,  5, 34, 39, 96],
    [78, 53, 24, 11,  2,  3,  6, 33, 40, 95],
    [79, 52, 25, 10,  9,  8,  7, 32, 41, 94],
    [80, 51, 26, 27, 28, 29, 30, 31, 42, 93],
    [81, 50, 49, 48, 47, 46, 45, 44, 43, 92],
    [82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
])

# Constants after declaration
num_players = 0
num_teams = 0
player_names = []
team_colors = []

# Global variables
start_position = 0
all_cards = np.zeros(ROWS*COLS)
cards = []
modified_board = np.zeros((ROWS, COLS, 2))
still_playing = []

def setup():
    global num_players
    global start_position
    global all_cards
    global cards
    global modified_board
    global still_playing
    # Create deck, shuffle cards
    for i in range(ROWS*COLS):
        all_cards[i] = i
    for i in range(num_players):
        rand.shuffle(all_cards)   
    # Deal starting cards
    cards = np.reshape(all_cards[:start_position], (num_players, CARDS_PER_PLAYER)).astype(int)
    # Initialize board
    for i in range(ROWS):
        for j in range(COLS):
            modified_board[i][j] = np.array([0, BOARD[i][j]])
    # All players' statuses are valid
    still_playing = np.ones(num_players)

# Board display
def display_board():
    global modified_board
    print("\n")
    for i in range(ROWS):
        for j in range(COLS):
            cutoff = 2
            if (modified_board[i][j][1] < 10):
                print(" ", end="")
                cutoff -= 1
            print(COLOR_CODES[int(modified_board[i][j][0])] + str(modified_board[i][j][1])[:cutoff], end=" ")
        print("\n")

# Check if playing at this location is valid
def valid_move(loc):
    global modified_board
    indices = np.where(BOARD == loc)
    return modified_board[int(indices[0])][int(indices[1])][0] == COLOR_CODES.index(WHITE)

# Have specified player place a peg at this location
def make_move(loc, player_num):
    global team_colors
    global modified_board
    indices = np.where(BOARD == loc)
    modified_board[int(indices[0])][int(indices[1])][0] = COLOR_CODES.index(team_colors[player_num % num_teams])

# Check rows for a win
def check_rows():
    global modified_board
    for i in range(ROWS):
        for j in range(COLS - WIN_PEGS + 1):
            count = 1
            cur_color_idx = modified_board[i][j][0]
            while (cur_color_idx == modified_board[i][j + count][0]) and (cur_color_idx != 0):
                count += 1
                if (count >= WIN_PEGS):
                    return True
    return False

# Check columns for a win
def check_cols():
    global modified_board
    for i in range(ROWS - WIN_PEGS + 1):
        for j in range(COLS):
            count = 1
            cur_color_idx = modified_board[i][j][0]
            while (cur_color_idx == modified_board[i + count][j][0]) and (cur_color_idx != 0):
                count += 1
                if (count >= WIN_PEGS):
                    return True
    return False

# Check diagonals for a win
def check_diags():
    global modified_board
    # Top left to bottom right
    for i in range(ROWS - WIN_PEGS + 1):
        for j in range(COLS - WIN_PEGS + 1):
            count = 1
            cur_color_idx = modified_board[i][j][0]
            while (cur_color_idx == modified_board[i + count][j + count][0]) and (cur_color_idx != 0):
                count += 1
                if (count >= WIN_PEGS):
                    return True
    # Top right to bottom left
    for i in range(ROWS - WIN_PEGS + 1):
        for j in range(COLS - 1, WIN_PEGS - 2, -1):
            count = 1
            cur_color_idx = modified_board[i][j][0]
            while (cur_color_idx == modified_board[i + count][j - count][0]) and (cur_color_idx != 0):
                count += 1
                if (count >= WIN_PEGS):
                    return True
    return False

def check_win(player_num):
    global num_teams
    global player_names
    global team_colors
    if (check_rows() or check_cols() or check_diags()):
        display_board()
        print(f"\n{team_colors[player_num % num_teams]}CONGRATULATIONS! {player_names[player_num]} LED THE {VALID_COLORS[COLOR_CODES.index(team_colors[player_num % num_teams])]} TEAM TO VICTORY!")
        return True
    return False

def is_dead(hand):
    global modified_board
    highest_playable = 99
    while (not valid_move(highest_playable)):
        highest_playable -= 1
    return np.any(np.where(hand <= highest_playable))

def check_elim(player_num, hand):
    global num_teams
    global player_names
    global team_colors
    if (is_dead(hand)):
        print(f"\n{team_colors[player_num % num_teams]}BREAKING NEWS! {player_names[player_num]} OF THE {VALID_COLORS[COLOR_CODES.index(team_colors[player_num % num_teams])]} TEAM HAS BEEN ELIMINATED!")
        return True
    return False

# Sequence of actions for a "play"
def play(card, hand, player_num):
    loc = input("\nNow choose where to play it: ")
    while (not loc.isdigit() or not valid_move(int(loc)) or (int(loc) < card)):
        loc = input("\nThat's not a valid location! Please try again: ")
    make_move(int(loc), player_num)
    hand[list(hand).index(card)] = -1
    print("\nCard played successfully. Moving on...")


# Sequence of actions for a "draw"
def draw(hand):
    global start_position
    global all_cards
    new_card = int(all_cards[start_position])
    start_position += 1
    print(f"\nDrawing card... Your new card is: {new_card}")
    hand[list(hand).index(-1)] = new_card
    print("\nCard drawn successfully. Moving on...")

# Full game runs here
def game():
    global num_players
    global num_teams
    global player_names
    global team_colors
    global start_position
    global all_cards
    global cards
    global modified_board
    print(f"{RESET}")
    while True:
        temp_num_players = input("\nEnter the total number of players (4, 6, 8, or 9): ")
        if (temp_num_players.isdigit()) and (int(temp_num_players) in VALID_NUM_PLAYERS):
            num_players = int(temp_num_players)
            break
        else:
            print("\nThat's not a valid total number of players, please try again.")
    while True:
        temp_num_teams = input("\nEnter the number of teams (2 or 3): ")
        if (temp_num_teams.isdigit()) and (int(temp_num_teams) in VALID_NUM_TEAMS) and (num_players % int(temp_num_teams) == 0):
            num_teams = int(temp_num_teams)
            break
        else:
            print("\nThat's not a valid number of players per team, please try again.")
    for i in range(num_players):
        print(f"\nYou are Player {i + 1}. You are on Team {(i % num_teams) + 1}.")
        while True:
            temp_name = input("\nEnter your unique player name: ")
            if temp_name not in player_names:
                player_names.append(temp_name)
                break
            else:
                print("\nThat name has already been taken, please try again.")
    for i in range(num_teams):
        teammates = player_names[i::num_teams]
        print(f"\nThis is Team {i + 1}. Here are the players on this team: ")
        for person in teammates:
            print("\n" + person)
        while True:
            temp_color = input("\nEnter your unique team color (BLUE, CYAN, GREEN, MAGENTA, RED, or YELLOW): ")
            if (temp_color in VALID_COLORS) and (temp_color not in team_colors):
                team_colors.append(COLOR_CODES[VALID_COLORS.index(temp_color)])
                break
            else:
                print("\nThat color is either invalid or has already been taken, please try again.")
    start_position = num_players*CARDS_PER_PLAYER
    setup()
    while (True):
        for i in range(num_players):
            if (still_playing[i] == 1):
                display_board()
                print(f"\n{team_colors[i % num_teams]}{player_names[i]}'s turn.")
                hand = np.sort(cards[i])
                print("\nHere are your cards:")
                print("\n" + " ".join(map(str, hand[np.nonzero(hand >= 0)])))
                if check_elim(i, cards[i]):
                    still_playing[i] = 0
                if check_win(i):
                    return True
                if (-1 not in cards[i]):
                    while True:
                        card = input("\nPick a card to play: ")
                        if (card.isdigit()) and (int(card) in cards[i]):
                            play(int(card), cards[i], i)
                            break
                        else:
                            print("\nThat's not a valid, currently playable card! Please try again.")
                elif (list(cards[i]).count(-1) == 4):
                    draw(cards[i])
                else:
                    while True:
                        option = input("\nYou can either play (type in card value) or draw (type in -1): ")
                        if (option == "-1"):
                            draw(cards[i])
                            break
                        elif (option.isdigit()) and (int(option) in cards[i]):
                            play(int(option), cards[i], i)
                            break
                        else:
                            print("\nThat's not a valid, currently playable card! Please try again.")
        
def main():
    game()
    while True:
        decision = input("\nPlay again? (Yes/No) ")
        if (decision == "Yes"):
            print("\nOkay, re-initializing the game...\n")
            game()
        elif (decision != "No"):
            print("\nThat's not a valid answer! Please try again.")
        else:
            print("\nOkay, exiting the game...")
            break
    return True

main()