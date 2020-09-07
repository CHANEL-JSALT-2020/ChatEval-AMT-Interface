import pickle as pkl
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


rows = read_csv('../format/3pt_030820_first_public.csv')

bad_workers = pkl.load(open('bad_workers.pkl', 'rb'))

for th, work in bad_workers.items():
    nrows = [['UID', 'ANSWER', 'ANNOTATOR']]
    for r in rows:
        if r['ANNOTATOR'] not in work:
            nrows.append([r['UID'], r['ANSWER'], r['ANNOTATOR']])
    write_csv(f'3pt_{th}.csv', nrows)