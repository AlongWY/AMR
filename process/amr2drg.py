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
            node_map = {}  # concepts to index

            for index, (src, role, tgt) in enumerate(drg.instances()):
                node_map[src] = index
                if len(tgt) >= 3 and tgt.startswith('\"') and tgt.endswith('\"'):
                    tgt = tgt.strip('\"')
                nodes.append({'id': src})
                if tgt != '[unreal]':
                    nodes[-1]['label'] = tgt

            edges = []
            removed_map = {}
            drg_edges = []
            done_set = set()
            for src, role, tgt in drg.edges():
                source_label = nodes[node_map[src]].get('label', None)
                target_label = nodes[node_map[tgt]].get('label', None)
                if source_label and target_label and attr_regex.fullmatch(target_label):
                    if src not in done_set:
                        done_set.add(src)
                        nodes[node_map[src]]['label'] = f"{source_label}.{target_label}"
                        removed_map[tgt] = src
                else:
                    drg_edges.append((src, role, tgt))

            for src, role, tgt in drg_edges:
                label: str = role[1:]
                edges.append({
                    "source": src,
                    "target": tgt
                })
                if label != 'link':
                    edges[-1]['label'] = label
            done_set = set()
            for src, role, tgt in drg.attributes():
                label: str = role[1:]
                src_label = nodes[node_map[src]].get('label', None)
                if label == 'op' and src_label:
                    if attr_regex.fullmatch(tgt) and src not in done_set:
                        done_set.add(src)
                        nodes[node_map[src]]['label'] = f"{src_label}.{tgt}"

            nodes = [node for node in nodes if node['id'] not in removed_map]
            remap = {node['id']: index for index, node in enumerate(nodes)}

            for key, value in remap.items():
                node_map[key] = value

            for node_id, replaced in removed_map.items():
                node_map[node_id] = node_map[replaced]

            for node in nodes:
                node['id'] = node_map[node['id']]
                label = node.get('label', None)
                if not (label is None or re_attrs.fullmatch(label) or label in rule):
                    node['label'] = f"\"{label}\""

            for edge in edges:
                edge["source"] = node_map[edge["source"]]
                edge["target"] = node_map[edge["target"]]

            top = node_map[drg.top]

            out.write(json.dumps({
                "id": metadata['id'],
                "flavor": 2,
                "framework": "drg",
                "language": "deu",
                "version": 1.1,
                "tops": [top],
                "input": " ".join(json.loads(metadata['snt'])),
                "time": "2020-06-16",
                "nodes": nodes,
                "edges": edges}) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--extra', '-e', required=True)
    argparser.add_argument('--output', '-o', required=True)
    argparser.add_argument('--rule', '-r', default='data/drg_deu/drg_no_comma.json')
    args = argparser.parse_args()

    main(args)
