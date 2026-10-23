import json, os
D = os.path.join(os.path.dirname(__file__), '..', 'datos')
FAM = {
 'g2023': {'PP':['000005','000056','000048'],'PSOE':['000002','000064','000047','000076','000072','000029'],'VOX':['000006'],
   'FA':['000010','000011','000066','000051','000021','000033','000030'],'SUMCOMP':['000082'],'ERC':['000050'],'JUNTS':['000057'],
   'BILDU':['000071'],'PNV':['000075'],'BNG':['000065'],'CC':['000031'],'UPN':['000074'],'AA':['000012']},
 'g2019n': {'PP':['000083','000084','000085','000086'],'PSOE':['000094','000091','000090','000092','000093'],'VOX':['000116'],
   'UP':['000078','000081','000076','000074','000077','000079','000080','000082','000075','000028'],'MP':['000046','000044','000045','000043','000050','000051'],
   'COMP':['000048'],'ERC':['000031'],'JUNTS':['000041'],'BILDU':['000029'],'PNV':['000022'],'BNG':['000010'],'CC':['000013','000054'],'NAPLUS':['000053'],'CS':['000018','000019']},
 'g2019a': {'PP':['000083','000084','000085','000086'],'PSOE':['000096','000093','000092','000094','000097'],'VOX':['000117'],
   'UP':['000077','000081','000076','000075','000080','000078','000079','000082','000074','000032'],'COMP':['000020'],'ERC':['000037'],'JUNTS':['000049'],
   'BILDU':['000033'],'PNV':['000027'],'BNG':['000012'],'CC':['000015'],'NAPLUS':['000052'],'CS':['000022','000023']},
}
def load(e):
    d = json.load(open(os.path.join(D, e + '.json')))
    code2fam = {c: f for f, cs in FAM[e].items() for c in cs}
    out = {}
    for pr, p in d['P'].items():
        fam = {}; other = p['o']
        seats = {}
        for c, v in p['v'].items():
            votes, s = (v, 0) if isinstance(v, int) else v
            f = code2fam.get(c)
            if f is None: other += votes; f2 = 'OTROS'
            else: fam[f] = fam.get(f, 0) + votes; f2 = f
            if s: seats[f2] = seats.get(f2, 0) + s
        out[pr] = dict(name=p['n'], ca=p['ca'], census=p['c'], blank=p['bl'], null=p['nu'], cand=p['cv'], seats_n=p['e'], fam=fam, otros=other, seats=seats,
                       raw={c:(v if isinstance(v,int) else v[0]) for c,v in p['v'].items()}, rawseats={c:v[1] for c,v in p['v'].items() if not isinstance(v,int)}, o=p['o'])
    return out
def dhondt(votes, n, valid, thr=0.03):
    elig = {k: v for k, v in votes.items() if v > 0 and v / valid >= thr}
    q = sorted(((v / d, v, k) for k, v in elig.items() for d in range(1, n + 1)), reverse=True)
    s = {}
    for _, _, k in q[:n]: s[k] = s.get(k, 0) + 1
    return s
