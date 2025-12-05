import numpy as _np
import matplotlib.pyplot as _plt
from scipy.stats import norm
from scipy import integrate

class GaussianSDTModel:
    """
    Simple SDT with two Gaussians:
    - Noise: X_N ~ N(mu_noise, sigma_noise)
    - Signal: X_S ~ N(mu_signal, sigma_signal)

    In classic SDT toy models we usually set:
        mu_noise = 0, sigma_noise = 1
        mu_signal = dprime, sigma_signal = 1

    Methods provide:
    - hit_far_rate(criterion)
    - roc_curve()
    - dprime_from_rates(HR, FAR)
    - dprime_curve(criterion_grid)
    - pauc(xmax)          : integrate ROC over FAR from 0 to xmax
    - pauc_at_criterion(c): x_max = FAR(c), so pAUC is a function of c
    """
    def __init__(self,
                 mu_noise: float = 0.0,
                 mu_signal: float = 1.5,
                 sigma_noise: float = 1.0,
                 sigma_signal: float = 1.0):
        self.mu_noise = mu_noise
        self.mu_signal = mu_signal
        self.sigma_noise = sigma_noise
        self.sigma_signal = sigma_signal

    @property
    def dprime_analytic(self) -> float:
        """
        Analytic d' for equal-variance SDT:
            d' = (mu_signal - mu_noise) / sigma_noise
        If variances differ, this is still a useful 'effective' separation.
        """
        return (self.mu_signal - self.mu_noise) / self.sigma_signal

    def hit_far_rate(self, criterion: float):
        """
        Compute hit rate and false alarm rate for a given decision criterion.
            HR = P(x_signal > criterion)
            FAR = P(x_noise > criterion)
        """
        hit_rate = 1 - norm.cdf(criterion, loc=self.mu_signal, scale=self.sigma_signal)
        far_rate = 1 - norm.cdf(criterion, loc=self.mu_noise, scale=self.sigma_noise)
        return hit_rate, far_rate

    def roc_curve(self, n_points: int = 200, span: float = 1.0):
        """
        Construct ROC curve by sweeping criterion across the distributions.
        n_points: number of points to compute on the ROC curve.
        span: fraction of the way from mu_noise to mu_signal to cover with criteria.
        """
        # Cover a range that comfortably includes both distributions
        lower = min(self.mu_noise, self.mu_signal) - span * max(self.sigma_noise, self.sigma_signal)
        upper = max(self.mu_noise, self.mu_signal) + span * max(self.sigma_noise, self.sigma_signal)
        criteria = _np.linspace(lower, upper, n_points)

        HRs, FARs = [], []
        for c in criteria:
            hr, fa = self.hit_far_rate(c)
            HRs.append(hr)
            FARs.append(fa)
        HRs = _np.array(HRs)
        FARs =_np.array(FARs)

        # Sort by FAR (0 -> 1) just to be safe
        order = _np.argsort(FARs)
        return FARs[order], HRs[order], criteria[order]

    @staticmethod
    def dprime_from_rates(HR: float, FAR: float):
        """
        Classic SDT definition: d' = z(HR) - z(FAR)
        Handles edge cases by clipping probabilities.
        """
        eps = 1e-6
        HR = _np.clip(HR, eps, 1 - eps)
        FAR = _np.clip(FAR, eps, 1 - eps)
        zHR = norm.ppf(HR)
        zFAR = norm.ppf(FAR)
        return zHR - zFAR

    def dprime_from_criterion(self, criterion: float) -> float:
        HR, FAR = self.hit_far_rate(criterion)
        return self.dprime_from_rates(HR, FAR)

    def dprime_curve(self, criteria: _np.ndarray) -> _np.ndarray:
        dvals = []
        for c in criteria:
            dvals.append(self.dprime_from_criterion(c))
        return _np.array(dvals)

    def _roc_given_far(self, far: float) -> float:
        """
        ROC in parametric form: given FAR, return HR.
        Steps:
        1) Find criterion c such that FAR(c) = far.
           For the noise distribution:
               FAR = P(X_N >= c) = 1 - Phi((c - mu_N)/sigma_N)
               => 1 - far = Phi((c - mu_N)/sigma_N)
               => (c - mu_N)/sigma_N = Phi^-1(1 - far)
               => c = mu_N + sigma_N * Phi^-1(1 - far)
        2) Use the same c to compute HR(c).
        """
        eps = 1e-9
        far = float(_np.clip(far, eps, 1 - eps))
        z = norm.ppf(1.0 - far)
        c = self.mu_noise + self.sigma_noise * z
        HR, _ = self.hit_far_rate(c)
        return HR

    def pauc(self, xmax: float) -> float:
        """
        Partial AUC from FAR=0 to FAR=xmax:
            pAUC(xmax) = ∫_0^xmax ROC(far) dfar
        """
        xmax = float(_np.clip(xmax, 0.0, 1.0))

        def integrand(fa):
            return self._roc_given_far(fa)

        val, _ = integrate.quad(integrand, 0.0, xmax)
        return val

    def pauc_at_criterion(self, criterion: float) -> float:
        """
        Define pAUC as a function of threshold by:
            xmax = FAR(criterion)
            pAUC(criterion) = ∫_0^{FAR(c)} ROC(far) dfar
        This matches how your pyWitness pAUC integrates from 0 to some xmax.
        """
        _, FAR = self.hit_far_rate(criterion)
        return self.pauc(FAR)


def plot_gaussians_with_criterion(model: GaussianSDTModel, criterion: float, ax=None):
    if ax is None:
        ax = _plt.gca()

    # x-range
    span = 4.0
    lower = min(model.mu_noise, model.mu_signal) - span * max(model.sigma_noise, model.sigma_signal)
    upper = max(model.mu_noise, model.mu_signal) + span * max(model.sigma_noise, model.sigma_signal)
    xs = _np.linspace(lower, upper, 400)

    noise_pdf = norm.pdf((xs - model.mu_noise) / model.sigma_noise) / model.sigma_noise
    signal_pdf = norm.pdf((xs - model.mu_signal) / model.sigma_signal) / model.sigma_signal

    ax.plot(xs, noise_pdf, label="Noise", linestyle="-")
    ax.plot(xs, signal_pdf, label="Signal", linestyle="--")
    ax.axvline(criterion, color="k", linestyle=":", label="Criterion")

    ax.text(
        0.98, 0.72,             # x,y in axes coordinates (0~1)
        f"c = {criterion:.2f}",
        transform=ax.transAxes,
        ha="right", va="top",
        fontsize=10
    )

    ax.set_xlabel("Internal response x")
    ax.set_ylabel("Density")
    ax.set_title("Signal vs Noise Distributions")
    ax.legend()
    ax.grid(False)

def plot_roc(model: GaussianSDTModel, criterion: float, ax=None, shade_pauc=True):
    if ax is None:
        ax = _plt.gca()

    FARs, HRs, criteria = model.roc_curve(n_points=400)
    ax.plot(FARs, HRs, label="ROC", color="C0")

    HR_c, FAR_c = model.hit_far_rate(criterion)
    ax.scatter([FAR_c], [HR_c], color="red", zorder=3,
               label="Current c")

    if shade_pauc:
        mask = FARs <= FAR_c
        x_fill = FARs[mask]
        y_fill = HRs[mask]

        if x_fill[0] > 0:
            x_fill = _np.insert(x_fill, 0, 0.0)
            y_fill = _np.insert(y_fill, 0, 0.0)

        ax.fill_between(x_fill, 0, y_fill, alpha=0.25,
                        color="C0", label="pAUC region")

    ax.text(
        0.98, 0.26,
        f"FAR(c) = {FAR_c:.2f}\nHR(c)  = {HR_c:.2f}",
        transform=ax.transAxes,
        ha="right", va="bottom", fontsize=10
    )

    ax.plot([0, 1], [0, 1], "k--", linewidth=1)

    ax.set_xlabel("False Alarm Rate (FAR)")
    ax.set_ylabel("Hit Rate (HR)")
    ax.set_title("ROC Curve")
    ax.legend()
    ax.set_xlim(-0.01, 1.01)
    ax.set_ylim(-0.01, 1.01)
    ax.set_aspect("equal", adjustable="box")

def plot_dprime_and_pauc(model: GaussianSDTModel, ax1=None, ax2=None, current_c=None):
    """
    Plot d'(c) and pAUC(c) as functions of criterion.
    If current_c is not None, mark that position with a vertical line + marker.
    """
    span = 4.0
    lower = min(model.mu_noise, model.mu_signal) - span * max(model.sigma_noise, model.sigma_signal)
    upper = max(model.mu_noise, model.mu_signal) + span * max(model.sigma_noise, model.sigma_signal)
    criteria = _np.linspace(lower, upper, 200)

    dvals = model.dprime_curve(criteria)
    pauc_vals = _np.array([model.pauc_at_criterion(c) for c in criteria])

    if ax1 is None or ax2 is None:
        fig, (ax1, ax2) = _plt.subplots(1, 2, figsize=(10, 4))

    # d'(c) curve
    ax1.plot(criteria, dvals, label="d'(c)")
    ax1.axhline(model.dprime_analytic, color="k", linestyle="--", label="Analytic d'")
    ax1.set_xlabel("Criterion c")
    ax1.set_ylabel("d'(c)")
    ax1.set_title("d' as a function of criterion")

    if current_c is not None:
        d_now = model.dprime_from_criterion(current_c)
        ax1.axvline(current_c, color="red", linestyle=":", alpha=0.8)
        ax1.scatter([current_c], [d_now], color="red")
    ax1.legend()

    # pAUC(c) curve
    ax2.plot(criteria, pauc_vals, label="pAUC(c)")
    ax2.set_xlabel("Criterion c")
    ax2.set_ylabel("pAUC(c)")
    ax2.set_title("pAUC as a function of criterion")

    if current_c is not None:
        pauc_now = model.pauc_at_criterion(current_c)
        ax2.axvline(current_c, color="red", linestyle=":", alpha=0.8)
        ax2.scatter([current_c], [pauc_now], color="red")
    ax2.legend()

    _plt.tight_layout()


try:
    from ipywidgets import interact, FloatSlider
except ImportError:
    interact = None
    FloatSlider = None

def interactive_sdt_demo(model,
                         c_init=0.5,
                         c_min=-4.0,
                         c_max=4.0,
                         c_step=0.1):
    """
    Launch an interactive SDT demo for a given model.

    Parameters
    ----------
    model : GaussianSDTModel
    c_init, c_min, c_max, c_step : float
        Slider settings for the decision criterion c.
    """
    if interact is None or FloatSlider is None:
        raise ImportError(
            "ipywidgets is required for interactive_sdt_demo. "
            "Install with `pip install ipywidgets` and enable it in Jupyter."
        )

    def _update(c):
        # robustly convert c to float
        if hasattr(c, "value"):
            c_val = float(c.value)
        else:
            c_val = float(c)

        fig, axes = _plt.subplots(1, 3, figsize=(14, 4))

        plot_gaussians_with_criterion(model, c_val, ax=axes[0])
        plot_roc(model, c_val, ax=axes[1])

        d_val = model.dprime_from_criterion(c_val)
        pauc_val = model.pauc_at_criterion(c_val)

        axes[2].axis("off")
        text = (
            f"Criterion c = {c_val:.2f}\n"
            f"d'(c)      = {d_val:.3f}\n"
            f"Analytic d' = {model.dprime_analytic:.3f}\n\n"
            # f"The point on ROC is defined by a set of FAR(c) and HR(c).\n"
            # f"pAUC(c) is Calculated by integrating ROC from FAR=0 to FAR(c).\n"
            f"pAUC(c) = {pauc_val:.3f}"
        )
        axes[2].text(0.01, 0.01, text, va="bottom", ha="left", fontsize=11)
        _plt.tight_layout()

    slider = FloatSlider(
        value=c_init,
        min=c_min,
        max=c_max,
        step=c_step,
        description="Criterion c"
    )

    return interact(_update, c=slider)
