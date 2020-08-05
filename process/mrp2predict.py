from argparse import ArgumentParser
import penman as pp
import json, re

from penman import Graph


def main(args):
    pattern = re.compile(r'''[\s()":/,\\'#]+''')
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for amr_data in f.readlines():
            if amr_data == '' or amr_data is None:
                break
            amr_data = json.loads(amr_data)
            triples = [("c0", ":instance", "none")]

            id = amr_data['id']
            snt = json.dumps(amr_data['input'])
            token = json.dumps(amr_data['token'])
            lemma = json.dumps(amr_data['lemma'])
            upos = json.dumps(amr_data['upos'])
            xpos = json.dumps(amr_data['xpos'])
            ner = json.dumps(amr_data['ner'])

            graph = Graph(triples, metadata=dict(
                id=id, snt=snt, token=token, lemma=lemma, upos=upos, xpos=xpos, ner=ner
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
