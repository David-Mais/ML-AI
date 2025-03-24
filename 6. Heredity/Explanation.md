# Introduction

This project models genetic inheritance for a specific gene—the hearing impairment version of GJB2—to explain how mutated versions can lead to a trait such as hearing loss. Using a Bayesian Network, the model represents each person with two random variables: one for their gene (indicating 0, 1, or 2 copies of the mutated gene) and one for the observable trait (yes or no). The network accounts for both direct evidence (an observed trait) and hidden genetic states (the actual number of mutated copies) which are inherited from the parents with possible mutations.

# Overview of the Code

The solution is organized around three key functions:

- **`joint_probability(people, one_gene, two_genes, have_trait)`**  
  Computes the joint probability that every person in the family has a specific gene count (0, 1, or 2 copies) and exhibits (or not) the trait, given the inheritance rules and mutation probabilities. This function factors in both unconditional probabilities (for people with no parents in the dataset) and the conditional probabilities when parental information is available.

- **`update(probabilities, one_gene, two_genes, have_trait, p)`**  
  Updates the running total of probabilities for each person’s gene and trait distributions. For every computed joint probability `p` for a particular configuration, this function adds `p` to the corresponding value in the distributions.

- **`normalize(probabilities)`**  
  Adjusts the probability distributions for each person so that they sum to 1 while keeping the relative proportions the same. This step ensures that the final output is a proper probability distribution.

# Detailed Code Explanation

## 1. Joint Probability Calculation

### Purpose  
The `joint_probability` function calculates the probability that:
- Every person in `one_gene` has exactly one copy of the mutated gene.
- Every person in `two_genes` has exactly two copies.
- Every other person (not in `one_gene` or `two_genes`) has zero copies.
- Additionally, the function factors in whether each person exhibits the trait based on the provided `have_trait` set.

### How It Works  
- **Input:**  
  - `people`: A dictionary where each key is a person’s name and the value is another dictionary with keys `mother`, `father`, and `trait`.
  - `one_gene`, `two_genes`: Sets listing which people have 1 and 2 copies of the gene, respectively. Anyone not in these sets is assumed to have 0 copies.
  - `have_trait`: A set of people who are observed (or assumed) to have the trait.
  
- **Logic:**  
  1. **Iterate Over People:**  
     For each person, determine the gene count based on membership in `one_gene` or `two_genes`. Also, determine if the person exhibits the trait.
  2. **Without Parental Information:**  
     If a person has no parents listed, multiply the joint probability by the unconditional probability from `PROBS["gene"]` and the corresponding trait probability from `PROBS["trait"]`.
  3. **With Parental Information:**  
     - Retrieve each parent’s gene count.
     - Calculate the probability that the mother and father pass the mutated gene to their child. This depends on:
       - For a parent with 0 copies, the chance of passing the gene is the mutation probability.
       - For a parent with 1 copy, there is a 50% chance.
       - For a parent with 2 copies, the chance is 1 minus the mutation probability.
     - Depending on the gene count for the child (0, 1, or 2 copies), compute the probability from the combination of parental contributions.
  4. **Combine Probabilities:**  
     Multiply by the trait probability for the current gene count.
  
- **Example Calculation:**  
  The explanation provided in the assignment shows how the joint probability is computed for a three-person family by multiplying the probability of each person’s gene count and trait (using both unconditional and conditional probability distributions).

```python
def joint_probability(people, one_gene, two_genes, have_trait):
    probability = 1

    for person in people:
        # Determine gene count: 0, 1, or 2
        gene_type = 0
        if person in one_gene:
            gene_type = 1
        elif person in two_genes:
            gene_type = 2

        # Determine trait: True if in have_trait, else False
        trait = person in have_trait

        # Base probabilities when no parental info exists
        gene_probability = PROBS['gene'][gene_type]
        trait_probability = PROBS['trait'][gene_type][trait]

        if people[person]['mother'] is None and people[person]['father'] is None:
            probability *= gene_probability * trait_probability
        else:
            mother = people[person]['mother']
            father = people[person]['father']

            # Determine parent's gene counts
            mother_gene_number = 0
            father_gene_number = 0
            if mother in one_gene:
                mother_gene_number = 1
            elif mother in two_genes:
                mother_gene_number = 2
            if father in one_gene:
                father_gene_number = 1
            elif father in two_genes:
                father_gene_number = 2

            # Calculate the probability each parent passes the gene
            if mother_gene_number == 0:
                mother_pass_probability = PROBS['mutation']
            elif mother_gene_number == 1:
                mother_pass_probability = 0.5
            else:
                mother_pass_probability = 1 - PROBS['mutation']

            if father_gene_number == 0:
                father_pass_probability = PROBS['mutation']
            elif father_gene_number == 1:
                father_pass_probability = 0.5
            else:
                father_pass_probability = 1 - PROBS['mutation']

            # Determine probability of child's gene count based on parental contributions
            if gene_type == 0:
                probability *= (1 - mother_pass_probability) * (1 - father_pass_probability)
            if gene_type == 1:
                probability *= (
                    (1 - mother_pass_probability) * father_pass_probability +
                    (1 - father_pass_probability) * mother_pass_probability
                )
            if gene_type == 2:
                probability *= mother_pass_probability * father_pass_probability

            # Multiply by the trait probability
            probability *= trait_probability

    return probability
```

## 2. Update Function

### Purpose  
The `update` function accumulates the joint probability `p` for a particular configuration of gene counts and traits into a running total stored in the `probabilities` dictionary.

### How It Works  
- **Input:**  
  - `probabilities`: A dictionary mapping each person to two sub-dictionaries: one for `gene` probabilities and one for `trait` probabilities.
  - `one_gene`, `two_genes`, `have_trait`: Sets that define the current configuration.
  - `p`: The joint probability for this configuration.
  
- **Logic:**  
  1. **Iterate Over People:**  
     For each person, update:
     - The appropriate entry in the gene distribution (0, 1, or 2 copies) based on whether they appear in `one_gene` or `two_genes`.
     - The appropriate entry in the trait distribution based on whether the person is in `have_trait`.
  2. **Accumulate Probability:**  
     Add `p` to the corresponding probability for that configuration.

```python
def update(probabilities, one_gene, two_genes, have_trait, p):
    for person in probabilities:
        # Update gene distribution based on gene copy
        if person in one_gene:
            probabilities[person]['gene'][1] += p
        elif person in two_genes:
            probabilities[person]['gene'][2] += p
        else:
            probabilities[person]['gene'][0] += p

        # Update trait distribution
        if person in have_trait:
            probabilities[person]['trait'][True] += p
        else:
            probabilities[person]['trait'][False] += p
```

*Note:* In your provided code, there was a slight mix-up in the keys when updating the distributions; the intent is to add `p` to the appropriate gene count and trait outcome.

## 3. Normalize Function

### Purpose  
The `normalize` function adjusts each probability distribution in the `probabilities` dictionary so that the values sum to 1, preserving the relative proportions.

### How It Works  
- **Input:**  
  - `probabilities`: The dictionary containing unnormalized probability distributions for each person.
  
- **Logic:**  
  1. **Compute Sums:**  
     For each person, sum the probabilities in their gene distribution and trait distribution.
  2. **Divide by Sum:**  
     For every entry in each distribution, divide by the sum so that the overall distribution becomes a valid probability distribution (summing to 1).
  3. **Optional Display:**  
     The helper function `print_dictionary` can be used to visualize the updated probabilities in a tabular format using pandas.

```python
def normalize(probabilities):
    normalized_probabilities = probabilities.copy()

    for person in probabilities:
        gene_sum = sum(probabilities[person]['gene'].values())
        trait_sum = sum(probabilities[person]['trait'].values())

        # Normalize gene distribution
        for gene_type in probabilities[person]['gene']:
            normalized_probabilities[person]['gene'][gene_type] = probabilities[person]['gene'][gene_type] / gene_sum

        # Normalize trait distribution
        for trait_type in probabilities[person]['trait']:
            normalized_probabilities[person]['trait'][trait_type] = probabilities[person]['trait'][trait_type] / trait_sum

    return normalized_probabilities
```

# Conclusion

This implementation of the heredity model uses three main functions:
- **`joint_probability`** to compute the likelihood of a specific combination of gene counts and trait expressions across a family.
- **`update`** to accumulate these probabilities for every configuration.
- **`normalize`** to convert the accumulated values into proper probability distributions.

Together, these functions allow the model to infer hidden genetic information based on observable traits and familial relationships, using the underlying probabilities defined in `PROBS`. This structured explanation should serve as a template for understanding and documenting similar projects in a clear and systematic way.