"""Backtest of the simulation: run the whole model as it would have run 35 days (and 1 day) before the
November 2019 and July 2023 general elections, and check where the real result fell.
Error sizes are calibrated leave-one-out: the test of each election uses only the OTHER elections' errors.
(April 2019 is used for national errors only: its provincial profile would need 2015–2016 results.)"""
import json, math, os, sys
import numpy as np
import backtest_prov as BP, backtest_nat as BN, simulacion as SM

D = BN.D
TARGETS = {'g2019n': ['g2019a'], 'g2023': ['g2019n', 'g2019a']}
REGIONAL = {'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC'}
RIGHT = {'PP', 'VOX', 'CS'}
NOT_RUNNING = {'g2023': {'CS'}}
SIZE_EXP = 0.75
NAT = json.load(open(os.path.join(D, 'backtest_nat.json')))
PROVRES = json.load(open(os.path.join(D, 'backtest_prov.json')))


def sigma30(elections, days):
    """pooled national error (points) of a party at 30 %, from the given elections at that horizon"""
    z = []
    for e in elections:
        x = NAT[e][str(days)]
        for k, err in x['err'].items():
            if k in NOT_RUNNING.get(e, ()) or x['avg'][k] < 0.2: continue
            z.append(err / (x['avg'][k] / 30) ** SIZE_EXP)
    return math.sqrt(np.mean(np.square(z)))


def prov_sd(elections):
    r = [PROVRES[e]['res'][k] for e in elections for k in ('PP', 'PSOE', 'VOX', 'SUM')]
    return float(np.mean([x['sd_ccaa'] for x in r])), float(np.mean([x['sd_prov'] for x in r]))


def params_for(target, days):
    others = [e for e in NAT if e != target]
    s1, s35 = sigma30(others, 1), sigma30(others, 35)
    t_scale = max(0.0, ((s35 / s1) ** 2 - 1) / 34)
    sd_ca, sd_pr = prov_sd([e for e in PROVRES if e != target])
    return dict(sigma_ref=s1, size_exp=SIZE_EXP, t_scale=t_scale, rho_bloc=0.3, df=5, sd_ccaa=sd_ca, sd_prov=sd_pr)


def setup(target, days):
    priors = TARGETS[target]; last = priors[0]
    avg = NAT[target][str(days)]['avg']
    prev = BP.national(last)
    S = {}
    for k in BP.PARTIES:
        if k in NOT_RUNNING.get(target, ()): continue
        v = avg.get(k)
        S[k] = v / 100 if v is not None and v > 0 else prev.get(k, 0)     # not polled → last result
    S = {k: v for k, v in S.items() if v > 0}
    I = BP.indices(priors)
    prov = [dict(id=pr, ca=BP.E[target][pr]['ca'], vp=BP.valid(last, pr), blank=BP.E[last][pr]['blank'] / BP.valid(last, pr),
                 otros=BP.E[last][pr]['otros'] / BP.valid(last, pr), seats=BP.E[target][pr]['seats_n']) for pr in BP.PROV]
    return S, I, prov


def actual(target):
    act = BP.shares(target); out = {}
    for pr in BP.PROV:
        vp = BP.valid(target, pr)
        out[pr] = BP.dhondt({k: v * vp for k, v in act[pr].items()}, BP.E[target][pr]['seats_n'], vp)
    return out


def run(target, days, n=20000, params=None):
    p = params or params_for(target, days)
    S, I, prov = setup(target, days)
    parties = list(S)
    seats, sh, T = SM.simulate(S, I, prov, parties, RIGHT, n=n, days=days, params=p, regional=REGIONAL, seed=7)
    real = actual(target)
    tot = seats.sum(1)
    rows = []
    for i, k in enumerate(parties):
        x = tot[:, i]; a = sum(real[pr].get(k, 0) for pr in BP.PROV)
        pit = float((x < a).mean() + 0.5 * (x == a).mean())
        rows.append(dict(party=k, real=a, med=int(np.median(x)), p10=int(np.percentile(x, 10)), p90=int(np.percentile(x, 90)),
                         p2_5=int(np.percentile(x, 2.5)), p97_5=int(np.percentile(x, 97.5)), pit=round(pit, 3)))
    # provincial: where did each party's real seats fall in its simulated distribution, province by province
    pits = []
    for j, pr in enumerate(BP.PROV):
        for i, k in enumerate(parties):
            x = seats[:, j, i]; a = real[pr].get(k, 0)
            if x.max() == 0 and a == 0: continue
            pits.append(float((x < a).mean() + 0.5 * (x == a).mean()))
    right = [parties.index(k) for k in parties if k in RIGHT]
    rs = tot[:, right].sum(1); ra = sum(real[pr].get(k, 0) for pr in BP.PROV for k in RIGHT)
    return dict(params={k: round(v, 3) if isinstance(v, float) else v for k, v in p.items()}, parties=rows,
                right=dict(real=ra, med=int(np.median(rs)), p10=int(np.percentile(rs, 10)), p90=int(np.percentile(rs, 90)),
                           p_majority=round(float((rs >= 176).mean()), 3)),
                prov_pit=pits)


def report(res):
    for key, r in res.items():
        print(f'\n== {key}   params {r["params"]}')
        print(f'   {"party":6s} real  median   80 % range   95 % range   real at percentile')
        for x in r['parties']:
            flag = '' if 0.1 <= x['pit'] <= 0.9 else ('  (outside 80 %)' if 0.025 <= x['pit'] <= 0.975 else '  (OUTSIDE 95 %)')
            print(f'   {x["party"]:6s} {x["real"]:4d}  {x["med"]:6d}   {x["p10"]:4d}–{x["p90"]:<4d}    {x["p2_5"]:4d}–{x["p97_5"]:<4d}    {x["pit"] * 100:5.1f}{flag}')
        rr = r['right']
        print(f'   right bloc (PP+Vox+Cs): real {rr["real"]}, median {rr["med"]} ({rr["p10"]}–{rr["p90"]}), P(≥176) = {rr["p_majority"]:.0%}')
        pit = np.array(r['prov_pit'])
        print(f'   provincial seat counts: {len(pit)} party-province cells; inside 80 % range: {np.mean((pit >= .1) & (pit <= .9)):.0%}, '
              f'inside 50 %: {np.mean((pit >= .25) & (pit <= .75)):.0%}')


if __name__ == '__main__':
    res = {}
    for target in TARGETS:
        for days in (35, 1):
            res[f'{target} T-{days}'] = run(target, days)
    report(res)
    for r in res.values(): r['prov_pit'] = [round(x, 3) for x in r['prov_pit']]
    json.dump(res, open(os.path.join(D, 'backtest.json'), 'w'), indent=1)
