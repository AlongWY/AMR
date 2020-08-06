import json
import collections
import argparse
import random
import os


def load_mrp(file):
    mrps = {}
    ids = []
    with open(file, 'r') as fi:
        line = fi.readline().strip()
        while line:
            mrp = json.loads(line, object_pairs_hook=collections.OrderedDict)
            id = mrp["id"]
            if id in mrps:
                print("id: {} occured for more than once!".format(id))
            else:
                ids.append(id)
            mrps[id] = mrp
            line = fi.readline().strip()
    return ids, mrps


def split_mrp(split, ids):
    random.shuffle(ids)
    id_splits = []
    split = [int(i) for i in args.split.split(":")]
    sum_spl = float(sum(split))
    split = [num * i / sum_spl for i in split]
    for i in range(1, len(split)):
        split[i] += split[i - 1]
    split = [0] + split
    # print split
    for i in range(1, len(split)):
        id_splits.append(ids[int(split[i - 1]):int(split[i])])
    return id_splits


def load_ids(idfile):
    id_splits = []
    with open(idfile, 'r') as fi:
        splits_ = fi.read().strip().split('\n\n')
        for split_ in splits_:
            split_ = split_.split('\n')
            print(split_[0])
            id = split_[0].split(' ')[1].split('-')[1]
            assert int(id) == len(id_splits)
            id_splits.append(split_[1:])
    return id_splits


def output_mrp(id_splits, mrps, outfile):
    assert len(id_splits) == 3
    for n_spl, id_split in enumerate(id_splits):
        if n_spl == 0:
            str = 'dev'
        elif n_spl == 1:
            str = 'test'
        elif n_spl == 2:
            str = 'train'
        file = outfile + '-' + str + '.aug.mrp'
        with open(file, 'w') as fo:
            for id in id_split:
                fo.write((json.dumps(mrps[id]) + '\n').encode('utf-8'))


def output_ids(id_splits, idfile):
    with open(idfile, 'w') as fo:
        for n_spl, id_split in enumerate(id_splits):
            fo.write('### Split-' + str(n_spl) + ' (' + str(len(id_split)) + ')\n')
            fo.write('\n'.join(id_split) + '\n\n')


parser = argparse.ArgumentParser(description='Sample Data')
parser.add_argument("input", type=str, help="Input MRP file")
parser.add_argument("--split", type=str, help="Split proportion (seperated by :)")
parser.add_argument("output_dir", type=str, help="Output Augmented file dir")
parser.add_argument("--input_ids", type=str, help="Input instance ids")
parser.add_argument("--output_ids", type=str, help="Output ids")
args = parser.parse_args()

ids, mrps = load_mrp(args.input)
num = len(mrps)
if args.split:
    assert not args.input_ids
    id_splits = split_mrp(args.split, ids)

elif args.input_ids:
    assert not args.split
    id_splits = load_ids(args.input_ids)

print('number of ids in each split: ', ' '.join([str(len(dat)) for dat in id_splits]))

# outfile=os.path.join(args.output_dir, os.path.basename(args.input))
outfile = args.output_dir
output_mrp(id_splits, mrps, outfile)

if args.output_ids:
    output_ids(id_splits, args.output_ids)
