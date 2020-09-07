import csv
from nltk.metrics.agreement import AnnotationTask

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




#rows = read_csv('../format/030820_first_public_noatt.csv')
#rows = read_csv('../format/attention_check.csv')

def ordinal(a, b):
    if a > b:
        a, b = b, a
    return (sum([i for i in range(a, b+1)]) - ((a+b)/2))**2


ths = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']

pts= ['2pt', '3pt', '4pt']

results = {}
to_csv = [['SCALE', 'TH', 'MAJORITY']]
for pt in pts:
    for th in ths:
        rows = read_csv(f'{pt}_{th}.csv')
        nrows = [(row['ANNOTATOR'], row['UID'], int(row['ANSWER'])) for row in rows]
        rating_task = AnnotationTask(data=nrows, distance=ordinal)
        to_csv.append([pt, th, rating_task.alpha()])


write_csv('alphas.csv', to_csv)
