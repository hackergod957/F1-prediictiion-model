# F1 predictor frontend

The frontend source and model exporter are included as ordinary files in the main repository. See ../README.md for setup and rebuild commands.

From the repository root:

```sh
.venv/bin/python frontend/export_model.py
.venv/bin/python -m http.server 8080 --directory frontend/dist
```

Open http://localhost:8080 for the home page; the comparison tool is at /predictor.html. The exported model is included, so rebuilding is optional.
Host `frontend/dist` on any static web host; no Python server is needed for predictions.

The adapter imports `features()` and trains a separate NumPy implementation of a
20-tree Gini random forest (depth 5, minimum split group 10, seed 42). It does not import
`algorithm.py`; it uses a faster cumulative-count split search with the same forest configuration. Training uses
2014–2024 only; the displayed metric uses 2025. Blank inputs use training medians
and the existing missing-indicator schema. The model JSON includes training
medians, five processed test examples, and aggregate metrics, not the raw datasets.

Inputs are engineered feature differences, not driver names. Driver and team form
are average finishing positions over the preceding five races. Qualifying gaps
are percentages relative to each session's fastest lap; their differences are
percentage points. Pit lane flags are 1 for pit lane starts and 0 otherwise.
