import datetime as dt, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import fetch_en as EN

HTML = open(os.path.join(os.path.dirname(__file__), 'fixture_en.html')).read()
P = EN.parse(HTML, today=dt.date(2026, 10, 23))


def test_rows_and_years():
    ends = [(p['firm'], p['end']) for p in P]
    assert ('emanalytics', dt.date(2026, 10, 17)) in ends
    assert ('emanalytics', dt.date(2026, 1, 3)) in ends                 # «27 Dec–3 Jan» ends in January
    assert ('emanalytics', dt.date(2025, 12, 26)) in ends                # Jan → Dec going down: the year before
    assert not any('election' in p['pollster'].lower() for p in P)


def test_values_first_line_only():
    p = next(p for p in P if p['firm'] == 'sigmados')
    assert p['v'] == {'PP': 31.9, 'PSOE': 25.3, 'VOX': 19.5, 'SUMAR': 8.1}


def test_compare():
    es = dict(pollster='Sigma Dos/El Mundo', end=dt.date(2026, 10, 14), v={'PP': 31.5, 'PSOE': 25.3, 'VOX': 19.5})
    assert EN.compare(es, P)[0] == 'difiere'                              # PP 31.5 vs 31.9
    es['v']['PP'] = 31.9
    assert EN.compare(es, P)[0] == 'coincide'
    es2 = dict(pollster='EM-Analytics/Electomanía', end=dt.date(2026, 10, 18), v={'PP': 31.8, 'PSOE': 27.1, 'VOX': 18.9})
    assert EN.compare(es2, P)[0] == 'coincide'                            # ±1 day
    es3 = dict(pollster='GAD3/ABC', end=dt.date(2026, 10, 10), v={'PP': 33})
    assert EN.compare(es3, P)[0] == 'no figura'


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'): fn(); print('ok', name)
