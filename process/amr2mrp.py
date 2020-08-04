import re, json
from argparse import ArgumentParser
from typing import List, Tuple

import penman as pp

from penman import Graph, Triple

from amr_parser import amr

attr_regex = re.compile(r'''(\w+\.\d+)''')


def generate_amr_lines(f1):
    """
    Read one AMR line at a time from each file handle
    :param f1: file handle (or any iterable of strings) to read AMR 1 lines from
    :param f2: file handle (or any iterable of strings) to read AMR 2 lines from
    :return: generator of cur_amr1, cur_amr2 pairs: one-line AMR strings
    """
    while True:
        cur_amr1 = amr.AMR.get_amr_line(f1)
        if not cur_amr1:
            pass
        else:
            yield cur_amr1
            continue
        break


def main(args):
    with open(args.input, encoding='utf-8') as f, \
            open(args.output, mode='w', encoding='utf-8') as out:
        anr_pair: List[Graph]
        anr_pair = []
        for sent_num, cur_amr1 in enumerate(generate_amr_lines(f), start=1):
            anr_pair.append(pp.decode(cur_amr1))

        for idx, amr in enumerate(anr_pair):
            metadata = amr.metadata
            nodes = []
            node_map = {}

            for index, (src, role, tgt) in enumerate(amr.instances()):
                tgt: str
                node_map[src] = index

                nodes.append({
                    'id': index,
                    "label": tgt
                })

            edges = []
            for src, role, tgt in amr.edges():
                label: str = role[1:]
                source = node_map[src]
                target = node_map[tgt]
                edges.append({
                    "source": source,
                    "target": target,
                    "label": label
                })

            for src, role, tgt in amr.attributes():
                source = node_map[src]
                label: str = role[1:]

                nodes[source].setdefault('properties', [])
                nodes[source].setdefault('values', [])

                nodes[source]['properties'].append(label)
                nodes[source]['values'].append(tgt.lower().strip("\""))

            top = node_map[amr.top]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 2,
                "framework": "amr",
                "version": 1.1,
                "tops": [top],
                "input": metadata['snt'],
                "time": "2020-06-22",
                "nodes": nodes,
                "edges": edges}) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
