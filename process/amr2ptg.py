import re, json
from argparse import ArgumentParser
from typing import List, Tuple

import penman as pp

from penman import Graph, Triple

from amr_parser import amr

attr_regex = re.compile(r'''(\w+\.\d+)''')


def generate_amr_lines(f1, f2):
    """
    Read one AMR line at a time from each file handle
    :param f1: file handle (or any iterable of strings) to read AMR 1 lines from
    :param f2: file handle (or any iterable of strings) to read AMR 2 lines from
    :return: generator of cur_amr1, cur_amr2 pairs: one-line AMR strings
    """
    while True:
        cur_amr1 = amr.AMR.get_amr_line(f1)
        cur_amr2 = amr.AMR.get_amr_line(f2)
        if not cur_amr1 and not cur_amr2:
            pass
        else:
            yield cur_amr1, cur_amr2
            continue
        break


def main(args):
    with open(args.input, encoding='utf-8') as f, \
            open(args.extra, encoding='utf-8') as e, \
            open(args.output, mode='w', encoding='utf-8') as out:
        ucca_pair: List[Tuple[Graph, Graph]]
        ucca_pair = []
        for sent_num, (cur_amr1, cur_amr2) in enumerate(generate_amr_lines(f, e), start=1):
            ucca_pair.append(
                (
                    pp.decode(cur_amr1),
                    pp.decode(cur_amr2)
                )
            )

        for idx, (ucca1, ucca2) in enumerate(ucca_pair):
            ucca1.metadata.update(ucca2.metadata)
            metadata = ucca1.metadata

            nodes = []
            node_map = {}

            for index, (src, role, tgt) in enumerate(ucca1.instances()):
                tgt: str
                id_ = int(src[1:])
                node_map[id_] = index
                if len(tgt) >= 3 and tgt.startswith('\"') and tgt.endswith('\"'):
                    tgt = tgt.strip('\"')
                nodes.append({
                    'id': id_
                })

                if tgt != '[unreal]':
                    nodes[-1]['label'] = tgt

            edges = []
            removed_map = {}
            for src, role, tgt in ucca1.edges():
                label: str = role[1:]
                source = int(src[1:])
                target = int(tgt[1:])
                edges.append({
                    "source": source,
                    "target": target
                })

                if label != 'link':
                    edges[-1]['label'] = label

            top = int(ucca1.top[1:])
            nodes = [node for node in nodes if node['id'] not in removed_map]
            remap = {node['id']: index for index, node in enumerate(nodes)}
            top = remap[top]

            for node in nodes:
                node['id'] = remap[node['id']]
            for edge in edges:
                source = removed_map.get(edge["source"], edge["source"])
                target = removed_map.get(edge["target"], edge["target"])

                edge["source"] = remap[source]
                edge["target"] = remap[target]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 1,
                "framework": "ptg",
                "version": 1.0,
                "tops": [top],
                "input": metadata['snt'],
                "time": "2020-06-16",
                "nodes": nodes,
                "edges": edges}) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--extra', '-e', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
