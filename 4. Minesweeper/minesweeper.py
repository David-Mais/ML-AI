import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


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

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # 1) mark the cell as a move that has been made
        print(f"Started making move: {cell}")
        self.moves_made.add(cell)
        print("Stage 1 completed successfully")

        # 2) mark the cell as safe
        self.mark_safe(cell)
        print("Stage 2 completed successfully")


        # 3) add a new sentence to the AI's knowledge base based on the value of `cell` and `count`
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

        # 4) mark any additional cells as safe or as mines if it can be concluded based on the AI's knowledge base
        for sentence in self.knowledge:
            current_cells = copy.deepcopy(sentence.cells)
            if len(sentence.cells) == sentence.count:
                for curr_cell in current_cells:
                    self.mark_mine(curr_cell)

            if sentence.count == 0:
                for curr_cell in current_cells:
                    self.mark_safe(curr_cell)
        print("Stage 4 completed successfully")

        # 5) add any new sentences to the AI's knowledge base if they can be inferred from existing knowledge
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


    def illegal_coordinate(self, x, y):
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return True
        return False

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
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