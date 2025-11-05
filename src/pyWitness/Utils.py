import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pandas

def getColorOfLabeledFromGca(label) :
    axes     = _plt.gca()
    children = axes.get_children()

    for child in children :
        # print(child.get_label())

        if label == child.get_label() :
            fc = child.get_facecolor()[0]
            return fc

            #print(fc)

def find_bins(val, bin_points, outliner_val=50, dropna=True):
    '''
    Compute bin edges by cumulative probability, after removing outliers.

    Parameters
    ----------
    val: values (confidence value in general)
    bin_points: number of bins. The data will be divided into (bin_points-1) bins.
    outliner_val: number of bins. Defaults to 50. Values greater than outliner_val are considered outliers and removed before binning.
    dropna: drop outlier if True. Defaults to True.
    '''
    s = _pandas.Series(val).astype("float")
    if dropna :
        s = s.dropna()

    # Remove outliers
    s = s[s < outliner_val]

    s= s.replace([_np.inf, -_np.inf], _np.nan).dropna()
    if len(s) == 0 :
        raise ValueError("No valid data points available after removing outliers and NaNs.")

    # Ensure bin_points is at least 2
    bin_points = int(bin_points)
    if bin_points < 2 :
        raise ValueError("bin_points must be at least 2 to create bins.")

    pobs = _np.linspace(0, 1, bin_points)
    edges = _np.quantile(s.values, pobs, method="linear")
    for i in range(1,len(edges)) :
        if edges[i] <= edges[i-1] :
            edges[i] = _np.nextafter(edges[i-1],_np.inf)

    return edges