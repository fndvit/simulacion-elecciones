"""Monte Carlo around the projection: thousands of plausible elections, each with
  1. a national polling error (per party, fat-tailed, plus a shared left/right swing),
  2. a regional (comunidad) and a provincial deviation from each party's territorial profile,
then the same steps as the projection (iterative proportional fitting to the national figures, joint lists,
D'Hondt with the 3 % barrier in each province). Not published: used for the backtest and, later, the forecast.

Everything is vectorised over simulations: arrays are [N sims, P provinces, K parties]."""
import numpy as np

# error parameters (calibrated in backtest.py; see datos/backtest.json)
DEFAULT = dict(
    sigma_ref=2.0,      # points of national error for a party at 30 % on election day
    t_scale=0.0,        # extra variance per day before the vote, relative: var × (1 + t_scale · days)
    rho_bloc=0.0,       # share of a big party's error that is a shared right-vs-left swing
    df=5,               # Student-t degrees of freedom for the national error (fat tails)
    sd_ccaa=0.08,       # sd of log deviation of a party's share in a comunidad from its profile
    sd_prov=0.035,      # sd of log deviation in a province within its comunidad
)


def _t(rng, df, size):
    """unit-variance Student-t draws"""
    if not df: return rng.standard_normal(size)
    return rng.standard_t(df, size) * np.sqrt((df - 2) / df)


def national_draws(rng, S, parties, right, n, days, p):
    """S: national shares (fractions) of the named parties. Returns [n, K] fractions.
    Error sd scales with √(share/0.30); a common swing moves the right bloc against the rest."""
    s = np.array([S[k] for k in parties])
    sd = p['sigma_ref'] / 100 * np.sqrt(s / 0.30) * np.sqrt(1 + p['t_scale'] * days)
    own = _t(rng, p['df'], (n, len(s))) * sd * np.sqrt(1 - p['rho_bloc'])
    sign = np.array([1.0 if k in right else -1.0 for k in parties])
    swing = _t(rng, p['df'], (n, 1)) * sign * sd * np.sqrt(p['rho_bloc'])
    d = own + swing
    d -= d.sum(1, keepdims=True) * s / s.sum()           # what one party gains, others lose
    return np.clip(s + d, 1e-5, None)


def ipf(T, I, vp, blank, otros, iters=60):
    """T [N,K] national targets; I [N,P,K] profiles; vp [P] valid votes; blank, otros [P] fractions.
    Returns shares [N,P,K+1] of the valid vote (last column = otros)."""
    N, P, K = I.shape
    sh = np.concatenate([T[:, None, :] * I, np.broadcast_to(otros[None, :, None], (N, P, 1))], axis=2)
    V = vp.sum(); w = vp[None, :, None] / V
    for _ in range(iters):
        cur = (sh[:, :, :K] * w).sum(1)                     # [N,K]
        f = np.where(cur > 0, T / np.where(cur > 0, cur, 1), 0)
        sh[:, :, :K] *= f[:, None, :]
        sh *= ((1 - blank)[None, :, None] / sh.sum(2, keepdims=True))
    return sh


def dhondt(votes, seats, valid, thr=0.03):
    """votes [N,K] for one province → seats [N,K]"""
    N, K = votes.shape
    v = np.where(votes / valid >= thr, votes, 0)
    q = v[:, :, None] / np.arange(1, seats + 1)[None, None, :]          # [N,K,seats]
    flat = q.reshape(N, -1)
    top = np.argpartition(-flat, seats - 1, axis=1)[:, :seats]
    out = np.zeros((N, K), dtype=np.int16)
    np.add.at(out, (np.repeat(np.arange(N), seats), (top // seats).ravel()), 1)
    return out


def simulate(S, I, prov, parties, right, n=10000, days=0, params=None, lists=(), seed=1, regional=None):
    """S {party: fraction}; I {prov: {party: index}}; prov: list of dicts with id, ca, vp, blank, otros, seats.
    lists: [(src, dst, set(prov ids))] joint lists. regional: parties standing in one comunidad only
    (their comunidad deviation is already their national error, so they get only provincial noise).
    Returns seats [N,P,K], shares [N,P,K+1], national draws [N,K]."""
    p = dict(DEFAULT, **(params or {}))
    rng = np.random.default_rng(seed)
    K, P = len(parties), len(prov)
    T = national_draws(rng, S, parties, right, n, days, p)
    I0 = np.array([[I[pr['id']].get(k, 0.0) for k in parties] for pr in prov])            # [P,K]
    cas = sorted({pr['ca'] for pr in prov}); cix = np.array([cas.index(pr['ca']) for pr in prov])
    reg = np.array([k in (regional or ()) for k in parties])
    e_ca = rng.standard_normal((n, len(cas), K)) * p['sd_ccaa']
    e_ca[:, :, reg] = 0
    e_pr = rng.standard_normal((n, P, K)) * p['sd_prov']
    Isim = I0[None] * np.exp(e_ca[:, cix, :] + e_pr - 0.5 * (p['sd_ccaa'] ** 2 * ~reg + p['sd_prov'] ** 2))
    vp = np.array([pr['vp'] for pr in prov], float)
    blank = np.array([pr['blank'] for pr in prov]); otros = np.array([pr['otros'] for pr in prov])
    sh = ipf(T, Isim, vp, blank, otros)
    for src, dst, where in lists:
        a, b = parties.index(src), parties.index(dst)
        for j, pr in enumerate(prov):
            if pr['id'] in where:
                sh[:, j, b] += sh[:, j, a]; sh[:, j, a] = 0
    seats = np.zeros((n, P, K), dtype=np.int16)
    for j, pr in enumerate(prov):
        seats[:, j, :] = dhondt(sh[:, j, :K] * vp[j], pr['seats'], vp[j])
    return seats, sh, T


def summary(seats, parties, blocs=None, majority=176):
    tot = seats.sum(1)                                                    # [N,K]
    out = {'seats': {}}
    for i, k in enumerate(parties):
        x = tot[:, i]
        if x.max() == 0: continue
        out['seats'][k] = dict(med=int(np.median(x)), mean=round(float(x.mean()), 1), p10=int(np.percentile(x, 10)),
                               p90=int(np.percentile(x, 90)), p2_5=int(np.percentile(x, 2.5)), p97_5=int(np.percentile(x, 97.5)),
                               p_any=round(float((x > 0).mean()), 3))
    for name, ks in (blocs or {}).items():
        x = tot[:, [parties.index(k) for k in ks if k in parties]].sum(1)
        out[name] = dict(med=int(np.median(x)), p10=int(np.percentile(x, 10)), p90=int(np.percentile(x, 90)),
                         p_majority=round(float((x >= majority).mean()), 3))
    return out
