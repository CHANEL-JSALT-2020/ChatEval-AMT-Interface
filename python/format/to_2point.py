import csv
import argparse
import os


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


def to_npoints(rows, dict):
    nrows = []
    for r in rows:
        nrows.append([r['UID'], dict[r['ANSWER']],r['ANNOTATOR']])
    return nrows



dico_2pt = {'1':'1',
            '2':'1',
            '3':'2',
            '4':'2'}
dico_3pt = {'1':'1',
            '2':'2',
            '3':'2',
            '4':'3'}

parser = argparse.ArgumentParser()
parser.add_argument('path_in', type=str, help="Path of the csv to combine in to 3pt and 2pt")
parser.add_argument('path_out', type=str, help="folder in which to write")
args = parser.parse_args()

rows = read_csv(args.path_in)

rows2 = [['UID', 'ANSWER', 'ANNOTATOR']]
rows2.extend(to_npoints(rows, dico_2pt))
write_csv(os.path.join(args.path_out, f'2pt_{os.path.basename(args.path_in)}'), rows2)

rows3 = [['UID', 'ANSWER', 'ANNOTATOR']]
rows3.extend(to_npoints(rows, dico_3pt))
write_csv(os.path.join(args.path_out, f'3pt_{os.path.basename(args.path_in)}'), rows3)