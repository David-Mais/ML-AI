# Introduction

This document explains the core logic behind a constraint satisfaction algorithm for solving crossword puzzles. The code implements key functions that enforce local consistency (node and arc consistency), assess assignments, and execute a backtracking search with intelligent heuristics. Together, these functions ensure that only valid word assignments are considered, making the search for a complete crossword solution both efficient and robust.

# Overview of the Code

The implementation is organized into several functions, each with a specific role:

- **Enforcing Node Consistency**  
  The `enforce_node_consistency` method prunes each variable’s domain by removing words that do not match the required length.

- **Revising Arcs for Consistency**  
  The `revise` method ensures that for any two variables that overlap, each word in the first variable’s domain has at least one corresponding word in the second variable’s domain that is compatible at the overlapping position.

- **Enforcing Arc Consistency (AC-3 Algorithm)**  
  The `ac3` method applies the arc consistency algorithm over all arcs (or a provided set), propagating constraints through the network of variables.

- **Assignment Completion and Consistency Checks**  
  The `assignment_complete` and `consistent` methods verify that a given assignment is complete (all variables assigned) and consistent (all constraints satisfied).

- **Ordering Domain Values**  
  The `order_domain_values` method orders possible words for a variable based on the “Least Constraining Value” heuristic to reduce the impact on neighboring domains.

- **Selecting an Unassigned Variable**  
  The `select_unassigned_variable` method uses the Minimum Remaining Values (MRV) heuristic combined with the Degree heuristic to choose the next variable for assignment.

- **Backtracking Search**  
  The `backtrack` method recursively searches for a complete and consistent assignment by trying domain values in order and backtracking when necessary.

# Detailed Code Explanation

## 1. Enforcing Node Consistency

**Method:** `enforce_node_consistency`

**Purpose:**  
This function updates each variable's domain so that it only contains words that satisfy the unary constraint—namely, that the word length matches the variable's defined length.

**Key Steps:**

- **Iterate Through Domains:**  
  Loop through every variable in `self.domains`.

- **Determine Expected Length:**  
  Retrieve the `length` attribute of the variable to know the required word size.

- **Identify and Remove Inconsistent Words:**  
  For each word in the variable's domain, check if the word’s length matches the expected length. Inconsistent words are collected and subsequently removed.

**Code Snippet:**

```python
def enforce_node_consistency(self):
    """
    Update `self.domains` such that each variable is node-consistent.
    (Remove any values that are inconsistent with a variable's unary
     constraints; in this case, the length of the word.)
    """
    for domain in self.domains:
        word_size = domain.length
        words_to_remove = []
        for word in self.domains[domain]:
            if len(word) != word_size:
                words_to_remove.append(word)
        for word in words_to_remove:
            self.domains[domain].remove(word)
```

**Details:**  
By removing all words that do not match the variable's length, this step reduces the search space for later steps. It ensures that the domain for each variable only contains potential candidates that are immediately feasible.

---

## 2. Revising Arcs for Consistency

**Method:** `revise`

**Purpose:**  
The `revise` method checks whether variable `x` is arc consistent with variable `y`. This means for each word in `x`’s domain, there must exist at least one word in `y`’s domain that shares a matching character at the overlapping position.

**Key Steps:**

- **Retrieve Overlap Information:**  
  Use the crossword’s `overlaps` data to determine the indices where `x` and `y` must agree. If no overlap exists, no revision is needed.

- **Examine Each Word:**  
  For each candidate word in `x`’s domain, iterate through all words in `y`’s domain.  
  - Count mismatches for the overlapping position.
  - If every word in `y` fails to match at the specified index, mark the word from `x` for removal.

- **Update the Domain:**  
  Remove all marked words from `x`’s domain and return whether any revision occurred.

**Code Snippet:**

```python
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
```

**Details:**  
This method is critical for enforcing binary constraints. By removing incompatible words, it helps maintain a consistent state between variables, which is essential for the AC-3 algorithm to work effectively.

---

## 3. Enforcing Arc Consistency (AC-3 Algorithm)

**Method:** `ac3`

**Purpose:**  
This function applies the AC-3 algorithm to enforce arc consistency across all variables. It systematically revises arcs until every variable’s domain is consistent with its neighbors.

**Key Steps:**

- **Initialize the Queue:**  
  If no specific arcs are provided, generate a list of all arcs by pairing each variable with its neighbors.

- **Process the Queue:**  
  Dequeue an arc and use the `revise` method to update the domain.  
  - If a revision is made and `x`’s domain becomes empty, return `False` (failure).
  - Otherwise, for every neighbor (except the one just checked), add the arc back into the queue for further processing.

- **Return Success:**  
  If the process completes without emptying any domains, return `True`.

**Code Snippet:**

```python
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
```

**Details:**  
The AC-3 algorithm iteratively propagates constraints across the network, ensuring that all variables remain consistent with each other. This reduces the domains further, making subsequent search steps more efficient.

---

## 4. Checking Assignment Completeness

**Method:** `assignment_complete`

**Purpose:**  
Determine whether the current assignment assigns a word to every crossword variable.

**Key Steps:**

- **Iterate Through Variables:**  
  Check if every variable in the crossword has an entry in the assignment dictionary.
- **Return Result:**  
  If any variable is missing, return `False`; otherwise, return `True`.

**Code Snippet:**

```python
def assignment_complete(self, assignment):
    """
    Return True if `assignment` is complete (i.e., assigns a value to each
    crossword variable); return False otherwise.
    """
    for variable in self.crossword.variables:
        if variable not in assignment:
            return False
    return True
```

**Details:**  
This check serves as the base case for the backtracking search, ensuring that only complete assignments are considered solutions.

---

## 5. Ensuring Assignment Consistency

**Method:** `consistent`

**Purpose:**  
Verify that the current assignment does not violate any crossword constraints such as word uniqueness, correct word length, and overlapping character consistency.

**Key Steps:**

- **Uniqueness Check:**  
  Ensure that no word is assigned to more than one variable.
- **Length Check:**  
  Confirm that each assigned word matches the variable's required length.
- **Overlap Check:**  
  For every pair of assigned variables with an overlap, verify that the letters in the overlapping positions match.

**Code Snippet:**

```python
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
```

**Details:**  
This method integrates all constraints—unary (length), binary (overlap), and global (uniqueness)—to ensure that the current assignment is valid before proceeding further in the search.

---

## 6. Ordering Domain Values

**Method:** `order_domain_values`

**Purpose:**  
Return a list of words in the domain of a given variable, sorted by how many choices they would eliminate from neighboring variables. This is an application of the “Least Constraining Value” heuristic.

**Key Steps:**

- **Prune Assigned Values:**  
  Remove words that have already been assigned in the current assignment.
- **Identify Unassigned Neighbors:**  
  Gather all neighboring variables that have not yet been assigned.
- **Calculate Elimination Score:**  
  For each remaining word, calculate how many values in the neighbors' domains it would rule out based on overlap constraints.
- **Sort and Return:**  
  Sort the words in ascending order of their elimination score and return the sorted list.

**Code Snippet:**

```python
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
```

**Details:**  
Ordering domain values by the number of eliminations helps in selecting words that preserve the maximum flexibility for future assignments, thereby increasing the likelihood of success during backtracking.

---

## 7. Selecting an Unassigned Variable

**Method:** `select_unassigned_variable`

**Purpose:**  
Select the next variable to assign by using a combination of the Minimum Remaining Values (MRV) heuristic and the Degree heuristic. This reduces the search space by focusing on the most constrained variables.

**Key Steps:**

- **Identify Unassigned Variables:**  
  Create a set of variables that have not yet been assigned.
- **Apply MRV Heuristic:**  
  Determine the variable(s) with the smallest domain size.
- **Tie-Break with Degree Heuristic:**  
  If multiple variables have the same minimum domain size, choose the one with the highest number of neighbors.
- **Return the Selected Variable:**  
  Return the variable that best meets the criteria.

**Code Snippet:**

```python
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
```

**Details:**  
By selecting the most constrained variable first, the algorithm minimizes the number of possible conflicts and reduces the overall complexity of the search.

---

## 8. Backtracking Search

**Method:** `backtrack`

**Purpose:**  
Implement a recursive backtracking algorithm that searches for a complete and consistent assignment of words to crossword variables.

**Key Steps:**

- **Base Case – Check for Completion:**  
  If the current assignment is complete (all variables are assigned), return the assignment as the solution.

- **Select Next Variable:**  
  Use the `select_unassigned_variable` method to pick the next variable to assign.

- **Iterate Through Domain Values:**  
  Order the domain values using `order_domain_values` and try each word in turn:
  - Create a new assignment by copying the current one and adding the new variable–word pair.
  - Check for consistency using the `consistent` method.
  - If consistent, recursively call `backtrack` with the new assignment.
  - If the recursive call returns a solution, propagate it upward immediately.

- **Failure to Find a Solution:**  
  If no word leads to a valid complete assignment, return `None` to backtrack.

**Code Snippet:**

```python
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
```

**Details:**  
Backtracking is the driver of the constraint solver. By combining variable selection, domain ordering, and consistency checks, the algorithm efficiently navigates the search space and finds a solution if one exists.

---

# Conclusion

This document outlines a comprehensive explanation of the crossword constraint satisfaction algorithm. By enforcing node and arc consistency, checking for assignment completeness and consistency, ordering domain values with a least-constraining heuristic, and selecting variables strategically, the algorithm effectively reduces the search space. The backtracking search ties all these components together, ensuring that the final solution satisfies all crossword constraints. This structured approach not only improves performance but also makes the underlying logic clear and maintainable.