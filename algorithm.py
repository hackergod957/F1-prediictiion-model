from features import features
import pandas as pd
import numpy as np

X_train,X_test,y_train,y_test = features()

def impurity(labels : pd.Series):
    _, counts = np.unique(labels, return_counts=True)
    probabilities = [(count / sum(counts)) for count in counts]
    gini = 1 - sum(p**2 for p in probabilities)
    return gini

def getThreshold(feature : pd.Series,labels : pd.Series):

    feature = feature.to_numpy()
    labels = labels.to_numpy()

    sorted_indices = np.argsort(feature)

    labels = labels[sorted_indices]
    feature = feature[sorted_indices]

    gini = impurity(labels)
    bestDrop = 0
    threshold = None

    for value in range(len(feature) - 1):

        if feature[value] == feature[value+1]:
            continue

        
        left = labels[:value + 1]
        right = labels[value + 1 : ]

        weighted = impurity(left) *   len(left) / len(labels)  + impurity(right) *  len(right) / len(labels)

        newThreshold = (feature[value] + feature[value + 1]) / 2

        drop = gini - weighted

        if drop > bestDrop:
            bestDrop = drop
            threshold = newThreshold


    return threshold , bestDrop

def getBestSplit(X: pd.DataFrame, labels: pd.Series , rng):
    feature = None
    threshold = None
    bestDrop = 0

    count = max(1, int(np.sqrt(X.shape[1])))
    columns = rng.choice(X.columns, size=count, replace=False)

    for column in columns:

        thresholds  , drop = getThreshold(X[column],labels)

        if drop > bestDrop:
            feature = column
            threshold = thresholds
            bestDrop = drop

    return feature,threshold,bestDrop


def buildTree( X:pd.DataFrame,labels:pd.Series , rng, depth=0 , max_depth=5, min_samples_split=10 ):
    node = {"probability": float(labels.mean())}


    if(
        depth >= max_depth
        or len(labels) < min_samples_split
        or labels.nunique() <= 1
    ):
        return node 
    
    feature ,  threshold , drop = getBestSplit(X,labels,rng)
    
    if feature is None:
        return node


    left = X[feature] <= threshold
    right = ~left

    node.update(
        {

            "feature" : feature,
            "threshold": threshold,
            "drop" : drop,
            "left" : buildTree(X.loc[left] , labels.loc[left] , rng ,depth + 1, max_depth, min_samples_split  ),
            "right": buildTree(X.loc[right] , labels.loc[right], rng ,depth + 1, max_depth, min_samples_split  )

        }

    )

    return node

    
def predictProbability(row, tree):
    while "feature" in tree:
        if row[tree["feature"]] <= tree["threshold"]:
            tree = tree["left"]
        else:
            tree = tree["right"]

    return tree["probability"]


def buildForest(
    X, labels, n_trees=20,
    max_depth=5, min_samples_split=10, seed=42
):
    rng = np.random.default_rng(seed)
    forest = []

    for _ in range(n_trees):
        indices = rng.choice(len(X), size=len(X), replace=True)

        sample_X = X.iloc[indices].reset_index(drop=True)
        sample_y = labels.iloc[indices].reset_index(drop=True)

        tree = buildTree(
            sample_X, sample_y, rng,
            max_depth=max_depth,
            min_samples_split=min_samples_split
        )
        forest.append(tree)

    return forest


forest = buildForest(X_train, y_train)

probabilities = X_test.apply(
    lambda row: np.mean([
        predictProbability(row, tree)
        for tree in forest
    ]),
    axis=1
)

predictions = (probabilities >= 0.5).astype(int)
accuracy = (predictions == y_test).mean()

print(f"Accuracy: {accuracy:.2%}")