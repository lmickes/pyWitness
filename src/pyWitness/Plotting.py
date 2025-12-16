import numpy as _np
import matplotlib.pyplot as _plt
from scipy.stats import _stats

def _errorBar(k, n, ci) :
    """
    Calculate the confidence interval for a proportion using the Wilson score interval.
    """

    alpha = 1.0 - ci
    z = _stats.norm.ppf(1 - alpha / 2)

    p = k / n
    denominator = 1 + (z*z) / n
    centre = p + (z*z) / (2*n) / denominator
    half = z * _np.sqrt((p*(1 - p) + (z*z) / (4*n)) / n) / denominator

    low = centre - half
    high = centre + half
    return (low, high)

def plotIdRateBarChart(dataProcesseds,
                       plotStyle = "separate",
                       conditionOder = None,
                       title = None,
                       ylim = [0.0, 1.0],
                       annotate = True,
                       errorBars = True,
                       ci = 0.95,) :
    """
    Plot identification rate bar chart for one or more DataProcessed objects.
    """

    if dataProcesseds is None or len(dataProcesseds) == 0 :
        raise ValueError("No DataProcessed objects provided for plotting.")

    if conditionOder is None :
        conditionOder = list(dataProcesseds.keys())
    else :
        conditions = []
        for c in conditionOder :
            if c not in dataProcesseds :
                raise ValueError(f"Condition '{c}' not found in provided DataProcessed objects.")
            conditions.append(c)

    correctRates, falserates = [], []
    correctLowerErrors, correctUpperErrors = [], []
    falseLowerErrors, falseUpperErrors = [], []

    for c in conditionOder :
        dp = dataProcesseds[c]

        k = int(dp.data_pivot.loc["targetPresent","suspectId"].sum())
        n = int(dp.targetPresentSum)
        p = k/n
        correctRates.append(p)

















