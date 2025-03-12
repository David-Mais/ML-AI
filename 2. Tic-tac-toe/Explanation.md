# Introduction

The purpose of this exercise was to build an intellectual method that could decide the best tic-tac-toe move every single time. This was achieved by envisioning each state of the board as a node in a tree and assigning a corresponding value, allowing the bot to choose the optimal move.

# Overview of the Code

We started with an empty `tictactoe.py` file and developed several methods to determine the best move at each step of the game. The key methods implemented were:

- **`player(board)`**  
  Determines whose turn it is, returning either `X` or `O`.

- **`result(board, action)`**  
  Computes and returns the new board state after applying the given action.

- **`winner(board)`**  
  Checks the board and identifies the winner, if any.

- **`terminal(board)`**  
  Determines if the game has reached a terminal state (i.e., no more moves are possible) and returns `true` if the game is over, otherwise `false`.

- **`utility(board)`**  
  Converts the winner information into a numerical value for evaluation.

- **`minimax(board)`** and **`minimax_helper(board)`**  
  These functions work together to calculate the best move available in the current board state.

  
# Detailed Code Explanation

## Input / Output

The main method, for which all other methods serve as helpers, is:

```python
def minimax(board):
```

This function receives a board configuration represented as a 3x3 two-dimensional list. Its 
output is the best move for the current player, expressed as a tuple `(row, column)`.

## Core Logic

### Initial Setup

Initially, we define the symbols for the players and an empty cell. We also create a function 
that returns the initial configuration of the board with all cells empty.

```python
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
```

### Determining the Next Player

The next method calculates which player should make the next move. The logic is based on counting 
the number of `X` and `O` symbols on the board. If both counts are equal, it is `X`'s turn; 
otherwise, if there are more `X`s than `O`s, it is `O`'s turn.

```python
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
```

### Generating Possible Actions

The `actions(board)` method returns a set of all possible actions in the form of tuples 
`(row, column)`. It scans the board and collects the indices of cells that are still empty.

```python
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
```

### Calculating the Resulting Board State

This method computes the board state after the current player makes a specific `action` on the 
provided `board`. It first verifies if the action is valid by checking whether the indices are 
within bounds and whether the selected cell is empty. If the action is invalid, a `ValueError` 
is raised.

```python
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
```

### Determining the Winner

The next method checks each row and column to see if they consist of the same non-empty symbol, 
which would indicate a win. It also checks the two diagonals (main and secondary) for a winner. 
If no winner is found, it returns `None`.

```python
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
```

### Checking for Terminal States

This method determines if the game has reached a terminal state. A board is considered terminal 
if there is a winner or if all cells are filled.

```python
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
```

### Utility Function

Lastly, this utility function assigns a numerical value to the outcome of the game. It returns 
`1` if `X` wins, `-1` if `O` wins, and `0` for a draw. This is particularly useful when evaluating 
moves in the minimax algorithm.

```python
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
```

### Calculating the Best Move with Minimax

Finally, we arrive at the most important part: the actual calculation of the best move using 
a recursive function. Let's walk through the helper function step by step.

#### Base Case

We begin by defining the helper method and checking for the base case. If the board is in a 
terminal state, there is no move to make. Therefore, we return `(-1, -1)` as a placeholder for 
the move, along with `utility(board)`, which provides the numerical value used in the minimax tree.

```python
def minimax_helper(board):
    if terminal(board):
        return (-1, -1), utility(board)
```

#### Initializing Variables

If the board is not terminal, we initialize two variables:
- `possible_actions`: all actions available from the current board state.
- `choices`: a list where we will store tuples of the form `(move, value)`, representing each 
    possible move and its corresponding evaluated value.

```python
    possible_actions = actions(board)
    choices = []
```

#### Evaluating Possible Moves

Next, we iterate over each action in `possible_actions`. For each move, we calculate the 
resulting board by calling `result(board, action)` and then recursively evaluate that board 
using `minimax_helper()`. The resulting value is stored together with the move in the 
`choices` list.

```python
    for i in range(0, len(possible_actions)):
        _, value = minimax_helper(result(board, possible_actions[i]))
        choices.append((possible_actions[i], value))
```

#### Selecting the Best Move

Now, the decision process depends on which player's turn it is.

- **If it's X's turn:**  
  We search for the move with the maximum value. We initialize `max_value` with a very low number 
(e.g., -2) and update it as we find better moves. Once the best move is found, we return it along 
with its value.

  ```python
    if player(board) == X:
        max_value = -2
        max_index = 0
        for i in range(0, len(choices)):
            if choices[i][1] > max_value:
                max_value = choices[i][1]
                max_index = i

        return choices[max_index][0], max_value
  ```

- **If it's O's turn:**  
  Similarly, we search for the move with the minimum value. We initialize `min_value` with a 
  high number (e.g., 2) and update it as we find lower values. The best move for O is then returned 
  with its corresponding value.

  ```python
    min_value = 2
    min_index = 0
    for i in range(0, len(choices)):
        if choices[i][1] < min_value:
            min_value = choices[i][1]
            min_index = i

    return choices[min_index][0], min_value
  ```


### Final Method: `minimax`

This is the method that is actually called in the `runner.py` file. It simply returns the 
optimal move from the `minimax_helper` method, ignoring the evaluated value. This is because 
the caller is only interested in the best move, not its numerical evaluation.

```python
def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    move, _ = minimax_helper(board)

    return move
```

### Conclusion

This implementation effectively demonstrates how the minimax algorithm can be applied 
to determine the optimal move in tic-tac-toe. By breaking down the game into manageable 
components—from initial state creation to move evaluation and final decision-making—the code 
provides a clear and robust framework for building intelligent game-playing agents.
