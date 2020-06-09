import json
from argparse import ArgumentParser


def main(args):
    with open(args.merge, encoding='utf-8') as f:
        merge = json.load(f)

    with open(args.input, encoding='utf-8') as f, \
            open(args.output, mode='w', encoding='utf-8') as out:
        for line in f.readlines():
            mrp_json = json.loads(line)

            mrp_json.pop('tok')
            ner = mrp_json.pop('ner')

            if mrp_json['id'] in merge:
                ner = [node['ner'] for node in merge[mrp_json['id']]]

            assert len(ner) == len(mrp_json['nodes'])
            for ner, node in zip(ner, mrp_json['nodes']):
                node['properties'].append('ner')
                node['values'].append(ner)
            out.write(json.dumps(mrp_json, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--merge', '-m', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
