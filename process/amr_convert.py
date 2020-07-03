from argparse import ArgumentParser
from amr_parser.bert_utils import BertEncoderTokenizer
from fast_smatch.amr import AMR
from fast_smatch.fast import get_amr_json
import penman as pp
import json, re

from penman import Graph, Triple


def main(args):
    pattern = re.compile(r'''[\s()":/,\\'#]+''')
    bert_tokenizer = BertEncoderTokenizer.from_pretrained('./bert-base-cased', do_lower_case=False)
    num_sentences = 0
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        while True:
            amr_data = get_amr_json(bert_tokenizer, f)
            if amr_data == '' or amr_data is None:
                break

            amr_nodes = amr_data['nodes']
            amr_edges = amr_data.get('edges', [])

            graph = []
            concepts = []

            for node in amr_nodes:
                short_name = f'c{node["id"]}'
                concept = node["label"]
                concepts.append(concept)
                graph.append((short_name, 'instance', concept))
                for attr, value in zip(node.get('properties', []), node.get('values', [])):
                    value = f"\"{value}\"" if pattern.search(value) else value
                    graph.append((short_name, attr, value))
            for edge in amr_edges:
                src = f'c{edge["source"]}'
                target = f'c{edge["target"]}'
                label = edge["label"]
                target = f"\"{target}\"" if pattern.search(target) else target
                graph.append((src, label, target))

            graph = Graph(graph)

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
