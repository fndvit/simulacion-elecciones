"""What the simulation says for 29N today (not published). Error sizes pooled from all three backtest elections."""
import json, os, datetime as dt, numpy as np
import backtest as BT, simulacion as SM
import projection as PJ
ALL = list(BT.NAT)
s1, s35 = BT.sigma30(ALL, 1), BT.sigma30(ALL, 35)
sd_ca, sd_pr = BT.prov_sd(list(BT.PROVRES))
P = dict(sigma_ref=s1, size_exp=BT.SIZE_EXP, t_scale=max(0, ((s35 / s1) ** 2 - 1) / 34), rho_bloc=0.3, df=5, sd_ccaa=sd_ca, sd_prov=sd_pr)
app = json.load(open(os.path.join(BT.D, 'app_data.json')))
days = (dt.date(2026, 11, 29) - dt.date.fromisoformat(app['today'])).days
S = {k: v / 100 for k, v in app['S'].items() if k != 'OTROS' and v > 0}
I, _ = PJ.indices(); B = PJ.base_inputs()
prov = [dict(id=pr, ca=B[pr]['ca'], vp=B[pr]['census'] * B[pr]['turnout'] * (1 - B[pr]['nullRate']), blank=B[pr]['blank'],
             otros=B[pr]['otros'], seats=B[pr]['seats']) for pr in PJ.PROV]
parties = list(S)
reg = {'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC', 'UPN', 'AA', 'COMP', 'UPC'}
seats, sh, T = SM.simulate(S, I, prov, parties, {'PP', 'VOX', 'SALF', 'UPN'}, n=20000, days=days, params=P,
                           lists=[(a, b, set(w)) for a, b, w in PJ.LISTS], regional=reg, seed=11)
out = SM.summary(seats, parties, {'PP+VOX+UPN': ['PP', 'VOX', 'UPN'], 'PP': ['PP'],
                                   'PSOE+FA+COMP+PODEMOS+UPC': ['PSOE', 'FA', 'COMP', 'PODEMOS', 'UPC']})
tot = seats.sum(1); ix = {k: i for i, k in enumerate(parties)}
out['p_pp_first'] = round(float((tot[:, ix['PP']] > tot[:, ix['PSOE']]).mean()), 3)
out['params'] = {k: round(v, 3) for k, v in P.items()}; out['days'] = days
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(os.path.join(BT.D, 'sim2026.json'), 'w'), indent=1)
