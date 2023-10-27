import datetime

source = [
    ("ABSSeq", datetime.date(2023, 3, 1), 3, 13),
    ("ABSSeq", datetime.date(2023, 12, 31), 3, 13),
    ("ABarray", datetime.date(2023, 3, 1), 3, 10),
    ("ABarray", datetime.date(2023, 12, 31), 3, 10),
    ("ACE", datetime.date(2023, 3, 1), 2, 7),
    ("ACE", datetime.date(2023, 12, 31), 2, 7),
    ("ACME", datetime.date(2023, 3, 1), 4, 13),
    ("ACME", datetime.date(2023, 12, 31), 4, 13),
    ("ADAM", datetime.date(2023, 3, 1), 5, 16),
    ("ADAM", datetime.date(2023, 12, 31), 5, 16),
]

# for package, dt, ips, dls in source:
#     year = dt.strftime('%Y')
#     mo = dt.strftime('%b')
    
    
# z = [(dt.strftime('%Y'), dt.strftime('%b')) for package, dt, ips, dls in source]

result = ["Package\tYear\tMonth\tNb_of_distinct_IPs\tNb_of_downloads"]
split = {}
for t in source:
    split.setdefault(t[0], []).append(t[1:])
    
for k, v in split.items():
    print(k)
    dates = set([u[0] for u in v])
    y0 = min(dates).year
    y1 = max(dates).year
    holes = set([datetime.date(y, m + 1, 1) for y in range(y0, y1 + 1) for m in range(12)]) - dates
    out = sorted(v + [(w, 0, 0) for w in holes])
    result.append('\n'.join([f"{k}\t{dt.year}\t{dt.strftime('%b') if dt.day == 1 else 'all'}\t{ip}\t{dl}" for dt, ip, dl in out]))


final = "\n".join(result)
print(final)
