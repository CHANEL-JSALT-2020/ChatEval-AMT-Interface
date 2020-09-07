import os, sys
import csv
from nltk.metrics.agreement import AnnotationTask
import numpy as np
import krippendorff
from scipy import stats
import pickle as pkl
import argparse
# np.set_printoptions(threshold=sys.maxsize)


def read_csv(path, dataset=''):
    with open(path, newline='', encoding='utf8') as f:
        reader = csv.DictReader(f)
        # rows = [row for row in reader]
        rows = []
        try:
            for r in reader:
                if dataset and r['UID'].split('-')[0] != dataset:
                    continue
                rows.append(r)
        except UnicodeDecodeError as err:
            print(f'{err}\n last row = {rows[-1]}')
    return rows


def get_annotations_old(rows, nb_turns_per_hit):
    annotations = {}
    for r in rows:
        for i in range(nb_turns_per_hit):
            hit_id = r['HITId']
            uid = r[f'Input.NUMBER_{i+1}']
            id = f'{uid}_{hit_id}'
            rating = r[f'Answer.ANSWER_{i+1}']
            if id in annotations:
                annotations[id].append(rating)
            else:
                annotations[id] = [rating]
    return annotations


def get_annotations(rows, nb_turns_per_hit, wo_attention_check=False):
    if nb_turns_per_hit != 1:
        return get_annotations_old(rows, nb_turns_per_hit)
    annotations = {}
    for r in rows:
        uid = r['UID']
        rating = r['ANSWER']
        if 'ATTENTION-CHECK' in uid and wo_attention_check:
            continue
        if uid in annotations:
            annotations[uid].append(rating)
        else:
            annotations[uid] = [rating]
    return annotations


def get_annotations_per_annotators(rows, wo_attention_check=False, wo_annotator=[]):
    annotations = {}
    annotators = set()
    for r in rows:
        uid = r['UID']
        if 'ATTENTION-CHECK' in uid and wo_attention_check:
            continue
        annotator = r['ANNOTATOR']
        annotators.add(annotator)
        if annotator in wo_annotator:
            # print(f'annotation {uid} from {annotator} removed')
            continue
        rating = r['ANSWER']
        if uid in annotations:
            if annotator in annotations[uid]:
                print(f'{uid} has been annotated multiple times by {annotator}')
            annotations[uid][annotator] = rating
        else:
            annotations[uid] = {annotator: rating}

    print('- Before filtering: -')
    print(f'# of annotations: {len(rows)}')
    print(f'# of annotated turns: {len(annotations)}')
    print(f'# of annotators: {len(annotators)}')

    return annotations


def get_annotator_tab(annotations, nb_min_rating=None):
    if not nb_min_rating:
        all_uid = list(annotations)
    else:
        all_uid = [uid for uid, ratings in annotations.items() if len(ratings) >= nb_min_rating]
    annotators = []
    data = []
    for uid, rating_per_annotator in annotations.items():
        if uid in all_uid:
            for annotator, rating in rating_per_annotator.items():
                if annotator not in annotators:
                    annotators.append(annotator)
                    data.append([None] * len(all_uid))
                data[annotators.index(annotator)][all_uid.index(uid)] = rating
    return data


def annotation_per_annotator2task_data(annotations):
    all_uid = list(annotations)
    annotators = []
    data = []
    task_data = []
    for uid, rating_per_annotator in annotations.items():
        for annotator, rating in rating_per_annotator.items():
            task_data.append([annotator, uid, int(rating)])
    #         if annotator not in annotators:
    #             annotators.append(annotator)
    #             data.append([None]*len(all_uid))
    #         data[annotators.index(annotator)][all_uid.index(uid)] = rating
    #
    # task_data = []
    # for i in range(len(data)):
    #     task_data.extend([str(i), str(j), str(data[i][j]) if data[i][j] else None] for j in range(len(data[i])))

    return task_data


def annotations2task_data(annotations, nb_annotators=None):
    if not nb_annotators:
        return annotation_per_annotator2task_data(annotations)
    data = [[] for _ in range(nb_annotators)]
    for uid, ratings in annotations.items():
        if len(ratings) < nb_annotators:
            print(f'Not enough ratings for {uid}, required: {nb_annotators}, actual: {len(ratings)}')
            continue
        if len(ratings) > nb_annotators:
            print(f'Too much ratings for {uid}, only the first {nb_annotators} are considered (actual: {len(ratings)})')
        for i in range(nb_annotators):
            data[i].append(ratings[i])
    # print(data)

    task_data = []
    for i in range(len(data)):
        task_data.extend([str(i), str(j), str(data[i][j])] for j in range(len(data[i])))

    return task_data


def print_annotation_statistics(annotations):
    annotators = set()
    value_frequency = {}
    nb_annotation_per_turn = {}
    for uid, ratings in annotations.items():
        if isinstance(ratings, list):
            for r in ratings:
                if r in value_frequency:
                    value_frequency[r] += 1
                else:
                    value_frequency[r] = 1
        else:
            for annotator, r in ratings.items():
                annotators.add(annotator)
                if r in value_frequency:
                    value_frequency[r] += 1
                else:
                    value_frequency[r] = 1
        if len(ratings) in nb_annotation_per_turn:
            nb_annotation_per_turn[len(ratings)] += 1
        else:
            nb_annotation_per_turn[len(ratings)] = 1

    print(f'# of annotations: {sum([f for _, f in value_frequency.items()])}')
    print(f'# of annotated turns: {len(annotations)}')
    print(f"# of annotators: {len(annotators) if annotators else 'NA'}")
    print(f'Annotation value frequency: {sorted(value_frequency.items(), key=lambda t: t[0])}')
    print(f'How many turns have been annotated x times: {sorted(nb_annotation_per_turn.items(), key=lambda t: t[0])}')


def ordinal(a, b):
    if a > b:
        a, b = b, a
    return (sum([i for i in range(a, b+1)]) - ((a+b)/2))**2


def compute_agreement(sce_path, nb_turns_per_hit=None, nb_annotators=None, wo_attention_check=False):
    # Compute Kappa coefficient and Krippendorff's alpha with nltk library (https://www.nltk.org/api/nltk.metrics.html)
    rows = read_csv(sce_path)
    if nb_annotators:
        annotations = get_annotations(rows, nb_turns_per_hit, wo_attention_check)
    else:
        annotations = get_annotations_per_annotators(rows, wo_attention_check)
    print_annotation_statistics(annotations)
    task_data = annotations2task_data(annotations, nb_annotators)
    # print(task_data)

    rating_task = AnnotationTask(data=task_data, distance=ordinal)
    print(f"Cohen's Kappa: {rating_task.kappa()}")
    print(f"Fleiss' Kappa: {rating_task.multi_kappa()}")
    print(f"Krippendorff's alpha with ordial metric: {rating_task.alpha()}")


def compute_krippendorff(sce_path, output_path='', wo_attention_check=False, bad_annotators_path='', dataset=''):
    """
    Compute Krippendorff's alpha with krippendorff library
    (https://github.com/pln-fing-udelar/fast-krippendorff/blob/master/sample.py)
    :param sce_path: csv file with columns UID, ANSWER, ANNOTATOR
    :param output_path: path of the output file where the results will be printed (if empty string the results are
    printed in the standart output)
    :param wo_attention_check: if True remove the attention check when computing alpha
    :param bad_annotators_path: path of the pkl file containing for each threshold the list of 'bad' annotators.
    For each threshold remove the annotations of the annotators listed when computing alpha. If empty string no
    annotator's annotation it removed.
    :param dataset: alphanumeric characters identifying the corpus to compute the alpha (if empty string the alpha is
    computed with annotation from all corpora and from attention check)
    """

    if output_path:
        sys.stdout = open(output_path, "w")

    rows = read_csv(sce_path, dataset=dataset)

    bad_annotators_per_th = get_bad_annotators(bad_annotators_path)
    for th, bad_annotators in bad_annotators_per_th.items():
        print(f'--- Threshold {th}---')
        annotations = get_annotations_per_annotators(rows, wo_attention_check=wo_attention_check,
                                                     wo_annotator=bad_annotators)

        print('- After filtering: -')
        print_annotation_statistics(annotations)

        ratings_per_annotator = get_annotator_tab(annotations)

        data = [[np.nan if not r else int(r) for r in ratings] for ratings in ratings_per_annotator]

        print("Krippendorff's alpha for nominal metric: ", krippendorff.alpha(reliability_data=data,
                                                                              level_of_measurement='nominal'))
        print("Krippendorff's alpha for interval metric: ", krippendorff.alpha(reliability_data=data))
        print("Krippendorff's alpha for ordinal metric: ", krippendorff.alpha(reliability_data=data,
                                                                              level_of_measurement='ordinal'))

        # with nltk library
        task_data = annotations2task_data(annotations)
        rating_task = AnnotationTask(data=task_data, distance=ordinal)
        print("Krippendorff's alpha for ordinal metric (nltk): ", rating_task.alpha())


def compute_spearman(sce_path):
    """
    (!) This code is not working with the data from AMT because of missing data (it seems that it needs for each
    annotator pair minimum 3 annotated data)
    data
    :param sce_path:
    """
    rows = read_csv(sce_path)
    annotations = get_annotations_per_annotators(rows)
    print(f'nb annotated turns: {len(annotations)}')
    ratings_per_annotator = get_annotator_tab(annotations, nb_min_rating=3)
    print(f'nb annotators: {len(ratings_per_annotator)}')
    print(f'nb turns annotated at least 3 times: {len(ratings_per_annotator[0])}')

    for ratings_x in ratings_per_annotator[:-1]:
        i_x = ratings_per_annotator.index(ratings_x)
        for ratings_y in ratings_per_annotator[(i_x+1):]:
            if ratings_x == ratings_y:
                continue
            i_y = ratings_per_annotator.index(ratings_y)
            x = np.array([np.nan if not r else int(r) for r in ratings_x])
            y = np.array([np.nan if not r else int(r) for r in ratings_y])
            if np.all(np.isnan(x * y)):
                print(f'spearman corr between {i_x} and {i_y}: NA')
            else:
                rho, pval = stats.spearmanr(x, y, nan_policy='omit')
                print(f'spearman corr between {i_x} and {i_y}: {rho} (pval: {pval})')

    # data = np.array([[np.nan if not r else int(r) for r in ratings] for ratings in ratings_per_annotator]).transpose()
    # # print(data)
    # print(f'matrix shape: {data.shape}')

    # rho, pval = stats.spearmanr(data, axis=0, nan_policy='omit')
    # rho, pval = stats.spearmanr(data, axis=0, nan_policy='propagate')
    # print(f'rho shape: {rho.shape}, pval shape: {pval.shape}')
    # print(f'Spearman rho: {rho}, pval: {pval}')


def get_bad_annotators(path):
    if not path:
        return {1: []}
    f = open(path, 'rb')
    annotator_per_threshold = pkl.load(f)
    return annotator_per_threshold


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("sce", type=str,
                        help="path of the csv file containing the annotations (columns: UID, ANSWER, ANNOTATOR)")
    parser.add_argument("-a", "--wo_attention_check", action="store_true",
                        help="If option used, remove the attention check when performing analysis")
    parser.add_argument("-d", "--dataset", type=str,
                        help="Alphanumeric characters identifying the corpus to perform the analysis (ex: TPCCHT)."
                             "Do not use the option if you want to perform the analysis on all annotations")
    parser.add_argument("-t", "--bad_annotators_path", type=str,
                        help="path of the pkl file containing for each threshold the list of 'bad' annotators.")

    args = parser.parse_args()
    sce = args.sce
    wo_attention_check = args.wo_attention_check
    dataset = args.dataset
    bad_annotators_path = args.bad_annotators_path

    # sce = "C:\\Users\\veron\\Documents\\jsalt\\amt_test\\validity_public\\030820_first_public_finding_atts.csv"
    # wo_attention_check = False
    # dataset = ''    # 'TPCCHT' or 'MPATHY' or ''
    # bad_annotators_path = "C:\\Users\\veron\\Documents\\jsalt\\amt_test\\validity_public\\bad_workers_last.pkl"

    output_file = sce.replace('.csv', '_analysis.txt')
    if wo_attention_check:
        output_file = output_file.replace('.txt', '_wo_attention_check.txt')
    if dataset:
        output_file = output_file.replace('.txt', f'_{dataset}.txt')

    # compute_agreement(sce, nb_turns_per_hit=1, nb_annotators=5, wo_attention_check=wo_attention_check)

    compute_krippendorff(sce, wo_attention_check=wo_attention_check, output_path=output_file, dataset=dataset,
                         bad_annotators_path=bad_annotators_path)

    # compute_spearman(sce)
