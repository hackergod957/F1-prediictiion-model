"""Build a browser-ready random forest without importing or modifying algorithm.py."""
from pathlib import Path
import sys
import json
import os
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
from features import features


def build_tree(x, y, rng, depth=0):
    node = {'probability': float(y.mean()), 'samples': len(y)}
    if depth >= 5 or len(y) < 10 or np.all(y == y[0]):
        return node
    parent = 2 * y.mean() * (1 - y.mean())
    best = (0, None, None)
    for column in rng.choice(x.shape[1], size=max(1, int(np.sqrt(x.shape[1]))), replace=False):
        order = np.argsort(x[:, column])
        values, targets = x[order, column], y[order]
        n = np.arange(1, len(y))
        sums = np.cumsum(targets)[:-1]
        lp, rp = sums / n, (targets.sum() - sums) / (len(y) - n)
        gains = parent - (n * 2 * lp * (1-lp) + (len(y)-n) * 2 * rp * (1-rp)) / len(y)
        gains[values[:-1] == values[1:]] = -np.inf
        index = int(np.argmax(gains))
        if gains[index] > best[0]:
            best = (float(gains[index]), int(column), float((values[index] + values[index+1]) / 2))
    gain, column, threshold = best
    if column is None:
        return node
    left = x[:, column] <= threshold
    node.update(feature=column, threshold=threshold,
                left=build_tree(x[left], y[left], rng, depth+1),
                right=build_tree(x[~left], y[~left], rng, depth+1))
    return node


def predict(row, node):
    while 'feature' in node:
        node = node['left'] if row[node['feature']] <= node['threshold'] else node['right']
    return node['probability']


if __name__ == '__main__':
    train, test, labels, test_labels = features()
    rng = np.random.default_rng(42)
    forest = []
    for _ in range(20):
        indices = rng.choice(len(train), size=len(train), replace=True)
        forest.append(build_tree(train.to_numpy()[indices], labels.to_numpy()[indices], rng))
    predictions = np.array([np.mean([predict(row, tree) for tree in forest]) for row in test.to_numpy()])
    accuracy = float(((predictions >= .5) == test_labels.to_numpy()).mean())
    payload = dict(forest=forest, nTrees=len(forest), maxDepth=5, columns=list(train.columns), defaults=train.median().to_dict(),
                   accuracy=accuracy, trainRows=len(train), testRows=len(test),
                   example=test.iloc[0].to_dict(), examples=[{'values': test.iloc[i].to_dict(), 'actual': int(test_labels.iloc[i]), 'probability': float(predictions[i])} for i in [0, 22, 100, 200, 300]])
    output = Path(__file__).parent / 'dist' / 'model.json'
    output.write_text(json.dumps(payload, allow_nan=False))
    print(f'Exported forest; 2025 pair accuracy: {accuracy:.2%}')
