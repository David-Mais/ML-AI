# Introduction

This document explains the functionality and logic of our shopping prediction code. The code is responsible for loading and processing shopping data, training a k-nearest neighbor classifier on that data, and evaluating the classifier's performance. In addition to detailing each method, we explain why the model predicts negatives (no purchase) more accurately than positives (purchase) and how the imbalance of data—having far more negative examples than positive—plays a critical role.

# Overview of the Code

The solution is composed of the following functions (excluding the main method):

- **`load_data(filename)`**  
  Loads shopping data from a CSV file and converts it into two lists: evidence (features) and labels (target outcomes). Each row in the CSV is processed into a list of 17 features with specific numeric types.

- **`month_number(month)`**  
  Converts month abbreviations into corresponding integer indices (0 for January up to 11 for December).

- **`visitor_type_number(visitor_type)`**  
  Encodes the visitor type as an integer. It returns 1 for returning visitors and 0 for others.

- **`bool_number(bool_value)`**  
  Converts string representations of boolean values to integers, where `"TRUE"` converts to 1 and other values to 0.

- **`train_model(evidence, labels)`**  
  Trains a k-nearest neighbor classifier (k=1) using the evidence and labels, and returns the fitted model.

- **`evaluate(labels, predictions)`**  
  Computes and returns sensitivity (true positive rate) and specificity (true negative rate) by comparing true labels with predictions. This function also reveals a key observation: the model predicts negatives more accurately than positives. The imbalance between negatives and positives in the data is a major factor in this behavior.

# Detailed Code Explanation

## 1. `load_data(filename)`

### Purpose
The `load_data` function reads shopping data from a CSV file and converts it into two lists:
- **Evidence:** A list of lists where each inner list contains 17 features, properly cast to numerical types.
- **Labels:** A list of binary values indicating whether revenue was generated (1) or not (0).

### How It Works
- **CSV Reading:**  
  Opens the file and uses `csv.DictReader` to iterate over each row.
- **Feature Conversion:**  
  Each row’s columns are converted to the required numerical types:
  - Integers for counts (e.g., *Administrative*, *Informational*).
  - Floats for duration and rate features (e.g., *Administrative_Duration*, *BounceRates*).
  - The month is converted using `month_number`.
  - The visitor type and weekend are processed using `visitor_type_number` and `bool_number`, respectively.
- **Label Extraction:**  
  The *Revenue* column is converted to an integer (1 for `"TRUE"` and 0 otherwise).

### Code Snippet

```python
def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).
    """
    evidence = []
    labels = []
    with open(filename, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            current_evidence = [
                int(row["Administrative"]),
                float(row["Administrative_Duration"]),
                int(row["Informational"]),
                float(row["Informational_Duration"]),
                int(row["ProductRelated"]),
                float(row["ProductRelated_Duration"]),
                float(row['BounceRates']),
                float(row['ExitRates']),
                float(row['PageValues']),
                float(row['SpecialDay']),
                month_number(row['Month']),
                int(row['OperatingSystems']),
                int(row['Browser']),
                int(row['Region']),
                int(row['TrafficType']),
                visitor_type_number(row['VisitorType']),
                bool_number(row['Weekend'])
            ]
            evidence.append(current_evidence)
            labels.append(bool_number(row['Revenue']))
    return evidence, labels
```

---

## 2. `month_number(month)`

### Purpose
Converts the month value from the CSV (provided as a string like "Jan" or "Feb") into an integer index.

### How It Works
- The function checks the month string and returns the corresponding index:
  - "Jan" returns 0, "Feb" returns 1, up to "Dec" which returns 11.

### Code Snippet

```python
def month_number(month):
    if month == "Jan":
        return 0
    elif month == "Feb":
        return 1
    elif month == "Mar":
        return 2
    elif month == "Apr":
        return 3
    elif month == "May":
        return 4
    elif month == "June":
        return 5
    elif month == "Jul":
        return 6
    elif month == "Aug":
        return 7
    elif month == "Sep":
        return 8
    elif month == "Oct":
        return 9
    elif month == "Nov":
        return 10
    elif month == "Dec":
        return 11
```

---

## 3. `visitor_type_number(visitor_type)`

### Purpose
Encodes the `VisitorType` column from the CSV into a binary numeric format.

### How It Works
- Returns 1 if `visitor_type` is `"Returning_Visitor"`; otherwise, returns 0.

### Code Snippet

```python
def visitor_type_number(visitor_type):
    if visitor_type == "Returning_Visitor":
        return 1
    else:
        return 0
```

---

## 4. `bool_number(bool_value)`

### Purpose
Converts string representations of boolean values into integers.

### How It Works
- Checks if the input string is exactly `"TRUE"`.
- Returns 1 if it is, otherwise returns 0.

### Code Snippet

```python
def bool_number(bool_value):
    if bool_value == "TRUE":
        return 1
    else:
        return 0
```

---

## 5. `train_model(evidence, labels)`

### Purpose
Trains a k-nearest neighbor classifier on the given evidence and labels.

### How It Works
- Uses scikit-learn’s `KNeighborsClassifier` with `n_neighbors` set to 1.
- Fits the model on the provided data and returns the trained classifier.

### Code Snippet

```python
def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model
```

---

## 6. `evaluate(labels, predictions)`

### Purpose
Evaluates the model's predictions by calculating sensitivity and specificity:
- **Sensitivity (True Positive Rate):** The proportion of actual positive cases (purchases) correctly predicted.
- **Specificity (True Negative Rate):** The proportion of actual negative cases (non-purchases) correctly predicted.

### How It Works
- Iterates over actual labels and predictions.
- **For each positive (actual == 1):**
  - Increments the total positive count.
  - Increments the true positives count if the prediction is also positive.
- **For each negative (actual == 0):**
  - Increments the total negative count.
  - Increments the true negatives count if the prediction is negative.
- Calculates sensitivity as the ratio of true positives to the total positive count.
- Calculates specificity as the ratio of true negatives to the total negative count.

### Code Snippet

```python
def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).
    """
    true_positives = 0
    true_negatives = 0
    total_positives = 0
    total_negatives = 0

    for actual, predicted in zip(labels, predictions):
        if actual == 1:
            total_positives += 1
            if predicted == 1:
                true_positives += 1
        else:
            total_negatives += 1
            if predicted == 0:
                true_negatives += 1

    sensitivity = true_positives / total_positives if total_positives > 0 else 0
    specificity = true_negatives / total_negatives if total_negatives > 0 else 0
    return sensitivity, specificity
```

### Why the Model Guesses Negatives More Accurately Than Positives

- **Class Imbalance:**  
  In the dataset, there are significantly more negatives (instances where no purchase occurred) than positives (instances where a purchase occurred). This imbalance means that the classifier sees a far greater number of negative examples during training.
  
- **Majority Class Bias:**  
  Because negative examples are the majority, the classifier naturally becomes better at predicting negatives. It optimizes its performance on the majority class, which results in higher specificity (accuracy in predicting negatives) compared to sensitivity (accuracy in predicting positives).
  
- **Impact on Metrics:**  
  Even if overall accuracy seems reasonable, the true positive rate (sensitivity) is lower because the model has less opportunity to learn the distinguishing features of the rarer positive cases. The evaluation metrics reflect this imbalance: while most negatives are predicted correctly (high specificity), many positives might be misclassified, leading to low sensitivity.

---

# Conclusion

This codebase demonstrates a complete pipeline for processing shopping data and predicting user purchases using a k-nearest neighbor classifier. Key functions include:
- Data loading and type conversion via **`load_data`**.
- Helper functions for mapping categorical data into numeric representations (**`month_number`**, **`visitor_type_number`**, **`bool_number`**).
- Model training with **`train_model`**.
- Comprehensive evaluation with **`evaluate`**, which not only computes sensitivity and specificity but also highlights how the underlying data imbalance causes the model to predict negatives more accurately than positives.

By understanding each component and the role that dataset imbalance plays, you are better equipped to tune the model and explore techniques (such as resampling or threshold adjustments) that may help improve positive predictions in future iterations.