import re, json
from argparse import ArgumentParser
from typing import List, Tuple

import penman as pp

from penman import Graph, Triple

from amr_parser import amr


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


def get_anchors(word, snt):
    # snt = snt.lower()
    word = word.lower()

    if len(word) >= 3 and word.startswith('\"') and word.endswith('\"'):
        word = word.strip('\"')

    pattern = re.escape(word)
    for match in re.finditer(f"{pattern}(\\s|$|\\W)", snt):
        return match.start(), match.start() + len(word)

    start = snt.index(word)
    return start, start + len(word)


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

            snt: str
            snt = metadata['snt'].lower()

            nodes = []
            node_map = {}

            for index, (src, role, tgt) in enumerate(ucca1.instances()):
                tgt: str
                node_map[src] = index
                try:
                    start, end = get_anchors(tgt, snt)
                    nodes.append({
                        'id': src,
                        # 'tgt': tgt,
                        "anchors": [{
                            "from": start,
                            "end": end
                        }]
                    })
                except Exception as e:
                    nodes.append({
                        'id': src,
                        # 'tgt': tgt
                    })
                    if tgt != '[unreal]' and tgt != '[multi]':
                        print(tgt)

            edges = []
            for src, role, tgt in ucca1.edges():
                label: str = role[1:]
                edges.append({
                    "source": src,
                    "target": tgt,
                    "label": label
                })

            for src, role, tgt in ucca1.attributes():
                nodes[node_map[src]].setdefault('anchors', [])
                start, end = get_anchors(tgt, snt)
                nodes[node_map[src]]['anchors'].append(
                    {
                        "from": start,
                        "end": end
                    }
                )

            remap = {node['id']: index for index, node in enumerate(nodes)}
            for node in nodes:
                node['id'] = remap[node['id']]
            for edge in edges:
                edge["source"] = remap[edge["source"]]
                edge["target"] = remap[edge["target"]]

            top = remap[ucca1.top]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 1,
                "framework": "ucca",
                "version": 1.0,
                "tops": [top],
                "input": metadata['snt'],
                "time": "2020-04-27",
                "nodes": nodes,
                "edges": edges}) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--extra', '-e', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
