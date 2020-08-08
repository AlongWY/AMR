import json
from argparse import ArgumentParser


def main(args):
    with open(f"{args.input}.filtered", "w", encoding='utf-8') as out, \
            open(args.input, encoding='utf-8') as file, \
            open(args.extra, encoding='utf-8') as extra:
        for input_sent, extra_sent in zip(file.readlines(), extra.readlines()):
            extra_sent = json.loads(extra_sent)

            if args.framework in extra_sent["targets"]:
                out.write(input_sent)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--framework', '-f', required=True)
    argparser.add_argument('--extra', '-e', default='data/evaluation/input.mrp')
    args = argparser.parse_args()
    main(args)
