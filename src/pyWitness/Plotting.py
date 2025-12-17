import numpy as _np
import matplotlib.pyplot as _plt
from scipy.stats import norm as _norm


def _errorBar(k, n, ci) :
    """
    Calculate the confidence interval for a proportion using the Wilson score interval.
    """

    alpha = 1.0 - ci
    z = float(_norm.ppf(1.0 - alpha / 2.0))

    p = k / n
    denominator = 1 + (z*z) / n
    centre = (p + (z * z) / (2.0 * n)) / denominator
    half = z * _np.sqrt((p*(1 - p) + (z*z) / (4*n)) / n) / denominator

    low = centre - half
    high = centre + half
    return (low, high)

def plotIdRatesBarChart(dataProcesseds,
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

    correctRates, falseRates = [], []
    correctLowerErrors, correctUpperErrors = [], []
    falseLowerErrors, falseUpperErrors = [], []

    for c in conditionOder :
        dp = dataProcesseds[c]

        k = int(dp.data_pivot.loc[("targetPresent","suspectId")].sum())
        nTP = int(dp.targetPresentSum)
        p = k / nTP
        correctRates.append(p)

        #  False Alarm Rate Calculation
        nTA = int(dp.targetAbsentSum)

        if errorBars :
            low, high = _errorBar(k, nTP, ci)
            correctLowerErrors.append(low)
            correctUpperErrors.append(high)

        if dp.lineupSize == 1 :
            kReject = int(dp.data_pivot.loc[("targetAbsent","rejectId")].sum())
            kChooseFoil = nTA - kReject
            pChooseFoil = kChooseFoil / nTA
            falseRates.append(pChooseFoil)

            if errorBars :
                low, high = _errorBar(kChooseFoil, nTA, ci)
                falseLowerErrors.append(low)
                falseUpperErrors.append(high)

        else :
            if dp.isDesignateId() :
                kDesignate = int(dp.data_pivot.loc[("targetAbsent","designateId")].sum())
                pDesignate = kDesignate / nTA
                falseRates.append(pDesignate)

                if errorBars :
                    low, high = _errorBar(kDesignate, nTA, ci)
                    falseLowerErrors.append(low)
                    falseUpperErrors.append(high)

            else :
                kChooseFiller = int(dp.data_pivot.loc[("targetAbsent","fillerId")].sum())
                pChooseFiller = kChooseFiller / nTA

                pFinal = pChooseFiller / dp.lineupSize
                falseRates.append(pFinal)

                if errorBars :
                    low, high = _errorBar(kChooseFiller, nTA, ci)
                    low = low / dp.lineupSize
                    high = high / dp.lineupSize
                    falseLowerErrors.append(low)
                    falseUpperErrors.append(high)

    correctRates = _np.array(correctRates)
    falseRates = _np.array(falseRates)

    if errorBars :
        correctLowerErrors = correctRates - _np.array(correctLowerErrors)
        correctUpperErrors = _np.array(correctUpperErrors) - correctRates
        falseLowerErrors = falseRates - _np.array(falseLowerErrors)
        falseUpperErrors = _np.array(falseUpperErrors) - falseRates
        correctErrorBars = [correctLowerErrors, correctUpperErrors]
        falseErrorBars = [falseLowerErrors, falseUpperErrors]
    else :
        correctErrorBars = None
        falseErrorBars = None

    x = _np.arange(len(conditionOder))

    if plotStyle == "separate" :
        fig, axs = _plt.subplots(1, 2, figsize=(12, 6), sharey=True)

        bars1 = axs[0].bar(x, correctRates, yerr=correctErrorBars, capsize=5, color='tab:blue', label='Correct ID Rate')
        axs[0].set_title('Correct Identification Rates')
        axs[0].set_xticks(x)
        axs[0].set_xticklabels(conditionOder)
        axs[0].set_ylim(ylim)
        axs[0].set_ylabel('Identification Rate')

        bars2 = axs[1].bar(x, falseRates, yerr=falseErrorBars, capsize=5, color='tab:orange', label='False ID Rate')
        axs[1].set_title('False Identification Rates')
        axs[1].set_xticks(x)
        axs[1].set_xticklabels(conditionOder)
        axs[1].set_ylim(ylim)
        axs[1].set_ylabel('Identification Rate')

        if annotate :
            for b, v in zip(bars1, correctRates) :
                axs[0].text(b.get_x()+b.get_width()/2.0, b.get_height(), f"{v:.3f}",
                            ha="center", va="bottom")
            for b, v in zip(bars2, falseRates) :
                axs[1].text(b.get_x()+b.get_width()/2.0, b.get_height(), f"{v:.3f}",
                            ha="center", va="bottom")

    elif plotStyle == "grouped" :
        fig, ax = _plt.subplots(1, 1, figsize=(8, 6))

        width = 0.35
        bars1 = ax.bar(x - width/2, correctRates, width, yerr=correctErrorBars, capsize=5, color='skyblue', label='Correct ID Rate')
        bars2 = ax.bar(x + width/2, falseRates, width, yerr=falseErrorBars, capsize=5, color='salmon', label='False ID Rate')

        ax.set_title('Identification Rates')
        ax.set_xticks(x)
        ax.set_xticklabels(conditionOder)
        ax.set_ylim(ylim)
        ax.set_ylabel('Identification Rate')
        ax.legend()

        if annotate :
            for b, v in zip(bars1, correctRates) :
                ax.text(b.get_x()+b.get_width()/2.0, b.get_height(), f"{v:.3f}",
                        ha="center", va="bottom")
            for b, v in zip(bars2, falseRates) :
                ax.text(b.get_x()+b.get_width()/2.0, b.get_height(), f"{v:.3f}",
                        ha="center", va="bottom")

    else :
        raise ValueError(f"Invalid plotStyle '{plotStyle}'. Use 'separate' or 'grouped'.")

    if title is not None :
        fig.suptitle(title)

    _plt.show()

















