import json
from argparse import ArgumentParser


def main(args):
    with open(f"{args.input}.filtered", "w", encoding='utf-8') as out, \
            open(args.input, encoding='utf-8') as file, \
            open(args.extra, encoding='utf-8') as extra:
        for input_sent, extra_sent in zip(file.readlines(), extra.readlines()):
            input_sent = json.loads(input_sent)
            extra_sent = json.loads(extra_sent)

            if "language" in extra_sent:
                input_sent["language"] = extra_sent["language"]
            else:
                input_sent["language"] = 'eng'

            if args.framework in extra_sent["targets"]:
                out.write(json.dumps(input_sent, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--framework', '-f', required=True)
    argparser.add_argument('--extra', '-e', default='data/evaluation/input.mrp')
    args = argparser.parse_args()
    main(args)
