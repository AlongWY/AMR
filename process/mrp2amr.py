from argparse import ArgumentParser
import penman as pp
import json, re

from penman import Graph


def main(args):
    pattern = re.compile(r'''[\s()":/,\\'#]+''')
    word_attr = re.compile(r'''(\w+)-(\d+)''')
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for amr_data in f.readlines():
            if amr_data == '' or amr_data is None:
                break
            amr_data = json.loads(amr_data)
            amr_nodes = amr_data.pop('nodes')
            amr_edges = amr_data.pop('edges', [])

            triples = []
            concepts = []

            for node in amr_nodes:
                short_name = f'c{node["id"]}'
                concept = node["label"]

                m = word_attr.match(concept)
                if m:
                    concept = m.group(1)
                    attr = m.group(2)
                    triples.append((short_name, 'link', attr))

                if pattern.search(concept):
                    concept = f"\"{concept}\""
                concepts.append(concept)
                triples.append((short_name, 'instance', concept))
                for attr, value in zip(node.get('properties', []), node.get('values', [])):
                    if pattern.search(value):
                        value = f"\"{value}\""
                    triples.append((short_name, attr, value))

            for edge in amr_edges:
                src = f'c{edge["source"]}'
                target = f'c{edge["target"]}'
                label = edge["label"]
                target = f"\"{target}\"" if pattern.search(target) else target
                triples.append((src, label, target))

            top = amr_data.pop('tops')[0]

            # id = amr_data['id']
            # snt = json.dumps(amr_data['input'])
            # token = json.dumps(amr_data['token'])
            # lemma = json.dumps(amr_data['lemma'])
            # upos = json.dumps(amr_data['upos'])
            # xpos = json.dumps(amr_data['xpos'])
            # ner = json.dumps(amr_data['ner'])

            for key, value in amr_data.items():
                amr_data[key] = json.dumps(value, ensure_ascii=False)

            graph = Graph(triples, top=f"c{top}", metadata=amr_data)

            graph_en = pp.encode(graph)
            graph_de = pp.decode(graph_en)

            out.write(graph_en + '\n\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
