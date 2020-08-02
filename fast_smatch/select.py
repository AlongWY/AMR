# -*- coding: utf-8 -*-
# !/usr/bin/env python

"""
This script computes smatch score between two AMRs.
For detailed description of smatch, see http://www.isi.edu/natural-language/amr/smatch-13.pdf

"""

import sys, argparse, glob
from fast_smatch.amr import AMR
from fast_smatch._smatch import get_best_match, compute_f

# Error log location
ERROR_LOG = sys.stderr

# Debug log location
DEBUG_LOG = sys.stderr


def eval(gold, predict):
    # matching triple number
    total_match_num = 0
    # triple number in test file
    total_test_num = 0
    # triple number in gold file
    total_gold_num = 0
    # sentence number
    sent_num = 1
    # Read amr pairs from two files
    with open(gold, encoding='utf-8') as f0, open(predict, encoding='utf-8') as f1:
        while True:
            cur_amr1 = AMR.get_amr_line(f0)
            cur_amr2 = AMR.get_amr_line(f1)
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

            amr1 = AMR.parse_AMR_line(cur_amr1)
            amr2 = AMR.parse_AMR_line(cur_amr2)
            prefix1 = "a"
            prefix2 = "b"
            # Rename node to "a1", "a2", .etc
            amr1.rename_node(prefix1)
            # Renaming node to "b1", "b2", .etc
            amr2.rename_node(prefix2)
            (instance1, attributes1, relation1) = amr1.get_triples()
            (instance2, attributes2, relation2) = amr2.get_triples()
            (best_mapping, best_match_num) = get_best_match(instance1, attributes1, relation1,
                                                            instance2, attributes2, relation2,
                                                            prefix1, prefix2, verbose=False)
            test_triple_num = len(instance1) + len(attributes1) + len(relation1)
            gold_triple_num = len(instance2) + len(attributes2) + len(relation2)
            total_match_num += best_match_num
            total_test_num += test_triple_num
            total_gold_num += gold_triple_num
            sent_num += 1

    (precision, recall, best_f_score) = compute_f(total_match_num, total_test_num, total_gold_num)
    return best_f_score


def main(args):
    best_f1 = 0.
    best_name = ""
    for filename in glob.glob(f'{args.d}/*_out'):
        f1 = eval(args.g, filename)
        if f1 > best_f1:
            best_f1 = f1
            best_name = filename
        print(filename, "f1:", f1)
    print(best_name)


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Smatch calculator -- arguments")
    parser.add_argument('-g', type=str, required=True, help='Gold AMR.')
    parser.add_argument('-d', type=str, required=True, help='Gold AMR.')
    return parser


if __name__ == "__main__":
    parser = build_arg_parser()
    args = parser.parse_args()
    main(args)
