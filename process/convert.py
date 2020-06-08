from argparse import ArgumentParser
from amr_parser.bert_utils import BertEncoderTokenizer
from fast_smatch.amr import AMR
from fast_smatch.fast_smatch import get_amr_json
import penman as pp
import json, re

import os

os.environ.setdefault('CORENLP_HOME', 'stanford-corenlp')

import corenlp


def main(args):
    pattern = re.compile(r'''[\s()":/,\\'#]+''')
    bert_tokenizer = BertEncoderTokenizer.from_pretrained('./bert-base-cased', do_lower_case=False)
    num_sentences = 0
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        with corenlp.CoreNLPClient(annotators="tokenize ner".split()) as client:
            while True:
                amr_data = get_amr_json(bert_tokenizer, f)
                amr_data: dict
                if 'ner' not in amr_data:
                    amr_data.setdefault('ner', [])
                    ann = client.annotate(amr_data['input'], output_format='json')
                    for sentence in ann['sentences']:
                        for tokens in sentence['tokens']:
                            amr_data['ner'].append(tokens['ner'])

                if len(amr_data['ner']) != len(amr_data['token']):
                    assert False

                if amr_data == '' or amr_data is None:
                    break

                amr = AMR.parse_amr_json(amr_data)
                instance_triple, relation_triple = amr.get_triples2()

                concepts = []
                graph = []

                for instance, short, label in instance_triple:
                    concepts.append(label)
                    graph.append((short, instance, label))

                for relation, source, target in relation_triple:
                    target = f"\"{target}\"" if pattern.search(target) else target
                    graph.append((source, relation, target))

                assert len(amr_data['tops']) == 1
                graph = pp.Graph(graph)
                out.write('# ::id ' + amr_data['id'] + '\n')
                out.write('# ::snt ' + amr_data['input'] + '\n')
                out.write('# ::token ' + json.dumps(amr_data['token']) + '\n')
                out.write('# ::lemma ' + json.dumps(amr_data['lemma']) + '\n')
                out.write('# ::upos ' + json.dumps(amr_data['upos']) + '\n')
                out.write('# ::xpos ' + json.dumps(amr_data['xpos']) + '\n')
                out.write('# ::ner ' + json.dumps(amr_data['ner']) + '\n')
                out.write('# ::conc ' + json.dumps(concepts) + '\n')
                out.write(pp.encode(graph) + '\n\n')
                num_sentences += 1
                if num_sentences % 1000 == 0:
                    print(f"Processed {num_sentences} sentences!")


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
