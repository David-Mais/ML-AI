# Introduction

This section of the code implements the core logic behind the Minesweeper AI. It consists of two main classes: one to represent logical statements about the board (the **Sentence** class) and another to manage the AI's decision-making process (the **MinesweeperAI** class). Together, they enable the AI to update its knowledge base, infer safe moves, and mark mines based on the information gathered from the game.

# Overview of the Code

The implementation is divided into two key parts:

- **Sentence Class**  
  Represents a logical statement about a set of board cells and the number of mines among them. It provides methods to deduce which cells are definitely safe or mines and to update its internal state when new information is acquired.

- **MinesweeperAI Class**  
  Acts as the game player by tracking moves, maintaining sets of known safe cells and mines, and managing a knowledge base comprised of Sentence objects. It uses this knowledge to make safe moves, add new insights based on revealed cells, and infer additional sentences from existing data.

# Detailed Code Explanation

## Sentence Class

### Logical Statement Representation

The **Sentence** class encapsulates a statement about the Minesweeper board. It consists of a set of cells and a count indicating how many of these cells are mines.

#### Key Methods

- **`__init__(self, cells, count)`**  
  Initializes a sentence by converting the provided list of cells into a set and storing the mine count.

- **`__eq__(self, other)`**  
  Defines equality between sentences by comparing both their cells and the mine count.

- **`__str__(self)`**  
  Returns a string representation of the sentence for easy debugging and logging.

- **`known_mines(self)`**  
  If every cell in the sentence must be a mine (i.e., the number of cells equals the count), returns a copy of the cell set; otherwise, returns `None`.

- **`known_safes(self)`**  
  If no cell in the sentence is a mine (i.e., the count is zero), returns a copy of the cell set; otherwise, returns `None`.

- **`mark_mine(self, cell)`**  
  When a cell is confirmed as a mine, this method removes it from the sentence and decrements the count accordingly.

- **`mark_safe(self, cell)`**  
  When a cell is determined to be safe, it is simply removed from the sentence.

```python
class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return copy.deepcopy(self.cells)
        return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return copy.deepcopy(self.cells)
        return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)
```

## MinesweeperAI Class

### AI Decision-Making and Knowledge Update

The **MinesweeperAI** class encapsulates the logic required to make informed moves on the Minesweeper board. It maintains internal records of moves made, cells known to be safe, cells identified as mines, and a knowledge base of sentences that represent pieces of inferred information.

#### Initialization

The constructor initializes board dimensions and sets up empty data structures to track moves, safe cells, mines, and logical sentences.

```python
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []
```

#### Marking Cells

Two helper methods update the AI’s knowledge base when a cell is identified as either a mine or safe:

- **`mark_mine(self, cell)`**  
  Adds the cell to the set of mines and updates every sentence in the knowledge base to reflect that the cell is a mine.

- **`mark_safe(self, cell)`**  
  Adds the cell to the set of safe cells and updates all sentences to remove that cell.

```python
    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
```

### Adding Knowledge

The **add_knowledge** method integrates information from a revealed safe cell into the AI's reasoning process. It follows these five steps:

- **Step 1: Record the Move**  
  The AI records that the cell has been played.

- **Step 2: Mark the Cell as Safe**  
  The cell is marked safe since it has been revealed.

- **Step 3: Create a New Sentence**  
  A new logical statement is generated by examining neighboring cells and adjusting the mine count accordingly.

- **Step 4: Update the Knowledge Base**  
  The AI reviews its current knowledge to mark additional cells as safe or mines based on the new sentence.

- **Step 5: Infer Additional Sentences**  
  New sentences are inferred by comparing existing sentences, expanding the AI’s understanding of the board.

# Detailed Code Explanation

## Step 1: Record the Move

The first step ensures the AI does not consider the same cell again by adding it to the set of moves made.

```python
print(f"Started making move: {cell}")
self.moves_made.add(cell)
print("Stage 1 completed successfully")
```

## Step 2: Mark the Cell as Safe

After recording the move, the cell is explicitly marked as safe. This confirms the board’s information that the cell does not contain a mine.

```python
self.mark_safe(cell)
print("Stage 2 completed successfully")
```

## Step 3: Create a New Sentence

This step examines the neighbors of the revealed cell. The method:
- Iterates through adjacent cells.
- Skips invalid coordinates, the cell itself, or those already known to be safe.
- Adjusts the mine count if a neighbor is already identified as a mine.
- Collects the remaining cells to form a new logical sentence, which is then added to the AI’s knowledge base if not empty.

```python
neighbor_cells = []
x, y = cell
top = x - 1
bottom = x + 1
left = y - 1
right = y + 1

adjusted_count = count
for i in range(top, bottom + 1):
    for j in range(left, right + 1):
        if self.illegal_coordinate(i, j) or (i == x and j == y):
            continue

        if (i, j) in self.safes:
            continue

        if (i, j) in self.mines:
            adjusted_count -= 1
            continue

        neighbor_cells.append((i, j))

if neighbor_cells:
    self.knowledge.append(Sentence(neighbor_cells, adjusted_count))
print("Stage 3 completed successfully")
```

## Step 4: Update the Knowledge Base

Next, the method scans through the existing sentences to mark additional cells as mines or safe:
- If a sentence's cell count equals its mine count, every cell in that sentence is a mine.
- If the count is zero, every cell is safe.
The AI then updates its internal records accordingly.

```python
for sentence in self.knowledge:
    current_cells = copy.deepcopy(sentence.cells)
    if len(sentence.cells) == sentence.count:
        for curr_cell in current_cells:
            self.mark_mine(curr_cell)

    if sentence.count == 0:
        for curr_cell in current_cells:
            self.mark_safe(curr_cell)
print("Stage 4 completed successfully")
```

## Step 5: Infer Additional Sentences

Finally, the method looks for opportunities to infer new sentences by comparing pairs of existing sentences:
- If one sentence's cells are a subset of another’s, the difference can form a new sentence.
- The new sentence's mine count is determined by the difference between the counts.
- If the new sentence is valid and unique, it is added to the knowledge base.

```python
new_sentences = []
for sentence_i in self.knowledge:
    for sentence_j in self.knowledge:
        if sentence_i == sentence_j:
            continue
        if sentence_i.cells.issubset(sentence_j.cells):
            result = sentence_j.cells.difference(sentence_i.cells)
            count_diff = sentence_j.count - sentence_i.count
            if result and count_diff >= 0:
                new_sentence = Sentence(result, count_diff)
                if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                    new_sentences.append(new_sentence)
self.knowledge.extend(new_sentences)
print(self.safes)
print(f"Intersection of safes and mines: {self.safes.intersection(self.mines)}")
print("Stage 5 completed successfully")

self.safes.difference_update(self.mines)
```
#### Helper Methods for Move Selection

The AI includes additional helper methods to facilitate move selection:

- **`illegal_coordinate(self, x, y)`**  
  Checks whether a given coordinate lies outside the boundaries of the board.

- **`make_safe_move(self)`**  
  Iterates through the known safe cells and returns one that has not yet been chosen as a move.

- **`make_random_move(self)`**  
  If no safe move is available, selects a random move from the remaining cells that have neither been chosen nor are known to be mines.

```python
    def illegal_coordinate(self, x, y):
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return True
        return False

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        """
        for move in self.safes:
            if move not in self.moves_made:
                print(move)
                return move
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(0, self.height):
            for j in range(0, self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return i, j
        return None
```

# Conclusion

This segment of the Minesweeper AI demonstrates a modular approach to logical inference and decision-making. The **Sentence** class encapsulates logical statements that allow the AI to deduce which cells are safe or contain mines, while the **MinesweeperAI** class leverages this knowledge to update its internal state, select safe moves, and infer new information from the existing knowledge base. This structured methodology forms the backbone of the AI's strategy for effectively navigating the Minesweeper game board.