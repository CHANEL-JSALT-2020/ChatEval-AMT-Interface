import numpy as np
import csv
import matplotlib.pyplot as plt
import pickle as pkl

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

def mode_per_uid(rows):
    dic = {}
    for r in rows:
        if r['UID'] in dic.keys():
            dic[r['UID']][int(r['ANSWER'])-1] += 1
        else:
            dic[r['UID']] = [0, 0, 0, 0]
            dic[r['UID']][int(r['ANSWER'])-1] += 1

    modes = {}

    for k, v in dic.items():
        modes[k] = np.argmax(v) + 1
    return modes

def compare_workers_mode(rows, mode):
    workers = {}

    for r in rows:
        if r['ANNOTATOR'] in workers.keys():
            if int(r['ANSWER']) != mode[r['UID']]:
                workers[r['ANNOTATOR']][0] += 1
                workers[r['ANNOTATOR']][1] += 1

            else:
                workers[r['ANNOTATOR']][0] += 1

        else:
            if int(r['ANSWER']) != mode[r['UID']]:
                workers[r['ANNOTATOR']] = [1, 1]
            else:
                workers[r['ANNOTATOR']] = [1, 0]

    return workers


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


rows = read_csv('../format/attention_check.csv')

modes = mode_per_uid(rows)
workers = compare_workers_mode(rows, modes)

l = []
for _,v in workers.items():
    l.append(v[1]/v[0])

print(l)
plt.figure(figsize=(8, 6))
plt.hist(l, bins=[0.05*i for i in range(21)])

plt.xlim(left=-0.1, right=1.1)
plt.xlabel('Deviation from Mode frequency')
plt.ylabel('Count of workers')
plt.savefig('histo.png')

l = sorted(l)
print(np.median(l))


erro = [i/10 for i in range(1, 11)]
bad_workers = {}
for err in erro:
    bad_workers[err] = []
    for k,v in workers.items():
        if v[1]/v[0] > err:
            print(k, v[1]/v[0])
            bad_workers[err].append(k)
pkl.dump(bad_workers, open('bad_workers.pkl', 'wb'))

