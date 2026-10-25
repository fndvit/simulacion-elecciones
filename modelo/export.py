import json, os, datetime as dt
import polls as PL
import transfers as TR
import participacion as TP
from projection import *
I, nat = indices(); B = base_inputs()
rows = PL.load(); he, counts = PL.house_effects(rows)
avg, detail = PL.average(rows, he=he)
mae, rw = PL.ratings()
splits = [r['comp_split'] for r in rows if r['comp_split']]; cs = sum(splits) / len(splits)
def toS(a):
    return {'PP':a['PP'],'PSOE':a['PSOE'],'VOX':a['VOX'],'FA':a['SUMAR']*(1-cs),'COMP':a['SUMAR']*cs,'PODEMOS':a['PODEMOS'],'SALF':a['SALF'],
            'ERC':a['ERC'],'JUNTS':a['JUNTS'],'BILDU':a['BILDU'],'PNV':a['PNV'],'BNG':a['BNG'],'CC':a['CC'],'UPN':a['UPN'],'AA':a['AA'],'AC':a['AC']}
S = toS(avg)
sh, valid_p, S2 = project(S, I, B)
SHORT = {'Alacant/Alicante':'Alicante','Araba/Álava':'Álava','Castelló/Castellón':'Castellón','València/Valencia':'Valencia','Illes Balears':'Illes Balears'}
geo = json.load(open(os.path.join(D, 'geo.json')))
g23 = E['g2023']
prov = []
for pr in PROV:
    b = B[pr]; fv = fam_votes('g2023', pr); v23 = g23[pr]['cand'] + g23[pr]['blank']
    seats23 = {}
    for c, s in g23[pr]['rawseats'].items():
        f = next((k for k, cs_ in __import__('elections').FAM['g2023'].items() if c in cs_), 'OTROS')
        f = 'FA' if f == 'SUMCOMP' else f
        seats23[f] = seats23.get(f, 0) + s
    prov.append(dict(id=pr, n=SHORT.get(b['name'], b['name']), ca=b['ca'], seats=b['seats'], seats23=g23[pr]['seats_n'], census=b['census'],
        t0=round(b['turnout'], 5), nr=round(b['nullRate'], 5), bl=round(b['blank'], 5),
        s={P: round(x, 6) for P, x in sh[pr].items() if x > 1e-6},
        r23={'v': {**{P: round((g23[pr]['fam'].get(P) or 0) / v23, 6) for P in ['PP','PSOE','VOX','ERC','JUNTS','BILDU','PNV','BNG','CC','UPN','AA'] if g23[pr]['fam'].get(P)},
                   'SUMAR': round((g23[pr]['fam'].get('FA', 0) + g23[pr]['fam'].get('SUMCOMP', 0)) / v23, 6), 'OTROS': round(g23[pr]['otros'] / v23, 6)},
             's': seats23, 'valid': v23, 'blank': g23[pr]['blank'], 'null': g23[pr]['null'], 'census': g23[pr]['census']},
        d=geo['p'][pr]['d'], c=geo['p'][pr]['c']))
# poll table (most recent 60) + series
plist = []
for r, w, c in sorted(detail, key=lambda d: d[0]['end'], reverse=True):
    plist.append(dict(p=r['pollster'], f=r['firm'], end=r['end'].isoformat(), fw=r['fw'], n=r['n'], w=round(w, 4),
        c={k: round(v, 3) for k, v in c.items()}, v={k: v for k, v in r['v'].items() if v is not None},
        he={k: round(v, 2) for k, v in he.get(r['firm'], {}).items() if k in ('PP','PSOE','VOX','SUMAR','PODEMOS','SALF') }))
series = []
d = dt.date(2025, 11, 1)
while d <= PL.TODAY:
    a, _ = PL.average([r for r in rows if r['end'] <= d], at=d, he=he)
    series.append(dict(d=d.isoformat(), **{k: round(a[k], 2) for k in ['PP','PSOE','VOX','SUMAR','PODEMOS','SALF'] if a.get(k)}))
    d += dt.timedelta(days=7)
if series[-1]['d'] != PL.TODAY.isoformat():
    series.append(dict(d=PL.TODAY.isoformat(), **{k: round(avg[k], 2) for k in ['PP','PSOE','VOX','SUMAR','PODEMOS','SALF']}))
out = dict(today=PL.TODAY.isoformat(), election='2026-11-29', S={k: round(v, 3) for k, v in S2.items()}, avgRaw={k: round(v, 3) for k, v in avg.items() if v},
    compSplit=round(cs, 3), halfLife=PL.HALF_LIFE, ratings={k: [round(mae[k], 2), round(rw[k], 2)] for k in mae},
    he={f: {k: round(v, 2) for k, v in d_.items()} for f, d_ in he.items()}, heN=counts,
    polls=plist, series=series, prov=prov, geo=dict(W=geo['W'], H=geo['H'], canBox=geo['canBox']),
    wElec=W_ELEC, census=CENSUS_2026)
# where the approved polls come from: the Wikipedia revision read, with the date it was approved
src_path = os.path.join(D, 'fuente.json')
if os.path.exists(src_path): out['fuente'] = json.load(open(src_path))
# vote transfers 2023 → projection: the latest CIS barometer's recall × intention, fitted to each province's totals
tr, trMeta = TR.province_flows(out)[:2]
out['tr'] = tr
out['trMeta'] = {k: trMeta[k] for k in ('study', 'title', 'n')}
# who joins or stays home when turnout changes: abstention geography of the 2023 polling stations
out['tp'], out['tpMeta'] = TP.profiles()
json.dump(out, open(os.path.join(D, 'app_data.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(json.dumps(out, ensure_ascii=False)), len(plist), len(series))
