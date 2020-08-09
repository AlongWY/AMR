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
        rule_attr = re.compile(r'''(\d+)''')
        for sent_num, cur_amr1 in enumerate(generate_amr_lines(f), start=1):
            amr = pp.decode(cur_amr1)

            metadata = amr.metadata
            nodes = []
            node_map = {}

            # instances = amr.instances()
            # amr_edges = amr.edges()
            # attributes = amr.attributes()

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

            done_sources = set()
            for src, role, tgt in amr.attributes():
                source = node_map[src]
                label: str = role[1:]

                tgt = tgt.lower().strip("\"")
                if rule_attr.match(tgt) and label == 'polarity':
                    continue
                if rule_attr.match(tgt) and label == 'link':
                    if tgt not in done_sources:
                        done_sources.add(tgt)
                        nodes[source]['label'] = f"{nodes[source]['label']}-{tgt}"
                    continue
                nodes[source].setdefault('properties', [])
                nodes[source].setdefault('values', [])

                nodes[source]['properties'].append(label)
                nodes[source]['values'].append(tgt)

            top = node_map[amr.top]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 2,
                "framework": "amr",
                "language": 'zho',
                "version": 1.1,
                "tops": [top],
                "input": " ".join(json.loads(metadata['snt'])),
                "time": "2020-06-22",
                "nodes": nodes,
                "edges": edges}, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
