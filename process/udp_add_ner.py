import os
import json
from argparse import ArgumentParser
import corenlp

os.environ.setdefault('CORENLP_HOME', 'stanford-corenlp')


def main(args):
    num_sentences = 0
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        with corenlp.CoreNLPClient(annotators="tokenize ner".split(), endpoint="http://localhost:5000") as client:
            for line in f.readlines():
                mrp_json = json.loads(line)

                ner = []
                ann = client.annotate(mrp_json['input'], output_format='json')
                for sentence in ann['sentences']:
                    for tokens in sentence['tokens']:
                        ner.append(tokens['ner'])
                if len(ner) != len(mrp_json['nodes']):
                    print(mrp_json['id'], " error!")

                mrp_json['ner'] = ner
                # for ner, nodes in zip(ner, mrp_json['nodes']):
                #     nodes['properties'].append('ner')
                #     nodes['values'].append(ner)

                out.write(json.dumps(mrp_json) + '\n')
                num_sentences += 1
                if num_sentences % 1000 == 0:
                    print(f"Processed {num_sentences} sentences!")


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
