import json
from argparse import ArgumentParser


def main(args):
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for idx, line in enumerate(f.readlines()):
            ucca_data = json.loads(line)
            for edge in ucca_data['edges']:
                edge.pop('attributes', None)
            out.write(json.dumps(ucca_data) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
