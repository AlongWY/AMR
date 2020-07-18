import re, json
from argparse import ArgumentParser
from itertools import chain
from typing import List, Tuple
from collections import Counter
from networkx import DiGraph

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
    # word = word.lower()
    if len(word) >= 3 and word.startswith('\"') and word.endswith('\"'):
        word = word.strip('\"')

    pattern = re.escape(word)
    for match in re.finditer(f"{pattern}(\\s|$|\\W)", snt):
        return match.start(), match.start() + len(word)

    start = snt.index(word)
    return start, start + len(word)


def get_all_anchors(word: str, snt: str):
    # word = word.lower()
    if len(word) >= 3 and word.startswith('\"') and word.endswith('\"'):
        word = word.strip('\"')

    if word.isalnum():
        pattern = re.escape(word)
        return [(match.start(), match.start() + len(word)) for match in re.finditer(f"{pattern}(\\s|$|\\W)", snt)]
    else:
        pattern = re.escape(word)
        return [(match.start(), match.start() + len(word)) for match in re.finditer(f"{pattern}", snt)]


def distance(cand, anchors):
    start, end = cand

    res = float('inf')
    for anchor in anchors:
        anchor_start = anchor['from']
        anchor_end = anchor['to']

        dis = min(abs(anchor_start - end), abs(anchor_end - start))
        res = min(dis, dis)

    return res


def replace_nearest(node, current, candicates, near_anchors):
    nearest = candicates[0]
    nearest_dis = distance(nearest, near_anchors)

    for cand in candicates[1:]:
        dis = distance(cand, near_anchors)
        if dis < nearest_dis:
            nearest = cand
            nearest_dis = dis

    index = node['anchors'].index(current)

    node['anchors'][index] = {'from': nearest[0], 'to': nearest[1]}


need_fix = []


class Anchor:
    def __init__(self, id, **kwargs):
        self.id = id
        self.dict = kwargs

    def __hash__(self):
        return hash(json.dumps(self.dict))

    def __eq__(self, other):
        if not isinstance(other, Anchor):
            return False
        return hash(self) == hash(other)

    def __str__(self):
        return json.dumps(dict(**self.dict, id=self.id))

    def __repr__(self):
        return json.dumps(dict(**self.dict, id=self.id))


def anchors_fix(mrp: dict):
    snt = mrp['input']
    counter = Counter()
    anchors = [[Anchor(**anchor, id=node['id']) for anchor in node['anchors']] for node in mrp['nodes'] if
               'anchors' in node]
    anchors = list(chain(*anchors))

    counter.update(anchors)
    node_counter = dict()

    for node in anchors:
        node_counter.setdefault(node, [])
        node_counter[node].append(node)

    most = counter.most_common(1)

    if len(most) > 0 and most[0][1] > 1:
        need_fix.append(mrp)

        graph = DiGraph()
        for node in mrp['nodes']:
            graph_node = node.copy()
            id = graph_node.pop('id')
            graph.add_node(id, **graph_node)

        for edge in mrp['edges']:
            graph.add_edge(edge['source'], edge['target'])

        for key, num in counter.items():
            if num < 2:
                continue
            for node in node_counter[key]:
                id = node.id
                start = node.dict['from']
                end = node.dict['to']
                word = snt[start:end]

                all_anchors = get_all_anchors(word, snt)
                if len(all_anchors) == 0:
                    continue

                links = [edge_to for edge_from, edge_to in graph.edges(id)] + \
                        [edge_from for edge_from, edge_to in graph.in_edges(id)]

                same_layer = list(
                    chain(*[[edge_to for edge_from, edge_to in graph.edges(link) if edge_to != id] for link in links]))
                up_layer = list(chain(*[[edge_from for edge_from, edge_to in graph.in_edges(link)] for link in links]))

                near_anchors = list(chain(*[graph.nodes[link]['anchors'] for link in links + same_layer + up_layer if
                                            len(graph.nodes[link])]))

                replace_nearest(mrp['nodes'][id], node.dict, all_anchors, near_anchors)

    return mrp


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

        cnt = 0
        for idx, (ucca1, ucca2) in enumerate(ucca_pair):
            ucca1.metadata.update(ucca2.metadata)
            metadata = ucca1.metadata

            snt: str
            snt = metadata['snt']
            # snt = snt.lower()

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
                            "to": end
                        }]
                    })
                except Exception as e:
                    nodes.append({
                        'id': src,
                        # 'tgt': tgt
                    })
                    if tgt != '[unreal]' and tgt != '[multi]':
                        # print(tgt)
                        cnt += 1

            edges = []
            for src, role, tgt in ucca1.edges():
                label: str = role[1:]

                edges.append({
                    "source": src,
                    "target": tgt,
                    "label": label[0]
                })

                if label.endswith('r'):
                    edges[-1].update({"attributes": ["remote"], "values": [True]})

            for src, role, tgt in ucca1.attributes():
                nodes[node_map[src]].setdefault('anchors', [])
                try:
                    start, end = get_anchors(tgt, snt)
                    nodes[node_map[src]]['anchors'].append(
                        {
                            "from": start,
                            "to": end
                        }
                    )
                except Exception as e:
                    continue

            remap = {node['id']: index for index, node in enumerate(nodes)}
            for node in nodes:
                node['id'] = remap[node['id']]
            for edge in edges:
                edge["source"] = remap[edge["source"]]
                edge["target"] = remap[edge["target"]]

            top = remap[ucca1.top]

            mrp = {
                "id": metadata['id'],
                "flavor": 1,
                "framework": "ucca",
                "version": 1.0,
                "tops": [top],
                "input": metadata['snt'],
                "time": "2020-04-27",
                "nodes": nodes,
                "edges": edges
            }

            mrp = anchors_fix(mrp)

            out.write(json.dumps(mrp) + '\n')

    with open(f"{args.output}_fix", mode='w', encoding='utf-8') as out:
        for mrp in need_fix:
            out.write(json.dumps(mrp) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--extra', '-e', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
