"""National error of our poll average in April 2019, November 2019 and 2023, at several distances from the vote.
Same averaging as polls.py (recency, sample, frequency, house effects); no pollster ratings, since those
come from 2023 itself. Uses only the polls published up to each cut-off."""
import csv, datetime as dt, json, math, os
import polls as PL
import backtest_prov as BP

D = PL.D
COLS = ['PP', 'PSOE', 'VOX', 'SUM', 'CS', 'ERC', 'JUNTS', 'BILDU', 'PNV', 'BNG', 'CC']
EDAY = {'g2019a': dt.date(2019, 4, 28), 'g2019n': dt.date(2019, 11, 10), 'g2023': dt.date(2023, 7, 23)}
DAYS = [56, 35, 21, 7, 1]


def load(e):
    rows = []
    for r in csv.DictReader(open(os.path.join(D, 'hist_polls.csv')), delimiter='|'):
        if r['election'] != e: continue
        rows.append(dict(pollster=r['pollster'], firm=PL.firm(r['pollster']), end=dt.date.fromisoformat(r['end']), fw='',
                         n=int(r['n']) if r['n'] else None, v={k: float(r[k]) if r[k] else None for k in COLS}))
    return rows


def average_at(e, days):
    at = EDAY[e] - dt.timedelta(days=days)
    rows = [r for r in load(e) if r['end'] <= at and (at - r['end']).days <= 120 and not r['firm'].startswith('CIS (')]
    PL.PARTIES = COLS
    he, _ = PL.house_effects(rows)
    avg, _ = PL.average(rows, at=at, he=he, use_rating=False)
    return avg, len([r for r in rows if (at - r['end']).days <= 30])


def result(e):
    return {k: v * 100 for k, v in BP.national(e).items()}


if __name__ == '__main__':
    out = {}
    for e in EDAY:
        res = result(e); out[e] = {'result': {k: round(res.get(k, 0), 2) for k in COLS}}
        print(f'\n== {e}  result', {k: round(res.get(k, 0), 1) for k in COLS})
        for d in DAYS:
            avg, n30 = average_at(e, d)
            err = {k: round(avg[k] - res.get(k, 0), 2) for k in COLS if avg.get(k) is not None}
            out[e][str(d)] = dict(avg={k: round(v, 2) for k, v in avg.items() if v is not None}, err=err, polls30=n30)
            big = [k for k in ('PP', 'PSOE', 'VOX', 'SUM', 'CS') if k in err]
            print(f'  T-{d:2d} ({n30:3d} polls/30d)  ' + '  '.join(f'{k} {err[k]:+.1f}' for k in big)
                  + f'   MAE(big) {sum(abs(err[k]) for k in big) / len(big):.2f}')
    json.dump(out, open(os.path.join(D, 'backtest_nat.json'), 'w'), indent=1)
