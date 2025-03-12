"""
Tic Tac Toe Player
"""

import math
import copy
import random
from operator import itemgetter

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = 0
    o_count = 0
    for row in board:
        for cell in row:
            if cell == X:
                x_count += 1
            elif cell == O:
                o_count += 1

    if x_count == o_count:
        return X

    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    move = []

    for i in range(0, 3):
        for j in range(0, 3):
            if board[i][j] == EMPTY:
                move.append((i, j))

    return move


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    symbol = player(board)
    i = action[0]
    j = action[1]
    if i < 0 or i >= 3 or j < 0 or j >= 3 or board[i][j] != EMPTY:
        raise ValueError("Invalid action")

    temp_board = copy.deepcopy(board)
    temp_board[i][j] = symbol

    return temp_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(0, 3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]

        if board[0][i] is not None and board[0][i] == board[1][i] == board[2][i]:
            return board[0][i]

    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]

    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    empty_count = 0
    for row in board:
        for cell in row:
            if cell == EMPTY:
                empty_count += 1

    return empty_count == 0

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    if win == O:
        return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    move, _ = minimax_helper(board)

    return move

def minimax_helper(board) :
    if terminal(board):
        return (-1, -1), utility(board)

    possible_actions = actions(board)
    choices = []

    for i in range(0, len(possible_actions)):
        _, value = minimax_helper(result(board, possible_actions[i]))
        choices.append((possible_actions[i], value))

    if player(board) == X:
        max_value = -2
        max_index = 0
        for i in range(0, len(choices)):
            if choices[i][1] > max_value:
                max_value = choices[i][1]
                max_index = i

        return choices[max_index][0], max_value

    min_value = 2
    min_index = 0
    for i in range(0, len(choices)):
        if choices[i][1] < min_value:
            min_value = choices[i][1]
            min_index = i

    return choices[min_index][0], min_value
