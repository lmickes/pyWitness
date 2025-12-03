import numpy as _np
import matplotlib.pyplot as _plt
from scipy.stats import norm
from scipy import integrate

class GaussianSDTModel:
    """

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
            Analytic d' for equal-variance SDT: d' = (mu_signal - mu_noise) / sigma_noise
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


