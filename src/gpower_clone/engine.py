"""Power calculations for chi-square contingency tables.

The implementation uses regularized incomplete gamma functions and the
Poisson-mixture representation of the noncentral chi-square distribution.
"""

from __future__ import annotations

import math


_EPS = 2.0e-15
_FPMIN = 1.0e-300
_MAX_ITER = 10000
MAX_SAMPLE_SIZE = 10_000_000


def _gamma_p(a: float, x: float) -> float:
    """Regularized lower incomplete gamma P(a, x)."""
    if x <= 0.0:
        return 0.0
    if math.isinf(x):
        return 1.0
    if x < a + 1.0:
        term = total = 1.0 / a
        ap = a
        for _ in range(_MAX_ITER):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) <= abs(total) * _EPS:
                break
        return min(1.0, max(0.0, total * math.exp(-x + a * math.log(x) - math.lgamma(a))))

    # Continued fraction for the upper tail Q(a, x), then complement.
    b = x + 1.0 - a
    c = 1.0 / _FPMIN
    d = 1.0 / max(abs(b), _FPMIN)
    if b < 0:
        d = -d
    h = d
    for i in range(1, _MAX_ITER + 1):
        an = -float(i) * (float(i) - a)
        b += 2.0
        d = an * d + b
        if abs(d) < _FPMIN:
            d = _FPMIN
        c = b + an / c
        if abs(c) < _FPMIN:
            c = _FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) <= _EPS:
            break
    q = math.exp(-x + a * math.log(x) - math.lgamma(a)) * h
    return min(1.0, max(0.0, 1.0 - q))


def _central_survival(x: float, df: int) -> float:
    return 1.0 - _gamma_p(df / 2.0, x / 2.0)


def _central_quantile(probability: float, df: int) -> float:
    """Invert the central chi-square CDF using a bracketed bisection."""
    lo = 0.0
    hi = max(1.0, float(df))
    while _gamma_p(df / 2.0, hi / 2.0) < probability:
        hi *= 2.0
        if math.isinf(hi):
            return hi
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _gamma_p(df / 2.0, mid / 2.0) < probability:
            lo = mid
        else:
            hi = mid
        if hi - lo <= 2.0e-14 * max(1.0, hi):
            break
    return (lo + hi) / 2.0


def _noncentral_survival(x: float, df: int, ncp: float) -> float:
    """Upper tail of a noncentral chi-square via its Poisson mixture."""
    if ncp == 0.0:
        return _central_survival(x, df)
    if math.isinf(ncp):
        return 1.0
    mu = ncp / 2.0
    # At this scale the tail is indistinguishable from one at double precision
    # for finite x; also avoids an impractical mixture with billions of terms.
    if mu > 1.0e8:
        return 1.0

    radius = 12.0 * math.sqrt(mu + 1.0) + 10.0
    low = max(0, int(math.floor(mu - radius)))
    high = int(math.ceil(mu + radius))
    if low == 0:
        weight = math.exp(-mu)
    else:
        weight = math.exp(-mu + low * math.log(mu) - math.lgamma(low + 1.0))

    total_weight = 0.0
    total_tail = 0.0
    for k in range(low, high + 1):
        if k > low:
            weight *= mu / k
        total_weight += weight
        total_tail += weight * _central_survival(x, df + 2 * k)
    # The omitted Poisson tails are far below the precision needed by the CLI.
    if total_weight > 0.0:
        total_tail /= total_weight
    return min(1.0, max(0.0, total_tail))


def _shared(w: float, alpha: float, df: int) -> float:
    if not math.isfinite(w) or w <= 0.0:
        raise ValueError("w must be finite and greater than zero")
    if not math.isfinite(alpha) or not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be between zero and one")
    if df < 1:
        raise ValueError("df must be at least one")
    return _central_quantile(1.0 - alpha, df)


def post_hoc(w: float, alpha: float, n_total: int, df: int) -> dict[str, float | int]:
    """Calculate achieved power for a supplied total sample size."""
    critical = _shared(w, alpha, df)
    if n_total < 2:
        raise ValueError("n_total must be at least two")
    ncp = n_total * w * w
    power = _noncentral_survival(critical, df, ncp)
    return {"ncp": ncp, "critical_chi2": critical, "power": power}


def a_priori(w: float, alpha: float, power: float, df: int) -> dict[str, float | int]:
    """Find the smallest supported integer N attaining the requested power."""
    critical = _shared(w, alpha, df)
    if not math.isfinite(power) or not 0.0 < power < 1.0:
        raise ValueError("power must be between zero and one")

    def achieved(n: int) -> float:
        return _noncentral_survival(critical, df, n * w * w)

    if achieved(2) >= power:
        n = 2
    else:
        lo, hi = 2, 4
        while hi < MAX_SAMPLE_SIZE and achieved(hi) < power:
            lo, hi = hi, min(MAX_SAMPLE_SIZE, hi * 2)
        if achieved(hi) < power:
            raise ArithmeticError("no solution within supported sample-size ceiling")
        while lo + 1 < hi:
            mid = (lo + hi) // 2
            if achieved(mid) >= power:
                hi = mid
            else:
                lo = mid
        n = hi

    ncp = n * w * w
    return {
        "ncp": ncp,
        "critical_chi2": critical,
        "n_total": n,
        "actual_power": achieved(n),
    }
