# Introduction

This program is a small natural‑language **parser** written in Python with `nltk`.  It defines a context‑free grammar (CFG) for a subset of English, uses an `nltk.ChartParser` to build syntax trees for sentences, and then extracts *noun‑phrase chunks* from those trees.  Two helper functions – `preprocess` and `np_chunk` – implement the text preprocessing and chunk extraction logic.

# Overview of the Code

- **Grammar definition**  
  *`TERMINALS`* lists all lexical items grouped by part of speech, while *`NONTERMINALS`* contains the rewrite rules that describe the sentence structure.
- **`preprocess` function**  
  Tokenises the raw sentence, lower‑cases each token, and removes anything that lacks an alphabetic character.
- **`np_chunk` function**  
  Walks an `nltk.Tree`, returning every *minimal* noun‑phrase (NP) subtree.
- **`main` routine**  
  Handles I/O, invokes the parser on the cleaned tokens, pretty‑prints each parse tree, and shows its NP chunks.

# Detailed Code Explanation

## Grammar Definition

### TERMINALS and NONTERMINALS
The grammar is declared as two multiline strings, concatenated to build an `nltk.CFG`.  `TERMINALS` maps each lexical category to concrete words.  `NONTERMINALS` introduces the structural rules needed to parse every sentence in the *sentences/* directory, including coordination and nested complements.

```python
TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> PART | PART Conj PART
PART -> NP VP | NP Adv VP | VP
NP -> N | NA N
NA -> Det | Adj | NA NA
VP -> V | V SUPP
SUPP -> NP | P | Adv | SUPP SUPP | SUPP SUPP SUPP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)
```
*Key ideas*
1. **Sentence (`S`)** can be a single clause `PART` or two clauses joined by a conjunction.
2. **Noun phrases (`NP`)** are either a bare noun or a noun preceded by a chain of determiners/adjectives (`NA`).  `NA` is left‑recursive to allow unlimited stacks such as *"the little red"*.
3. **Verb phrases (`VP`)** may stand alone or take one or more complements/adjuncts via the helper symbol `SUPP`, which is recursive and thus captures chains like *"sat in the armchair"* or *"had never smiled"*.

## `preprocess` Function

### Purpose
Prepare raw user input for the parser by ensuring the token list matches the lowercase lexical entries and excludes punctuation or numbers.

#### Key Steps
- **Tokenise** with `nltk.tokenize.word_tokenize`.
- **Normalize case** by calling `lower()` on every token.
- **Filter** out tokens that contain no alphabetic character.

```python
def preprocess(sentence):
    """Return a cleaned list of lowercase word tokens."""
    word_list = []
    tokenized = nltk.tokenize.word_tokenize(sentence)

    for word in tokenized:
        word = word.lower()
        if any(char.isalpha() for char in word):
            word_list.append(word)

    return word_list
```

## `np_chunk` Function

### Purpose
Extract *minimal* noun‑phrase subtrees (NPs that do **not** themselves contain smaller NPs) from a full parse tree.

#### Algorithm
1. Iterate over every subtree of the input `tree`.
2. Collect those whose label is `"NP"`.
3. Because the grammar never embeds one `NP` inside another without an intervening non‑NP node (by design), every collected subtree is minimal.

```python
def np_chunk(tree):
    """Return a list of minimal NP subtrees from *tree*."""
    chunks = []
    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            chunks.append(subtree)
    return chunks
```

## `main` Routine

### Flow of Control
1. **Input acquisition:** Read a sentence either from a file supplied on the command line or via standard input.
2. **Pre‑processing:** Pass the string through `preprocess` to obtain a clean token list.
3. **Parsing:** Use the global `parser` to generate one or more parse trees.  Handle failures.
4. **Output:** For each tree, pretty‑print it and list the NP chunks returned by `np_chunk`.

```python
if __name__ == "__main__":
    main()
```

# Conclusion

The script combines a handcrafted CFG with simple token‑level cleaning to parse Sherlock‑Holmes‑style sentences and surface every elementary noun phrase they contain.  Its modular organisation – grammar specification, preprocessing, chunk extraction, and orchestrating **main** – makes it easy to extend the lexical coverage or refine the phrase‑structure rules without touching the surrounding logic.

