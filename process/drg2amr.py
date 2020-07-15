import re, json
from argparse import ArgumentParser
import penman as pp

from penman import Graph, Triple


def main(args):
    pattern = re.compile(r'''[\s():/,\\#~]+''')
    re_attrs = re.compile(r'''([\w'-~]+)\.(\w+\.\d+)''')
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for idx, line in enumerate(f.readlines()):
            drg_data = json.loads(line)

            concepts = []
            instances = []
            triples = []
            attrs = []

            for node in drg_data['nodes']:
                concepts.append(f"c{node['id']}")
                instance = node.get('label', '[unreal]').strip('\"')
                if re.match(re_attrs, instance):
                    instance = re.sub(re_attrs, r'\1', instance)
                instances.append(instance)

            for edge in drg_data['edges']:
                src = edge['source']
                tgt = edge['target']
                label = edge.get('label', 'link')

                triples.append(Triple(source=f"c{src}", role=label, target=f"c{tgt}"))

            for concept, instance in zip(concepts, instances):
                triples.append(Triple(source=concept, role=':instance', target=instance))

            triples = [Triple(source=source, role=role, target=f"\"{target}\"") \
                           if pattern.search(target) else Triple(source=source, role=role, target=target)
                       for source, role, target in triples]

            top = drg_data['tops'][0]

            id = drg_data['id']
            snt = drg_data['input']
            token = json.dumps(drg_data['token'])
            lemma = json.dumps(drg_data['lemma'])
            upos = json.dumps(drg_data['upos'])
            xpos = json.dumps(drg_data['xpos'])

            graph = Graph(triples, top=f"c{top}", metadata=dict(
                id=id, snt=snt, token=token, lemma=lemma, upos=upos, xpos=xpos
            ))

            graph_en = pp.encode(graph)
            graph_de = pp.decode(graph_en)

            out.write(graph_en + '\n\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
