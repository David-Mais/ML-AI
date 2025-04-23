# Introduction

This segment of **mask.py** implements the three functions you were asked to write in the “Attention” exercise.  
Collectively they locate the `[MASK]` token, convert raw attention scores to grayscale colours, and create a full suite of attention–head diagrams for every layer in BERT-base.

# Overview of the Code

- **`get_mask_token_index`**  
  Scans the tokenised input sequence and returns the position of the `[MASK]` token (or `None` if absent).

- **`get_color_for_attention_score`**  
  Linearly maps an attention weight in `[0, 1]` to an RGB triple along the black→white axis.

- **`visualize_attentions`**  
  Iterates through all 12 layers × 12 heads of BERT, passes the relevant slice of the attention tensor to `generate_diagram`, and injects 1-indexed layer/head numbers into the filename.

# Detailed Code Explanation

## `get_mask_token_index`

### Purpose

Identify **where** in `inputs.input_ids` the mask token appears so the model’s logits can be sliced correctly.

### Logic

1. Loop once over the flattened ID list (`inputs.input_ids[0]`).  
2. Compare each ID to `mask_token_id`.  
3. Return the first matching index; fall back to `None` if no match.

```python
def get_mask_token_index(mask_token_id, inputs):
    for i, token in enumerate(inputs.input_ids[0]):
        if token == mask_token_id:
            return i
    return None
```

*Complexity: O (n) where *n* is the number of tokens.*

---

## `get_color_for_attention_score`

### Purpose

Convert a **continuous attention score** into a discrete shade of grey for the PNG heat-maps.

### Logic

1. Convert the incoming TensorFlow scalar to a NumPy float.  
2. Multiply by 255 and round to the nearest integer.  
3. Return an RGB tuple with equal R = G = B values, ensuring true greyscale.

```python
def get_color_for_attention_score(attention_score):
    attention_score = attention_score.numpy()
    value = round(attention_score * 255)
    return value, value, value
```

- *0 → (0, 0, 0)* (pure black)  
- *1 → (255, 255, 255)* (pure white)

---

## `visualize_attentions`

### Purpose

Produce **144 separate attention diagrams**—one for every head in BERT-base.

### Logic

1. **Enumerate layers** (`i`) in the `attentions` tuple.  
2. For each layer, determine `layer_number = i + 1` (human-friendly 1-indexing).  
3. **Enumerate heads** (`k`) inside the current layer tensor (`layer[0]`).  
4. Compute `head_number = k + 1`.  
5. Call `generate_diagram` with  
   - `layer_number`, `head_number`  
   - full `tokens` list  
   - the 2-D slice `attentions[i][0][k]` (shape `[seq_len × seq_len]`).

```python
def visualize_attentions(tokens, attentions):
    for i, layer in enumerate(attentions):
        for k in range(len(layer[0])):
            layer_number = i + 1
            head_number = k + 1
            generate_diagram(
                layer_number,
                head_number,
                tokens,
                attentions[i][0][k]
            )
```

### Result

Running `mask.py` now saves files named, for example,

```
Attention_Layer3_Head10.png
Attention_Layer7_Head4.png
...
```

each containing a square grid where lighter squares indicate stronger self-attention between the corresponding pair of tokens.

# Conclusion

These three functions bridge the gap between BERT’s numerical outputs and an interpretable visual analysis pipeline:

* `get_mask_token_index` pinpoints the prediction target  
* `get_color_for_attention_score` translates weights to greyscale pixels  
* `visualize_attentions` automates the exhaustive generation of 144 annotated heat-maps

Together, they allow you to explore and annotate the rich-but-opaque structure of transformer attention heads.