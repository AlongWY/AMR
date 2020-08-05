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
    re_attrs = re.compile(r'''([\w'-~]+)\.(\w+\.\d+)''')
    with open(args.rule, encoding='utf-8') as f:
        rule = json.load(f)

    with open(args.input, encoding='utf-8') as f, \
            open(args.extra, encoding='utf-8') as e, \
            open(args.output, mode='w', encoding='utf-8') as out:
        drg_pair: List[Tuple[Graph, Graph]]
        drg_pair = []
        for sent_num, (cur_amr1, cur_amr2) in enumerate(generate_amr_lines(f, e), start=1):
            drg_pair.append(
                (
                    pp.decode(cur_amr1),
                    pp.decode(cur_amr2)
                )
            )

        for idx, (drg, extra) in enumerate(drg_pair):
            drg.metadata.update(extra.metadata)
            metadata = drg.metadata

            nodes = []
            node_map = {}

            for index, (src, role, tgt) in enumerate(drg.instances()):
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
            for src, role, tgt in drg.edges():
                label: str = role[1:]
                source = int(src[1:])
                target = int(tgt[1:])
                source_label = nodes[node_map[source]].get('label', None)
                target_label = nodes[node_map[target]].get('label', None)
                if source_label and target_label and label == 'op':
                    if attr_regex.fullmatch(target_label):
                        nodes[node_map[source]]['label'] = f"{source_label}.{target_label}"
                        removed_map[target] = source
                    # else:
                    #     print("not match")
                elif label != 'op' and (target_label is None or not attr_regex.fullmatch(target_label)):
                    edges.append({
                        "source": source,
                        "target": target
                    })

                    if label != 'link':
                        edges[-1]['label'] = label

            for src, role, tgt in drg.attributes():
                label: str = role[1:]
                source = int(src[1:])

                src_label = None
                if 'label' in nodes[node_map[source]]:
                    src_label = nodes[node_map[source]]['label']
                if label == 'op' and src_label:
                    if attr_regex.fullmatch(tgt):
                        nodes[node_map[source]]['label'] = f"{src_label}.{tgt}"

            top = int(drg.top[1:])
            nodes = [node for node in nodes if node['id'] not in removed_map]
            remap = {node['id']: index for index, node in enumerate(nodes)}
            top = remap[top]

            for node in nodes:
                node['id'] = remap[node['id']]
                label = node.get('label', None)
                if not (label is None or re_attrs.fullmatch(label) or label in rule):
                    node['label'] = f"\"{label}\""

            for edge in edges:
                source = removed_map.get(edge["source"], edge["source"])
                target = removed_map.get(edge["target"], edge["target"])

                edge["source"] = remap[source]
                edge["target"] = remap[target]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 2,
                "framework": "drg",
                "version": 1.1,
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
    argparser.add_argument('--rule', '-r', default='data/drg/drg_no_comma.json')
    args = argparser.parse_args()

    main(args)