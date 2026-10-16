# F1 Predictor

[Open the live predictor](https://f1-eight-theta.vercel.app/)

Compare two Formula 1 drivers using a random forest trained on historical race results. The app estimates the probability that Driver A finishes ahead of Driver B from their grid positions, qualifying performance, and recent form.

## How to use

1. Open the [website](https://f1-eight-theta.vercel.app/) and select **Compare drivers**.
2. Select **Next example** to load one of five historical comparisons, or enter your own feature values.
3. Enter every difference as **Driver A minus Driver B**. For example, if A starts 8th and B starts 3rd, the grid difference is `8 - 3 = 5`. The best grid position is `3`.
4. Leave unknown values blank. The model uses training medians and available missing-value indicators.
5. Select **Predict result** to see both drivers' probabilities.
6. Expand **First tree’s decision path** to see the questions one tree used. The final prediction averages all 20 trees.

A result of **Driver A: 70%** means the forest estimates a 70% chance that A finishes ahead of B. It does not mean A has a 70% chance of winning the race. The two probabilities add up to 100%.

Use **Next example** again to try another comparison. The example message shows which driver actually finished ahead. Select **F1 / PREDICTOR** to return to the home page.

## How it works

### Preparing the data

`features.py` combines race, result, and qualifying CSV files. It converts qualifying times into seconds, calculates each driver's session gap to the fastest lap, and builds driver and constructor form from the previous five races. Form features are shifted so the current race result is excluded.

Drivers from the same race are paired. Their features are subtracted to describe a head-to-head comparison, and the label records which driver finished ahead. Pair orientation is randomly flipped for a subset of rows, with the label flipped too. Pairs where both drivers have retirement status `R` are excluded.

The data is split chronologically: 2014–2024 for training and 2025 for evaluation. Missing values are filled using training medians. Missing-value flags are included for columns that contain missing values in training.

### Growing the forest

Each of the 20 trees receives a bootstrap sample: training rows drawn with replacement. At every node, the tree considers a random subset of features and selects the feature and threshold with the largest reduction in weighted Gini impurity.

A branch stops when it reaches depth 5, contains fewer than 10 rows, has only one label, or has no improving split. Each leaf stores the proportion of its rows with label 1. The forest prediction is the average of the 20 reached leaf probabilities.

### Predicting in the browser

The website loads the exported forest from `model.json`. JavaScript follows each tree's conditions and averages the results locally. Predictions require no account, Python server, or live API request.

## Model

| Setting | Value |
| --- | --- |
| Trees | 20 |
| Maximum depth | 5 |
| Minimum samples to split | 10 |
| Features per split | Floor of the square root of the feature count |
| Sampling | Bootstrap rows with replacement |
| Random seed | 42 |
| Training seasons | 2014–2024 |
| Holdout season | 2025 |
| Training pairs | 42,835 |
| Holdout pairs | 4,139 |
| Exported forest holdout accuracy | Approximately 76.8% |

Each tree returns the share of label 1 at its reached leaf. The forest averages these shares. Label 1 means Driver A finishes ahead of Driver B. This is historical pairwise classification, not live race forecasting, and probabilities are not calibrated.

`algorithm.py` contains the learning implementation. `frontend/export_model.py` trains a separate, optimized NumPy implementation using cumulative counts for split search and the same forest settings. The website uses that exported forest, not a live call to `algorithm.py`. Different numerical tie handling can produce different trees and metrics.

## Inputs

All differences are **Driver A minus Driver B**.

| Input | Meaning |
| --- | --- |
| Grid difference | Difference in starting positions after preprocessing pit lane starts |
| Pit lane flag difference | Difference between flags: 1 for pit lane start, 0 otherwise |
| Qualifying position difference | Difference in qualifying positions |
| Qualifying sessions difference | Difference in the number of sessions with recorded times |
| Q1 / Q2 / Q3 gap differences | Difference in session gaps to the fastest driver, in percentage points |
| Driver form difference | Difference in average finishing position over each driver's previous five races |
| Team form difference | Difference in rolling team finishing-position averages over the preceding five races |
| Best grid position | Lower of the two processed grid positions |

Leave unknown inputs blank. The frontend fills them with training medians and sets missing indicators where the training schema includes them. Historical examples retain their original missingness. Driver names and current race feeds are not included.

## Run locally

To use the included website locally, run this from the repository root:

```sh
python3 -m http.server 8080 --directory public
```

Open http://localhost:8080. Serve the files over HTTP so the browser can load `model.json`.

## Project structure

| File | Purpose |
| --- | --- |
| `features.py` | Prepares features and chronological training/test splits |
| `algorithm.py` | Learning implementation of the random forest |
| `frontend/export_model.py` | Builds the optimized browser model when the frontend checkout is available |
| `public/index.html` | Home page |
| `public/predictor.html` | Comparison form and browser predictions |
| `public/model.json` | Exported forest, training medians, examples, and evaluation metrics |

## Limitations

The app uses historical data and manually entered features; it does not fetch current drivers, qualifying sessions, or race updates. Its accuracy measures driver-pair classification on the 2025 holdout set, not race-winner accuracy. Probabilities are not calibrated and should be treated as model estimates.
