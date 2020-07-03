import re, json
from argparse import ArgumentParser
import penman as pp

from penman import Graph, Triple


def main(args):
    pattern = re.compile(r'''[\s():/,\\#~]+''')
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for idx, line in enumerate(f.readlines()):
            ucca_data = json.loads(line)

            concepts = []
            instances = []
            triples = []

            for node in ucca_data['nodes']:
                concepts.append(f"c{node['id']}")
                anchors = node.get('anchors', None)

                if anchors is not None:
                    instance = [ucca_data['input'][anchor['from']:anchor['to']] for anchor in anchors]
                else:
                    instance = ['[UNREAL]']

                instances.append(instance)

            for edge in ucca_data['edges']:
                src = edge['source']
                tgt = edge['target']
                label = edge['label']

                triples.append(Triple(source=f"c{src}", role=label, target=f"c{tgt}"))

            for concept, instance in zip(concepts, instances):
                if len(instance) == 1:
                    triples.append(Triple(source=concept, role=':instance', target=instance[0]))
                else:
                    triples.append(Triple(source=concept, role=':instance', target='multi'))
                    for idx, value in enumerate(instance):
                        triples.append(Triple(source=concept, role=f':op{idx}', target=value))

            triples = [Triple(source=source, role=role, target=f"\"{target}\"") \
                           if pattern.search(target) else Triple(source=source, role=role, target=target)
                       for source, role, target in triples]

            top = ucca_data['tops'][0]

            id = ucca_data['id']
            snt = ucca_data['input']
            token = json.dumps(ucca_data['token'])
            lemma = json.dumps(ucca_data['lemma'])
            upos = json.dumps(ucca_data['upos'])
            xpos = json.dumps(ucca_data['xpos'])

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
