"""
Quién se suma (o se queda en casa) cuando cambia la participación, provincia a provincia.

Datos: resultados de las generales de julio de 2023 por mesa electoral (Ministerio del Interior,
datos/interior/02202307_MESA.zip; ficheros 03 = candidaturas, 09 = mesas, 10 = votos por mesa).

Idea: la participación no puede subir donde ya roza el techo; los nuevos votantes salen de donde hay
abstención. Y cuando baja, baja sobre todo donde ya era media o baja (un desplazamiento logístico).
  · Sube: los votantes que se suman en cada mesa son proporcionales a su abstención, censo × (1 − t).
  · Baja: los que se quedan en casa son proporcionales a censo × t × (1 − t).
En ambos casos votan (o votaban) como el resto de su mesa. Sumando las mesas de cada provincia sale el
perfil de esos votantes, que se guarda como un multiplicador por partido sobre su voto en la provincia
(×1 = como la media). Los partidos sin equivalente en 2023 (SALF, Adelante Andalucía)
quedan en ×1; los herederos de Sumar (Frente Amplio, Compromís, Podemos) toman el de Sumar.

Uso: from participacion import profiles → ({prov: {'up': {...}, 'down': {...}}}, meta)
"""
import collections, os, zipfile

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'datos')
ZIP = os.path.join(D, 'interior', '02202307_MESA.zip')
# código de la candidatura de cabecera nacional (fichero 03) → familia de 2023
NAT = {'000005': 'PP', '000002': 'PSOE', '000006': 'VOX', '000010': 'SUMAR', '000050': 'ERC', '000057': 'JUNTS', '000071': 'BILDU',
       '000075': 'PNV', '000065': 'BNG', '000031': 'CC', '000074': 'UPN'}
# partido de 2026 → familia de 2023 de la que toma el perfil
HEIR = {'PP': 'PP', 'PSOE': 'PSOE', 'VOX': 'VOX', 'FA': 'SUMAR', 'COMP': 'SUMAR', 'PODEMOS': 'SUMAR', 'UPC': 'SUMAR', 'ERC': 'ERC', 'JUNTS': 'JUNTS',
        'BILDU': 'BILDU', 'PNV': 'PNV', 'BNG': 'BNG', 'CC': 'CC', 'UPN': 'UPN', 'OTROS': 'OTROS', 'BL': 'BLANK'}
MIN_SHARE = 0.002      # por debajo, el partido es demasiado pequeño en la provincia para fiarse: ×1
CLIP = (0.5, 2.0)


def read(path=ZIP):
    with zipfile.ZipFile(path) as z:
        name = lambda k: next(n for n in z.namelist() if os.path.basename(n).startswith(k))
        lines = lambda k: z.read(name(k)).decode('latin-1').splitlines()
        fam = {l[8:14]: NAT.get(l[226:232], 'OTROS') for l in lines('03')}
        M = {}
        for l in lines('09'):
            if l[13:16] == '999': continue                       # voto exterior (CERA)
            census, blank, cand = int(l[30:37]), int(l[65:72]), int(l[79:86])
            if census > 0: M[l[11:23]] = dict(prov=l[11:13], census=census, valid=blank + cand, v=collections.Counter(BLANK=blank))
        for l in lines('10'):
            m = M.get(l[11:23])
            if m: m['v'][fam[l[23:29]]] += int(l[29:36])
    return M


def profiles(path=ZIP):
    M = read(path)
    byp = collections.defaultdict(list)
    for m in M.values(): byp[m['prov']].append(m)
    out = {}
    for p, L in byp.items():
        tot, up, dn = collections.Counter(), collections.Counter(), collections.Counter()
        Wu = Wd = 0.0
        for m in L:
            if not m['valid']: continue
            t = min(0.99, max(0.01, m['valid'] / m['census']))
            wu, wd = m['census'] * (1 - t), m['census'] * t * (1 - t)
            Wu += wu; Wd += wd
            for k, v in m['v'].items():
                s = v / m['valid']
                tot[k] += v; up[k] += wu * s; dn[k] += wd * s
        V = sum(tot.values())
        def ratio(acc, W):
            r = {}
            for k in tot:
                sh = tot[k] / V
                r[k] = 1.0 if sh < MIN_SHARE else min(CLIP[1], max(CLIP[0], (acc[k] / W) / sh))
            return {P: round(r.get(f, 1.0), 4) for P, f in HEIR.items()}
        out[p] = {'up': ratio(up, Wu), 'down': ratio(dn, Wd)}
    meta = dict(fuente='Ministerio del Interior, generales de julio de 2023 por mesa', mesas=len(M))
    return out, meta


if __name__ == '__main__':
    prof, meta = profiles()
    print(meta)
    for p in ['08', '28', '41', '15', '46', '48']:
        print(p, 'sube:', {k: v for k, v in prof[p]['up'].items() if abs(v - 1) > 0.01}, '| baja:', {k: v for k, v in prof[p]['down'].items() if abs(v - 1) > 0.01})
