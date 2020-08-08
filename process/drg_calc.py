from collections import Counter, OrderedDict
import json
from os import path
from argparse import ArgumentParser


def main(args):
    comma_counter = Counter()
    no_comma_counter = Counter()
    with open(args.input, encoding='utf-8') as f:
        for idx, line in enumerate(f.readlines()):
            drg_data = json.loads(line)

            for node in drg_data['nodes']:
                instance: str = node.get('label', '[unreal]')

                if instance.startswith("\""):
                    comma_counter.update([instance])
                else:
                    no_comma_counter.update([instance])
    temp = OrderedDict()
    for key, value in comma_counter.most_common():
        temp[key] = value
    with open(path.join(args.output, "drg_comma.json"), mode='w', encoding='utf-8') as f:
        json.dump(temp, f, ensure_ascii=False, indent=2)

    temp = OrderedDict()
    for key, value in no_comma_counter.most_common():
        if "." not in key:
            temp[key] = value
    with open(path.join(args.output, "drg_no_comma.json"), mode='w', encoding='utf-8') as f:
        json.dump(temp, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', default="data/drg_deu")
    args = argparser.parse_args()

    main(args)
