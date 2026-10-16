from features import features
import pandas as pd
import numpy as np

X_train,X_test,y_train,y_test = features()

def impurity(labels : pd.Series):
    counts = labels.value_counts()
    probabilities = [(count / sum(counts)) * 100 for count in counts]
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

def getBestSplit(X: pd.DataFrame, labels: pd.Series ):
    feature = None
    threshold = None
    bestDrop = 0

    for column in X.columns:

        thresholds  , drop = getThreshold(X[column],labels)

        if drop > bestDrop:
            feature = column
            threshold = thresholds
            bestDrop = drop

    return feature,threshold,bestDrop

