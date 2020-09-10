import csv
import argparse
import numpy as np


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

def mode_per_uid(rows):
    dic = {}
    for r in rows:
        if r['UID'] in dic.keys():
            dic[r['UID']][int(r['ANSWER'])-1] += 1
        else:
            dic[r['UID']] = [0, 0, 0, 0]
            dic[r['UID']][int(r['ANSWER'])-1] += 1

    modes = {}
    annotations = {}

    for k, v in dic.items():
        annotations[k] = np.argmax(v) + 1
        modes[k] = np.max(v)
    return annotations, modes

def find_disagreement_uids(csv_with_answers, original_csv):
    annotations, modes = mode_per_uid(csv_with_answers)

    new_csv = [['UID', 'SID', 'SEG', 'ANNOTATION', 'MODE']]

    for l in original_csv:
        if l['UID'] in annotations:
            new_csv.append([l['UID'], l['SID'], l['SEG'], annotations[l['UID']], modes[l['UID']]])
        else:
            new_csv.append([l['UID'], l['SID'], l['SEG'], -1, 0])

    return new_csv

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('answers', type=str)
    parser.add_argument('data', type=str)
    args = parser.parse_args()

    csv_with_answers = read_csv(args.answers)
    original_csv = read_csv(args.data)

    disagreement = find_disagreement_uids(csv_with_answers, original_csv)

    write_csv('disagreement.csv', disagreement)
