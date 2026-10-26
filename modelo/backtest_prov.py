"""Provincial hold-out: how wrong is our territorial profile when the national result is known exactly?
Predict each target election's provincial shares from the earlier elections' profiles (the same method as
projection.py), feeding it the TRUE national shares, and measure the residuals.
Targets: 2023 (from 2019N + 2019A) and 2019N (from 2019A)."""
import json, math, os, statistics as st
from elections import load, dhondt, D

E = {e: load(e) for e in ('g2019a', 'g2019n', 'g2023')}
PROV = sorted(E['g2023'])
W = {'g2023': 0.6, 'g2019n': 0.25, 'g2019a': 0.15}
PARTIES = ['PP', 'PSOE', 'VOX', 'SUM', 'CS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC']


def fam(e, pr):
    f = dict(E[e][pr]['fam']); o = {}
    for k in ['PP', 'PSOE', 'VOX', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'CS']: o[k] = f.get(k, 0)
    if e == 'g2023':
        o['SUM'] = f.get('FA', 0) + f.get('SUMCOMP', 0); o['PP'] += f.get('UPN', 0)
    else:
        o['SUM'] = f.get('UP', 0) + f.get('MP', 0) + f.get('COMP', 0); o['PP'] += f.get('NAPLUS', 0)
    return o


def valid(e, pr):
    p = E[e][pr]; return p['cand'] + p['blank']


def shares(e):
    return {pr: {k: v / valid(e, pr) for k, v in fam(e, pr).items()} for pr in PROV}


def national(e):
    tot = sum(valid(e, pr) for pr in PROV); acc = {}
    for pr in PROV:
        for k, v in fam(e, pr).items(): acc[k] = acc.get(k, 0) + v
    return {k: v / tot for k, v in acc.items()}


def indices(priors):
    I = {}
    nat = {e: national(e) for e in priors}
    for pr in PROV:
        I[pr] = {}
        for P in PARTIES:
            num = den = 0
            for e in priors:
                v = fam(e, pr).get(P, 0)
                if v and nat[e].get(P): num += W[e] * v / valid(e, pr) / nat[e][P]; den += W[e]
            I[pr][P] = num / den if den else 0.0
    return I


def project(S, I, vp, blank, otros, iters=300):
    """S: national shares (fractions of valid vote) of the named parties."""
    V = sum(vp.values())
    Ps = [P for P in S if S[P] > 0]
    sh = {pr: {P: S[P] * I[pr].get(P, 0) for P in Ps} for pr in PROV}
    for pr in PROV: sh[pr]['OTROS'] = otros[pr]
    for _ in range(iters):
        for P in Ps:
            cur = sum(sh[pr][P] * vp[pr] for pr in PROV) / V
            if cur:
                f = S[P] / cur
                for pr in PROV: sh[pr][P] *= f
        for pr in PROV:
            t = sum(sh[pr].values()); tgt = 1 - blank[pr]
            for P in sh[pr]: sh[pr][P] *= tgt / t
    return sh


def run(target, priors):
    last = priors[0]
    vp = {pr: valid(target, pr) for pr in PROV}
    blank = {pr: E[target][pr]['blank'] / valid(target, pr) for pr in PROV}
    otros = {pr: E[last][pr]['otros'] / valid(last, pr) for pr in PROV}
    S = {k: v for k, v in national(target).items() if k in PARTIES}
    I = indices(priors)
    pred = project(S, I, vp, blank, otros)
    act = shares(target)
    seats_p, seats_a, wrong = {}, {}, 0
    for pr in PROV:
        n = E[target][pr]['seats_n']
        sp = dhondt({k: v * vp[pr] for k, v in pred[pr].items() if k != 'OTROS'}, n, vp[pr])
        sa = dhondt({k: v * vp[pr] for k, v in act[pr].items()}, n, vp[pr])
        for k in set(sp) | set(sa): wrong += max(0, sp.get(k, 0) - sa.get(k, 0))
        for k, v in sp.items(): seats_p[k] = seats_p.get(k, 0) + v
        for k, v in sa.items(): seats_a[k] = seats_a.get(k, 0) + v
    return pred, act, vp, seats_p, seats_a, wrong


if __name__ == '__main__':
    out = {}
    for target, priors in (('g2023', ['g2019n', 'g2019a']), ('g2019n', ['g2019a'])):
        pred, act, vp, sp, sa, wrong = run(target, priors)
        print(f'\n== {target} from {priors}: seats moved between parties given the true national vote: {wrong}')
        print('  pred', dict(sorted(sp.items(), key=lambda x: -x[1])))
        print('  real', dict(sorted(sa.items(), key=lambda x: -x[1])))
        # log-ratio residuals, decomposed into region (CCAA) and province parts, vote-weighted
        rows = []
        for pr in PROV:
            for P in PARTIES:
                a, p = act[pr].get(P, 0), pred[pr].get(P, 0)
                if a > 0.01 and p > 0.01:
                    rows.append((pr, E[target][pr]['ca'], P, math.log(p / a), vp[pr] * a, (p - a) * 100))
        res = {}
        for P in PARTIES:
            r = [x for x in rows if x[2] == P]
            if len(r) < 5: continue
            w = sum(x[4] for x in r); m = sum(x[3] * x[4] for x in r) / w
            ca = {}
            for x in r: ca.setdefault(x[1], []).append(x)
            ca_mean = {c: sum(x[3] * x[4] for x in xs) / sum(x[4] for x in xs) for c, xs in ca.items()}
            s_ca = math.sqrt(sum((ca_mean[x[1]] - m) ** 2 * x[4] for x in r) / w)
            s_pr = math.sqrt(sum((x[3] - ca_mean[x[1]]) ** 2 * x[4] for x in r) / w)
            rmse_pts = math.sqrt(sum(x[5] ** 2 * x[4] for x in r) / w)
            res[P] = dict(n=len(r), sd_ccaa=round(s_ca, 3), sd_prov=round(s_pr, 3), rmse_pts=round(rmse_pts, 2))
            print(f'  {P:6s} n={len(r):2d}  sd(log) CCAA {s_ca:.3f}  prov {s_pr:.3f}   RMSE {rmse_pts:.2f} pts')
        out[target] = dict(res=res, wrong=wrong)
    json.dump(out, open(os.path.join(D, 'backtest_prov.json'), 'w'), indent=1)
