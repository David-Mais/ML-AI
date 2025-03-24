# Introduction

This project implements the PageRank algorithm, which estimates the importance of web 
pages based on the links between them. The idea is inspired by the random surfer model, 
where a hypothetical user clicks on links at random. The algorithm assigns higher rank to 
pages that are more likely to be visited, either because many pages link to them or because 
they are linked from pages that themselves are important. Two methods are implemented here: 
one that estimates PageRank via sampling from a Markov chain (the random surfer) and another 
that iteratively applies a mathematical formula until convergence.

# Overview of the Code

The solution is organized into three main functions along with a helper:
- **`transition_model(corpus, page, damping_factor)`**  
  Generates a probability distribution over the next page a surfer might visit given the current page. It factors in the damping factor so that, with probability _d_, the surfer follows one of the links on the current page, and with probability _1 - d_, the surfer jumps to any page at random.

- **`sample_pagerank(corpus, damping_factor, n)`**  
  Estimates the PageRank of each page by simulating the random surfer. Starting from a randomly chosen page, it uses the transition model to sample _n_ pages and then computes the proportion of visits for each page.

- **`iterate_pagerank(corpus, damping_factor)`**  
  Computes PageRank values using an iterative approach based on the PageRank formula. Each page’s rank is repeatedly updated using the contributions from pages linking to it until the values converge within a specified threshold.

- **`calculate_second_part(damping_factor, page, corpus, probability_dictionary)`**  
  A helper function used by `iterate_pagerank` to compute the contribution from pages that link to a given page. This implements the summation part of the PageRank formula: for every page that links to the target, it adds that page’s rank divided by its number of outgoing links (treating pages with no links as linking to every page).

# Detailed Code Explanation

## 1. Transition Model

### Purpose  
The `transition_model` function computes a probability distribution that represents the chance of moving to any page in the corpus from a given current page.

### How It Works  
- **Input:**  
  - `corpus`: A dictionary mapping each page name to a set of pages it links to.  
  - `page`: The current page of the random surfer.  
  - `damping_factor`: The probability with which the surfer follows one of the links on the current page.
  
- **Logic:**  
  1. **Handling No Outgoing Links:**  
     If the current page has no outgoing links, the function returns a uniform distribution over all pages.
  2. **Distributing Probabilities:**  
     - With probability `damping_factor`, the surfer chooses one of the pages linked from the current page uniformly at random.
     - With probability `1 - damping_factor`, the surfer jumps to any page in the corpus uniformly.
  3. **Combining the Two Parts:**  
     The probabilities from both parts are summed for each page to create the final distribution.  
     
- **Example:**  
  For a corpus such as `{"1.html": {"2.html", "3.html"}, "2.html": {"3.html"}, "3.html": {"2.html"}}` and current page `"1.html"`, the function would assign a portion of the probability to the linked pages (`"2.html"` and `"3.html"`) based on the damping factor, plus an equal share to every page for the random jump.

```python
def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.
    
    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    probability_dictionary = dict()
    
    all_files_in_corpus = set()
    for p_set in corpus.values():
        all_files_in_corpus.update(p_set)
    
    page_links = corpus[page]
    if len(page_links) == 0:
        even_probability = 1.0 / len(all_files_in_corpus)
        for i_page in all_files_in_corpus:
            probability_dictionary[i_page] = even_probability
        return probability_dictionary
    
    each_link_probability = damping_factor / len(page_links)
    for link in page_links:
        probability_dictionary[link] = each_link_probability
    
    any_page_probability = (1 - damping_factor) / len(all_files_in_corpus)
    for p in all_files_in_corpus:
        if p not in probability_dictionary:
            probability_dictionary[p] = any_page_probability
        else:
            probability_dictionary[p] = probability_dictionary[p] + any_page_probability
    
    return probability_dictionary
```

## 2. Sampling PageRank

### Purpose  
The `sample_pagerank` function estimates each page’s PageRank by simulating the random surfer process over a large number of samples.

### How It Works  
- **Input:**  
  - `corpus`: The mapping of pages to the pages they link to.
  - `damping_factor`: The probability used in the transition model.
  - `n`: The number of samples (iterations) to simulate.
  
- **Logic:**  
  1. **Initialization:**  
     The simulation starts with a randomly chosen page from the corpus.
  2. **Sampling Process:**  
     For each of the _n_ samples, the function:
     - Uses the `transition_model` to obtain a probability distribution for the next page.
     - Chooses the next page based on the weighted probabilities.
     - Records the visit by updating a counter.
  3. **Normalization:**  
     After all samples, the counts for each page are divided by the total number of samples so that the final values represent probabilities (summing to 1).

```python
def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.
    
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    probability_dictionary = dict()
    all_files_in_corpus = set()
    for p_set in corpus.values():
        all_files_in_corpus.update(p_set)

    current_page = random.choice(list(all_files_in_corpus))
    probability_dictionary[current_page] = 1

    for _ in range(1, n):
        probability_dictionary_transition = transition_model(corpus, current_page, damping_factor)

        page_list = []
        page_weights = []
        for page, probability in probability_dictionary_transition.items():
            page_list.append(page)
            page_weights.append(probability)

        current_page = random.choices(page_list, weights=page_weights, k=1)[0]
        if current_page not in probability_dictionary:
            probability_dictionary[current_page] = 1
        else:
            probability_dictionary[current_page] += 1

    value_sum = 0
    for page, probability in probability_dictionary.items():
        value_sum += probability

    for key in probability_dictionary:
        probability_dictionary[key] = probability_dictionary[key] / value_sum

    probability_sum = 0
    for page, probability in probability_dictionary.items():
        probability_sum += probability

    print(f"Sum of probabilities: {probability_sum}")
    return probability_dictionary
```

*Note:* The function repeatedly updates the current page based on the transition model and counts visits. Finally, it normalizes the counts so that they represent probabilities summing to 1.

## 3. Iterative PageRank Calculation

### Purpose  
The `iterate_pagerank` function computes PageRank values using an iterative formula until the values converge to within a threshold (0.001). This method uses the recursive definition of PageRank where each page’s rank is updated based on the ranks of the pages linking to it.

### How It Works  
- **Input:**  
  - `corpus`: The dictionary of pages and their links.
  - `damping_factor`: The damping factor used to weight the contributions from linking pages.
  
- **Logic:**  
  1. **Initialization:**  
     Each page is assigned an initial PageRank of `1 / N`, where _N_ is the total number of pages.
  2. **Iterative Update:**  
     For every page, the new rank is computed as the sum of two components:
     - A base probability: `(1 - damping_factor) / N`.
     - The weighted contributions from all pages that link to it. This contribution is computed by the helper function `calculate_second_part`.
  3. **Convergence Check:**  
     The process repeats until the change in PageRank for every page is less than 0.001.
  4. **Normalization:**  
     After convergence, the PageRank values are normalized so that they sum to 1.

```python
def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.
    
    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    old_probability_dictionary = dict()
    new_probability_dictionary = dict()
    all_files_in_corpus = set()
    for p, p_set in corpus.items():
        all_files_in_corpus.update(p_set)
        all_files_in_corpus.add(p)

    for file in all_files_in_corpus:
        new_probability_dictionary[file] = 1.0 / len(all_files_in_corpus)
        old_probability_dictionary[file] = 0.0

    one_minus_d_over_n = (1.0 - damping_factor) / len(all_files_in_corpus)
    while True:
        for j in all_files_in_corpus:
            new_probability_dictionary[j] = one_minus_d_over_n + calculate_second_part(damping_factor, j, corpus, old_probability_dictionary)

        no_change = True
        for file in all_files_in_corpus:
            if abs(new_probability_dictionary[file] - old_probability_dictionary[file]) > 0.001:
                no_change = False
                break

        if no_change:
            probability_sum = 0
            for _, probability in new_probability_dictionary.items():
                probability_sum += probability

            for k in all_files_in_corpus:
                new_probability_dictionary[k] = new_probability_dictionary[k] * (1.0 / probability_sum)

            print(f"Sum of probabilities: {probability_sum * (1.0 / probability_sum)}")
            return new_probability_dictionary

        for i in all_files_in_corpus:
            old_probability_dictionary[i] = new_probability_dictionary[i]
```

## 4. Helper Function: `calculate_second_part`

### Purpose  
This helper function computes the summation term in the iterative PageRank formula. For a given page, it sums the contributions from every other page that links to it.

### How It Works  
- **Input:**  
  - `damping_factor`: The damping factor used in the PageRank calculation.
  - `page`: The target page whose new rank is being calculated.
  - `corpus`: The dictionary of pages and their links.
  - `probability_dictionary`: The current PageRank values for all pages.
  
- **Logic:**  
  1. **Prepare Corpus:**  
     It first ensures that every page (even those with no outgoing links) is treated as if it links to all pages.
  2. **Contribution Calculation:**  
     For every page that links to the target page, the function adds that page’s current rank divided by the number of links it has.
  3. **Scaling:**  
     The sum is then multiplied by the damping factor before being returned.

```python
def calculate_second_part(damping_factor, page, corpus, probability_dictionary):
    all_pages = set()
    for key in corpus:
        all_pages.update(corpus[key])
        all_pages.add(key)

    for i in all_pages:
        if i not in corpus:
            corpus[i] = all_pages
        elif len(corpus[i]) == 0:
            corpus[i] = all_pages

    i_linked_to_page = []
    for key in corpus:
        if page in corpus[key]:
            i_linked_to_page.append(key)

    i_sum = 0
    for i_page in i_linked_to_page:
        i_page_probability = probability_dictionary[i_page]
        i_num_links = len(corpus[i_page])
        i_sum += i_page_probability / i_num_links

    return i_sum * damping_factor
```

# Conclusion

This implementation of PageRank provides two distinct methods for estimating page importance:
- **Sampling-based:** Simulating a random surfer using the transition model to build empirical probabilities.
- **Iterative-based:** Applying the recursive PageRank formula until the values converge.

Each function plays a crucial role in modeling the behavior of a random web surfer and ensuring that even pages with no outgoing links are properly handled. By combining these methods, the algorithm yields robust estimates of page importance, closely reflecting the underlying principles of the PageRank algorithm.

This explanation should serve as a template for documenting similar projects and clarifying the logic behind each section of your code.