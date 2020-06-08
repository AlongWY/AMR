# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This script computes smatch score between two AMRs.
For detailed description of smatch, see http://www.isi.edu/natural-language/amr/smatch-13.pdf

"""

from . import amr
from amr_parser.bert_utils import BertEncoderTokenizer
import os, sys, json, argparse
from ._smatch import get_best_match, compute_f

# total number of iteration in smatch computation
iteration_num = 5

# verbose output switch.
# Default false (no verbose output)
verbose = False

# single score output switch.
# Default true (compute a single score for all AMRs in two files)
single_score = True

# precision and recall output switch.
# Default false (do not output precision and recall, just output F score)
pr_flag = False

# Error log location
ERROR_LOG = sys.stderr

# Debug log location
DEBUG_LOG = sys.stderr


def get_amr_line(input_f):
    """
    Read the file containing AMRs. AMRs are separated by a blank line.
    Each call of get_amr_line() returns the next available AMR (in one-line form).
    Note: this function does not verify if the AMR is valid

    """
    cur_amr = []
    has_content = False
    for line in input_f:
        line = line.strip()
        if line == "":
            if not has_content:
                # empty lines before current AMR
                continue
            else:
                # end of current AMR
                break
        if line.strip().startswith("#"):
            # ignore the comment line (starting with "#") in the AMR file
            continue
        else:
            has_content = True
            cur_amr.append(line.strip())
    return "".join(cur_amr)


def get_amr_json(bert_tokenizer, input_f):
    for line in input_f:
        line = line.strip()
        if line == '':
            return line
        data = json.loads(line)
        bert_token, token_subword_index = bert_tokenizer.tokenize(data['token'])
        if len(bert_token) > 512:
            print('skip')
            continue
        return data
    return ''


def build_arg_parser():
    """
    Build an argument g_parser using argparse. Use it when python version is 2.7 or later.

    """
    parser = argparse.ArgumentParser(description="Smatch calculator -- arguments")
    parser.add_argument('-f', nargs=2, required=True, type=argparse.FileType('r', encoding='utf-8'),
                        help='Two files containing AMR pairs. AMRs in each file are separated by a single blank line')
    parser.add_argument('-r', type=int, default=4, help='Restart number (Default:4)')
    parser.add_argument('-v', action='store_true', help='Verbose output (Default:false)')
    parser.add_argument('--ms', action='store_true', default=False,
                        help='Output multiple scores (one AMR pair a score)' \
                             'instead of a single document-level smatch score (Default: false)')
    parser.add_argument('--pr', action='store_true', default=False,
                        help="Output precision and recall as well as the f-score. Default: false")
    return parser


def print_alignment(mapping, instance1, instance2):
    """
    print the alignment based on a node mapping
    Args:
        match: current node mapping list
        instance1: nodes of AMR 1
        instance2: nodes of AMR 2

    """
    result = []
    for i, m in enumerate(mapping):
        if m == -1:
            result.append(instance1[i][1] + "(" + instance1[i][2] + ")" + "-Null")
        else:
            result.append(instance1[i][1] + "(" + instance1[i][2] + ")" + "-"
                          + instance2[m][1] + "(" + instance2[m][2] + ")")
    return " ".join(result)


def print_errors(mapping, amr1, amr2, prefix1, prefix2):
    (instance1, attribute1, relation1) = amr1
    (instance2, attribute2, relation2) = amr2

    inst1_match = [False for x in instance1]
    attr1_match = [False for x in attribute1]
    rel1_match = [False for x in relation1]
    inst2_match = [False for x in instance2]
    attr2_match = [False for x in attribute2]
    rel2_match = [False for x in relation2]

    for i in range(0, len(instance1)):
        if mapping[i] != -1:
            if instance1[i][2].lower() == instance2[mapping[i]][2].lower():  # exists a mapping, and the names match
                inst1_match[i] = True
                inst2_match[mapping[i]] = True
            # else:
            # print "Incorrect aligned concept: ", instance1[i][2], "->", instance2[mapping[i]][2].lower()

    for i in range(0, len(attribute1)):
        for j in range(0, len(attribute2)):
            # if both attribute relation triple have the same relation name and value
            if attribute1[i][0].lower() == attribute2[j][0].lower() \
                    and attribute1[i][2].lower() == attribute2[j][2].lower():
                node1_index = int(attribute1[i][1][len(prefix1):])
                node2_index = int(attribute2[j][1][len(prefix2):])
                # if the mapping is correct
                if mapping[node1_index] == node2_index:
                    attr1_match[i] = True
                    attr2_match[j] = True

    for i in range(0, len(relation1)):
        for j in range(0, len(relation2)):
            # if both relations share the same name
            if relation1[i][0].lower() == relation2[j][0].lower():
                node1_index_amr1 = int(relation1[i][1][len(prefix1):])
                node1_index_amr2 = int(relation2[j][1][len(prefix2):])
                node2_index_amr1 = int(relation1[i][2][len(prefix1):])
                node2_index_amr2 = int(relation2[j][2][len(prefix2):])
                # if the mappings are correct
                if mapping[node1_index_amr1] == node1_index_amr2 and mapping[node2_index_amr1] == node2_index_amr2:
                    rel1_match[i] = True
                    rel2_match[j] = True

    # for i in range(0, len(instance1)):
    #    if not inst1_match[i]:
    #        print "Incorrect concept: ", instance1[i][2]
    # for i in range(0, len(instance2)):
    #    if not inst2_match[i]:
    #        print "Missing concept: ", instance2[i][2]
    # for i in range(0, len(attribute1)):
    #    if not attr1_match[i]:
    #        print "Incorrect attribute: ", attribute1[i][0], attribute1[i][2]
    # for i in range(0, len(attribute2)):
    #    if not attr2_match[i]:
    #        print "Missing attribute: ", attribute2[i][0], attribute2[i][2]
    # for i in range(0, len(relation1)):
    #    if not rel1_match[i]:
    #        node1 = int(relation1[i][1][len(prefix1):])
    #        node2 = int(relation1[i][2][len(prefix1):])
    #        print "Incorrect relation: ", instance1[node1][2], ":"+relation1[i][0], instance1[node2][2]
    # for i in range(0, len(relation2)):
    #    if not rel2_match[i]:
    #        node1 = int(relation2[i][1][len(prefix2):])
    #        node2 = int(relation2[i][2][len(prefix2):])
    #        print "Missing relation: ", instance2[node1][2], ":"+relation2[i][0], instance2[node2][2]


def main(arguments):
    """
    Main function of smatch score calculation

    """
    global verbose
    global iteration_num
    global single_score
    global pr_flag
    # set the iteration number
    # total iteration number = restart number + 1
    iteration_num = arguments.r + 1
    if arguments.ms:
        single_score = False
    if arguments.v:
        verbose = True
    if arguments.pr:
        pr_flag = True
    # matching triple number
    total_match_num = 0
    # triple number in test file
    total_test_num = 0
    # triple number in gold file
    total_gold_num = 0
    # sentence number
    sent_num = 1
    # Read amr pairs from two files
    bert_tokenizer = BertEncoderTokenizer.from_pretrained('./bert-base-cased', do_lower_case=False)
    while True:
        cur_amr1 = get_amr_json(bert_tokenizer, args.f[0])
        cur_amr2 = get_amr_line(args.f[1])
        if cur_amr1 == "" and cur_amr2 == "":
            break
        if cur_amr1 == "":
            print("Error: File 1 has less AMRs than file 2", file=ERROR_LOG)
            print("Ignoring remaining AMRs", file=ERROR_LOG)
            break
        if cur_amr2 == "":
            print("Error: File 2 has less AMRs than file 1", file=ERROR_LOG)
            print("Ignoring remaining AMRs", file=ERROR_LOG)
            break

        amr1 = amr.AMR.parse_amr_json(cur_amr1)
        amr2 = amr.AMR.parse_AMR_line(cur_amr2)
        prefix1 = "a"
        prefix2 = "b"
        # Rename node to "a1", "a2", .etc
        amr1.rename_node(prefix1)
        # Renaming node to "b1", "b2", .etc
        amr2.rename_node(prefix2)
        (instance1, attributes1, relation1) = amr1.get_triples()
        (instance2, attributes2, relation2) = amr2.get_triples()
        if verbose:
            # print parse results of two AMRs
            print("AMR pair", sent_num, file=DEBUG_LOG)
            print("============================================", file=DEBUG_LOG)
            print("AMR 1 (one-line):", cur_amr1, file=DEBUG_LOG)
            print("AMR 2 (one-line):", cur_amr2, file=DEBUG_LOG)
            print("Instance triples of AMR 1:", len(instance1), file=DEBUG_LOG)
            print(instance1, file=DEBUG_LOG)
            print("Attribute triples of AMR 1:", len(attributes1), file=DEBUG_LOG)
            print(attributes1, file=DEBUG_LOG)
            print("Relation triples of AMR 1:", len(relation1), file=DEBUG_LOG)
            print(relation1, file=DEBUG_LOG)
            print("Instance triples of AMR 2:", len(instance2), file=DEBUG_LOG)
            print(instance2, file=DEBUG_LOG)
            print("Attribute triples of AMR 2:", len(attributes2), file=DEBUG_LOG)
            print(attributes2, file=DEBUG_LOG)
            print("Relation triples of AMR 2:", len(relation2), file=DEBUG_LOG)
            print(relation2, file=DEBUG_LOG)

        (best_mapping, best_match_num) = get_best_match(instance1, attributes1, relation1,
                                                        instance2, attributes2, relation2,
                                                        prefix1, prefix2, verbose=verbose)
        if verbose:
            print("best match number", best_match_num, file=DEBUG_LOG)
            print("best node mapping", best_mapping, file=DEBUG_LOG)
            print("Best node mapping alignment:", print_alignment(best_mapping, instance1, instance2), file=DEBUG_LOG)
        test_triple_num = len(instance1) + len(attributes1) + len(relation1)
        gold_triple_num = len(instance2) + len(attributes2) + len(relation2)
        print_errors(best_mapping, (instance1, attributes1, relation1), (instance2, attributes2, relation2), prefix1,
                     prefix2)
        if not single_score:
            # if each AMR pair should have a score, compute and output it here
            (precision, recall, best_f_score) = compute_f(best_match_num,
                                                          test_triple_num,
                                                          gold_triple_num,
                                                          verbose)
            # print "Sentence", sent_num
            if pr_flag:
                print("Precision: %.2f" % precision)
                print("Recall: %.2f" % recall)
            print("F1: %.3f" % best_f_score)
        total_match_num += best_match_num
        total_test_num += test_triple_num
        total_gold_num += gold_triple_num
        sent_num += 1
    if verbose:
        print("Total match number, total triple number in AMR 1, and total triple number in AMR 2:", file=DEBUG_LOG)
        print(total_match_num, total_test_num, total_gold_num, file=DEBUG_LOG)
        print("---------------------------------------------------------------------------------", file=DEBUG_LOG)
    # output document-level smatch score (a single f-score for all AMR pairs in two files)
    if single_score:
        (precision, recall, best_f_score) = compute_f(total_match_num, total_test_num, total_gold_num)
        if pr_flag:
            print("Precision: %.3f" % precision)
            print("Recall: %.3f" % recall)
        print("Document F-score: %.3f" % best_f_score)
    args.f[0].close()
    args.f[1].close()


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    main(args)
