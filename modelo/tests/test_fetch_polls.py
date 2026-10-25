import datetime as dt, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import fetch_polls as F

HTML = open(os.path.join(os.path.dirname(__file__), 'fixture_wikipedia.html')).read()
P = F.parse(HTML, today=dt.date(2026, 10, 23))
by = {(p['pollster'], p['end']): p for p in P}


def test_years_and_dates():
    assert ('EM-Analytics/Electomanía', dt.date(2026, 10, 17)) in by
    assert ('EM-Analytics/Electomanía', dt.date(2026, 1, 3)) in by       # «27 Dic–3 Ene» ends in January
    assert ('EM-Analytics/Electomanía', dt.date(2025, 12, 26)) in by     # 2025 table


def test_fa_compromis_split():
    p = by[('EM-Analytics/Electomanía', dt.date(2026, 10, 17))]['v']
    assert p['FA'] == 4.9 and p['COMP'] == 1.3 and p['SUMAR'] is None and p['SALF'] == 1.7


def test_cis_rowspans():
    raw = by[('CIS', dt.date(2026, 10, 6))]
    re_ = by[('CIS (Ateneo Del Dato)', dt.date(2026, 10, 6))]
    assert raw['v']['PSOE'] == 34.0 and raw['v']['PP'] == 22.2 and raw['n'] == 5025
    assert re_['v']['PP'] == 28.3 and re_['v']['PSOE'] == 28.6 and re_['v']['ERC'] is None and re_['v']['PODEMOS'] == 3.0 and re_['v']['SALF'] == 2.4 and re_['v']['AC'] is None
    dec = by[('CIS', dt.date(2025, 12, 5))]                                 # own name, spanned date/sample
    assert dec['v']['PSOE'] == 31.4 and dec['n'] == 4017
    assert by[('CIS (Logoslab)', dt.date(2025, 12, 5))]['v']['PP'] == 28.0


def test_cleaning():
    assert not any(p['pollster'].startswith('Elecciones') for p in P)
    assert sum(1 for p in P if p['pollster'] == '40dB/Prisa') == 1       # the same poll listed twice → kept once
    assert by[('40dB/Prisa', dt.date(2026, 10, 8))]['v']['PP'] == 31.9    # «31.9'» parsed
    assert by[('DYM/Henneo', dt.date(2026, 10, 7))]['v']['SUMAR'] is None  # 18.6 typo dropped
    assert all('Derecha' not in str(p['v']) for p in P)


def test_sources():
    assert by[('EM-Analytics/Electomanía', dt.date(2026, 10, 17))]['src'] == 'https://electomania.es/electopanel-17o/'
    assert by[('Sigma Dos/El Mundo', dt.date(2026, 10, 14))]['src'].startswith('https://www.elmundo.es/')
    assert by[('EM-Analytics/Electomanía', dt.date(2026, 1, 3))]['src'] == ''          # no footnote → empty


if __name__ == '__main__':
    for name, fn in list(globals().items()):
        if name.startswith('test_'): fn(); print('ok', name)
