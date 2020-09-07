import csv

def read_csv(path):
    with open(path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        # rows = [row for row in reader]
        rows = []
        try:
            for r in reader:
                rows.append(r)
        except UnicodeDecodeError as err:
            print(f'{err}\n last row = {rows[-1]}')
    return rows

def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

ths = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']

pts= ['2pt', '3pt', '4pt']

results = {}
to_csv = [['SCALE', 'TH', 'MAJORITY']]
for pt in pts:
    for th in ths:
        rows = read_csv(f'{pt}_{th}.csv')
        dic = {}
        for r in rows:
            if r['UID'] in dic:
                dic[r['UID']][int(r['ANSWER'])-1] += 1
            else:
                dic[r['UID']] = [0, 0, 0, 0]
                dic[r['UID']][int(r['ANSWER']) - 1] += 1

        unique_m = 0
        tot_m = 0

        for k, v in dic.items():
            m = max(v)
            tot_m += 1
            if v.count(m) == 1:
                unique_m += 1
        to_csv.append([pt, th, unique_m/tot_m])

write_csv('vote_stats.csv', to_csv)

