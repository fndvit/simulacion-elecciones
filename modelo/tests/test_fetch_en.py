import datetime as dt, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import fetch_en as EN

# trimmed copy of the English page (revision 1383431757, 2 Nov 2026): the newest table whole, two more in part
HTML = open(os.path.join(os.path.dirname(__file__), 'fixture_en.html')).read()
P = EN.parse(HTML, today=dt.date(2026, 11, 2))
by = {(p['pollster'], p['end']): p for p in P}


def test_rows_and_years():
    assert P[0]['pollster'] == 'SocioMétrica/El Español' and P[0]['end'] == dt.date(2026, 11, 1)
    assert ('40dB/Prisa', dt.date(2026, 1, 5)) in by                       # «29 Dec–5 Jan» ends in January
    assert ('Sigma Dos/El Mundo', dt.date(2025, 12, 29)) in by              # Jan → Dec going down: the year before
    assert not any('election' in p['pollster'].lower() for p in P)


def test_values_sample_source():
    p = by[('SocioMétrica/El Español', dt.date(2026, 11, 1))]
    assert p['n'] == 4893 and p['fw'] == '1 Sep–1 Nov'
    assert by[('40dB/Prisa', dt.date(2026, 1, 5))]['fw'] == '29 Dic–5 Ene'     # Spanish month abbreviations
    v = p['v']
    assert (v['PP'], v['PSOE'], v['VOX'], v['FA'], v['COMP'], v['ERC'], v['PODEMOS'], v['SALF']) == (32.7, 26.6, 19.1, 5.2, 0.9, 2.5, 1.7, 2.5)
    assert v['SUMAR'] is None                                             # FA and Compromís given apart
    assert p['src'].startswith('http')


def test_joint_list_spanning_columns():
    v = by[('IMOP/El Confidencial', dt.date(2026, 10, 16))]['v']           # one figure over FA and FV
    assert v['SUMAR'] == 8.9 and v['FA'] is None and v['COMP'] is None


def test_compare():
    es = dict(pollster='Sigma Dos/El Mundo', end=dt.date(2026, 10, 14), v={'PP': 31.0, 'PSOE': 25.3, 'VOX': 19.5})
    p = by[('Sigma Dos/El Mundo', dt.date(2026, 10, 14))]
    assert EN.compare(p, [es])[0] == 'difiere'                            # PP 31.5 vs 31.0
    es['v'] = {k: p['v'][k] for k in EN.CHECK}
    assert EN.compare(p, [es])[0] == 'coincide'
    es['end'] = dt.date(2026, 10, 15)
    assert EN.compare(p, [es])[0] == 'coincide'                           # ±1 day
    assert EN.compare(by[('The Objective', dt.date(2026, 10, 27))], [es])[0] == 'no figura'


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'): fn(); print('ok', name)
