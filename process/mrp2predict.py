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

            if 'tokenization' in amr_data:
                id = amr_data['id']

                tokenization = amr_data['tokenization']
                properties = tokenization[0]['properties']

                snt = json.dumps([token['label'] for token in tokenization], ensure_ascii=False)
                token = json.dumps([token['label'] for token in tokenization], ensure_ascii=False)
                lemma = json.dumps([token['values'][properties.index('lemma')] for token in tokenization],
                                   ensure_ascii=False)
                upos = json.dumps([token['values'][properties.index('upos')] for token in tokenization],
                                  ensure_ascii=False)
                xpos = json.dumps([token['values'][properties.index('xpos')] for token in tokenization],
                                  ensure_ascii=False)
                # ner = json.dumps([token['values'][properties.index('ner')] for token in tokenization], ensure_ascii=False)

                graph = Graph(triples, metadata=dict(
                    id=id, snt=snt, token=token, lemma=lemma, upos=upos, xpos=xpos
                ))
            else:
                id = amr_data['id']
                snt = json.dumps(amr_data['input'], ensure_ascii=False)
                token = json.dumps(amr_data['token'], ensure_ascii=False)
                lemma = json.dumps(amr_data['lemma'], ensure_ascii=False)
                upos = json.dumps(amr_data['upos'], ensure_ascii=False)
                xpos = json.dumps(amr_data['xpos'], ensure_ascii=False)
                ner = json.dumps(amr_data['ner'], ensure_ascii=False)

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
