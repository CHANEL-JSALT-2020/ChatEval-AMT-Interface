import pickle as pkl
from xml.etree import ElementTree
import csv
import re
from format import *
import argparse

number = re.compile(r'NUMBER_([0-9]*)')
answer = re.compile(r'ANSWER_([0-9]*)')
att = re.compile(r'ATTENTION-CHECK.*')



def convert(path_pkl, path_out, keep_attention = True, add_hitid=False):

    pik = pkl.load(open(path_pkl, 'rb'))
    #print(pik)
    with open(path_out, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        column_names = ['UID', 'ANSWER', 'ANNOTATOR']
        if add_hitid:
            column_names.append('HITId')
        spamwriter.writerow(column_names)
        workers = {}
        comments = []
        times = [['HITId', 'WorkerId', 'Timer']]
        att_chks = [['UID', 'ANSWER', 'ANNOTATOR']]

        for hit in pik:
            hit_id = None
            for assign in hit['Assignments']:
                hit_id = assign['HITId']

                comments.append(hit_id + '\n')
                worker = assign['WorkerId']
                times.append([hit_id, worker, assign['SubmitTime'] - assign['AcceptTime']])
                root = ElementTree.fromstring(assign['Answer'])
                lis = {}
                for i in range(len(root)):
                    l = []
                    for j in range(len(root[i])):
                        l.append(root[i][j].text)
                    match_n = number.match(l[0])
                    if match_n is not None:
                        if match_n[1] in lis.keys():
                            lis[match_n[1]][0] = l[1] if l[1] != "ATTENTION-CHECK" else f"{l[1]}-{assign['HITId']}-{match_n[1]}"
                        else:
                            lis[match_n[1]] = [l[1] if l[1] != "ATTENTION-CHECK" else f"{l[1]}-{assign['HITId']}-{match_n[1]}", '', worker]
                        if add_hitid:
                            if len(lis[match_n[1]]) < 4:
                                lis[match_n[1]].append(hit_id)
                    else:
                        match_a = answer.match(l[0])
                        if match_a is not None:
                            if match_a[1] in lis.keys():
                                lis[match_a[1]][1] = l[1] if l[1] != "ATTENTION-CHECK" else f"{l[1]}-{assign['HITId']}-{match_a[1]}"
                            else:
                                lis[match_a[1]] = ['', l[1] if l[1] != "ATTENTION-CHECK" else f"{l[1]}-{assign['HITId']}-{match_a[1]}", worker]
                            if add_hitid:
                                if len(lis[match_a[1]]) < 4:
                                    lis[match_a[1]].append(hit_id)
                        else:
                            if l[0] == 'comment':
                                comments.append(f"{worker}, {l[1]}\n")
                            if l[0] == 'participant':
                                workers[worker] = l[1]
                print(lis)

                for k, v in lis.items():
                    if keep_attention:
                        spamwriter.writerow(v)
                    else:
                        m = att.match(v[0])
                        if m is None:
                            spamwriter.writerow(v)
                        else:
                            att_chks.append(v)

        write_csv('attention_check.csv', att_chks)
        f = open(f"comments.txt", 'w')
        f.writelines(comments)
        f.close()
        pkl.dump(workers, open('workers.pkl', 'wb'))
        write_csv('timers.csv', times)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('path_in', type=str, help="Path of the .pkl containing the retrieved hits")
    parser.add_argument('path_out', type=str, help="Path of .csv where the converted data will be written")
    parser.add_argument('-a', '--keep_attention', action='store_true', default=False, help="Whether to keep the attention checks in the output or in a seperate file (default: False, which means attention in a seperate file)")
    parser.add_argument('-i', '--hit_id', action='store_true', default=False, help="Whether to add hit_id to the csv (default : False)")
    args = parser.parse_args()
    convert(args.path_in, args.path_out, keep_attention=args.keep_attention, add_hitid=args.hit_id)