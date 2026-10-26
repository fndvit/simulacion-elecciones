import json, os, datetime as dt
from elections import load, dhondt, D
import polls as PL

CENSUS_2026 = 38728356
SEATS_2026_CHANGES = {'28': 38, '11': 8}
W_ELEC = {'g2023': 0.6, 'g2019n': 0.25, 'g2019a': 0.15}
CAT = {'08','17','25','43'}; AND = {'04','11','14','18','21','23','29','41'}; VAL = {'03','12','46'}
# parties that do not stand somewhere on 29N (structural zero in the projection)
# Podemos: no list in Catalonia; it backs ERC and has candidates on its lists (pact of 12 Oct 2026)
NOT_RUNNING = {'PODEMOS': CAT}
AA_W = {'11':1.6,'41':1.2,'29':1.0,'18':1.0,'14':0.9,'21':0.9,'23':0.8,'04':0.6}
PARTIES = ['PP','PSOE','VOX','FA','COMP','PODEMOS','SALF','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA','AC']

E = {e: load(e) for e in W_ELEC}
PROV = sorted(E['g2023'])

def fam_votes(e, pr):
    """lineage-mapped family votes for one election/province"""
    p = E[e][pr]; f = dict(p['fam'])
    out = {}
    if e == 'g2023':
        sc = f.get('SUMCOMP', 0)
        for k in ['PP','PSOE','VOX','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA']: out[k] = f.get(k, 0)
        out['FA'] = f.get('FA', 0) + 0.5 * sc
        out['COMP'] = 0.5 * sc
        out['PODEMOS'] = None  # inside Sumar in 2023 → no signal
    else:
        for k in ['PP','PSOE','VOX','ERC','JUNTS','BILDU','PNV','BNG','CC','COMP']: out[k] = f.get(k, 0)
        out['FA'] = f.get('UP', 0) + f.get('MP', 0)
        out['PODEMOS'] = f.get('UP', 0)
        out['UPN'] = None; out['AA'] = None
        if pr == '31': out['PP'] = None  # Navarra Suma (UPN+PP+Cs) in 2019
    return out

def valid(e, pr):
    p = E[e][pr]; return p['cand'] + p['blank']

def indices():
    nat = {}
    for e in W_ELEC:
        tot = sum(valid(e, pr) for pr in PROV); acc = {}
        for pr in PROV:
            for k, v in fam_votes(e, pr).items():
                if v: acc[k] = acc.get(k, 0) + v
        nat[e] = {k: v / tot for k, v in acc.items()}
    I = {}
    for pr in PROV:
        I[pr] = {}
        for P in PARTIES:
            if P in ('SALF','AC','AA'): continue
            num = den = 0; ran_any = False
            vals = {}
            for e, w in W_ELEC.items():
                v = fam_votes(e, pr).get(P)
                if v is None or not nat[e].get(P): continue
                vals[e] = v / valid(e, pr) / nat[e][P]
                if v > 0: ran_any = True
            if not ran_any: I[pr][P] = 0.0; continue
            for e, x in vals.items():
                if x == 0: continue          # didn't stand there that year → treat as missing, not as zero support
                num += W_ELEC[e] * x; den += W_ELEC[e]
            I[pr][P] = num / den if den else 0.0
        I[pr]['SALF'] = 0.5 + 0.5 * I[pr]['VOX']
        I[pr]['AA'] = AA_W.get(pr, 0)
        I[pr]['AC'] = 1.0 if pr in CAT else 0
        for P, where in NOT_RUNNING.items():
            if pr in where: I[pr][P] = 0.0
    return I, nat

def base_inputs():
    g = E['g2023']; tot23 = sum(g[pr]['census'] for pr in PROV); k = CENSUS_2026 / tot23
    out = {}
    for pr in PROV:
        p = g[pr]; votantes = p['cand'] + p['blank'] + p['null']
        out[pr] = dict(name=p['name'], ca=p['ca'], census=round(p['census'] * k), seats=SEATS_2026_CHANGES.get(pr, p['seats_n']),
                       turnout=votantes / p['census'], nullRate=p['null'] / votantes, blank=p['blank'] / (p['cand'] + p['blank']),
                       otros=p['otros'] / (p['cand'] + p['blank']))
    return out

def project(S, I, B, iters=200):
    """S: national targets (% of valid vote) per party. IPF between provincial rows and national columns."""
    valid_p = {pr: B[pr]['census'] * B[pr]['turnout'] * (1 - B[pr]['nullRate']) for pr in PROV}
    V = sum(valid_p.values())
    blank_nat = sum(valid_p[pr] * B[pr]['blank'] for pr in PROV) / V
    S = dict(S); S['OTROS'] = max(0.5, 100 - sum(S.values()) - blank_nat * 100)
    sh = {pr: {P: S[P] / 100 * I[pr][P] for P in PARTIES} for pr in PROV}
    for pr in PROV: sh[pr]['OTROS'] = B[pr]['otros']
    for _ in range(iters):
        for P in list(S):
            cur = sum(sh[pr][P] * valid_p[pr] for pr in PROV) / V
            f = (S[P] / 100) / cur if cur else 0
            for pr in PROV: sh[pr][P] *= f
        for pr in PROV:
            t = sum(sh[pr].values()); target = 1 - B[pr]['blank']
            for P in sh[pr]: sh[pr][P] *= target / t
    return sh, valid_p, S

if __name__ == '__main__':
    I, nat = indices(); B = base_inputs()
    rows = PL.load(); he, counts = PL.house_effects(rows); avg, detail = PL.average(rows, he=he)
    splits = [r['comp_split'] for r in rows if r['comp_split']]; cs = sum(splits) / len(splits)
    S = {'PP':avg['PP'],'PSOE':avg['PSOE'],'VOX':avg['VOX'],'FA':avg['SUMAR']*(1-cs),'COMP':avg['SUMAR']*cs,'PODEMOS':avg['PODEMOS'],
         'SALF':avg['SALF'],'ERC':avg['ERC'],'JUNTS':avg['JUNTS'],'BILDU':avg['BILDU'],'PNV':avg['PNV'],'BNG':avg['BNG'],'CC':avg['CC'],
         'UPN':avg['UPN'],'AA':avg['AA'],'AC':avg['AC']}
    sh, valid_p, S2 = project(S, I, B)
    seats = {}
    for pr in PROV:
        votes = {P: sh[pr][P] * valid_p[pr] for P in sh[pr] if P != 'OTROS'}
        s = dhondt(votes, B[pr]['seats'], valid_p[pr])
        for k, v in s.items(): seats[k] = seats.get(k, 0) + v
    print('S', {k: round(v, 2) for k, v in S2.items()})
    print('seats', dict(sorted(seats.items(), key=lambda x: -x[1])), sum(seats.values()))
    # sanity: replicate 2023 from its own indices
    I23 = {}
    for pr in PROV:
        fv = fam_votes('g2023', pr); I23[pr] = {P: ((fv.get(P) or 0) / valid('g2023', pr)) / (nat['g2023'].get(P) or 1) for P in PARTIES}
    S23 = {P: (nat['g2023'].get(P) or 0) * 100 for P in PARTIES}
    B23 = {pr: dict(B[pr], census=E['g2023'][pr]['census'], seats=E['g2023'][pr]['seats_n']) for pr in PROV}
    sh23, vp23, _ = project(S23, I23, B23)
    seats23 = {}
    for pr in PROV:
        s = dhondt({P: sh23[pr][P] * vp23[pr] for P in PARTIES}, B23[pr]['seats'], vp23[pr])
        for k, v in s.items(): seats23[k] = seats23.get(k, 0) + v
    print('replicated 2023 seats', dict(sorted(seats23.items(), key=lambda x: -x[1])))
    json.dump(dict(I=I, B=B, S=S2, he=he, cs=cs), open(os.path.join(D, 'proj_tmp.json'), 'w'))
