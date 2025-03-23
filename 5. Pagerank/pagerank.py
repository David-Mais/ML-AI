import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 1000000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    
  
    
    
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print("PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


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

    for _ in range(n):
        probability_dictionary = transition_model(corpus, current_page, damping_factor)

        page_list = []
        page_weights = []
        for page, probability in probability_dictionary.items():
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

if __name__ == "__main__":
    main()
