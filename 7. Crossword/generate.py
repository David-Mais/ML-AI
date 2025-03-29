import sys

from pandas.util.version import Infinity

from crossword import *
import math


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # print(f"Domains: {self.domains}")

        for domain in self.domains:
            word_size = domain.length
            words_to_remove = []
            for word in self.domains[domain]:
                if len(word) != word_size:
                    words_to_remove.append(word)

            for word in words_to_remove:
                self.domains[domain].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        overlaps_xy = self.crossword.overlaps[x, y]
        if overlaps_xy is None:
            return revised

        elements_to_remove_from_x_domain = set()
        mismatches = 0
        for x_element in self.domains[x]:
            for y_element in self.domains[y]:
                if x_element[overlaps_xy[0]] != y_element[overlaps_xy[1]]:
                    mismatches += 1
            if mismatches == len(self.domains[y]):
                elements_to_remove_from_x_domain.add(x_element)
            mismatches = 0


        for x_element in elements_to_remove_from_x_domain:
            self.domains[x].remove(x_element)

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            arcs = []
            for x in self.crossword.variables:
                for n in self.crossword.neighbors(x):
                    if (x, n) not in arcs:
                        arcs.append((x, n))

        queue = list(arcs)

        while len(queue) > 0:
            x, y = queue.pop(0)
            print(len(queue))

            revise_happened = self.revise(x, y)
            if revise_happened:
                if len(self.domains[x]) == 0:
                    return False

                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        return True


    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.crossword.variables:
            if variable not in assignment:
                return False

        return True


    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        all_words = set()
        for word in assignment.values():
            if word in all_words:
                return False
            all_words.add(word)

        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        for x in assignment:
            for y in assignment:
                if x == y:
                    continue

                overlaps = self.crossword.overlaps[x, y]
                if overlaps is not None:
                    if assignment[x][overlaps[0]] != assignment[y][overlaps[1]]:
                        return False

        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        domain_values = self.domains[var]

        for word in assignment.values():
            if word in domain_values:
                domain_values.remove(word)

        neighbour_values = []
        for neighbor in self.crossword.neighbors(var):
            if neighbor not in assignment:
                neighbour_values.append(neighbor)


        word_elimination = dict()
        for word in domain_values:
            word_elimination[word] = 0

            for neighbor in neighbour_values:
                overlaps = self.crossword.overlaps[var, neighbor]
                for neighbor_word in self.domains[neighbor]:
                    if word[overlaps[0]] != neighbor_word[overlaps[1]]:
                        word_elimination[word] += 1

        sorted_words = sorted(word_elimination, key=word_elimination.get)

        print(sorted_words)
        return sorted_words



    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        available_variables = set()
        for variable in self.crossword.variables:
            if variable not in assignment:
                available_variables.add(variable)


        min_amount = math.inf
        for var, dom in self.domains.items():
            if var not in available_variables:
                continue

            if len(dom) < min_amount:
                min_amount = len(dom)

        min_amount_variables = set()
        for var, dom in self.domains.items():
            if var not in available_variables:
                continue

            if len(dom) == min_amount:
                min_amount_variables.add(var)

        if len(min_amount_variables) == 1:
            return min_amount_variables.pop()

        neighbor_dict = dict()
        for var in min_amount_variables:
            neighbor_dict[var] = self.crossword.neighbors(var)

        return max(neighbor_dict, key=neighbor_dict.get)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        unassigned_variable = self.select_unassigned_variable(assignment)

        for word in self.order_domain_values(unassigned_variable, assignment):
            new_assignment = assignment.copy()

            new_assignment[unassigned_variable] = word

            is_consistent = self.consistent(new_assignment)
            if is_consistent:
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
