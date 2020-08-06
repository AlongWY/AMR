import argparse
import json
from collections import defaultdict


def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--companion', type=str)
    parser.add_argument('--path', type=str)
    parser.add_argument('--output', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_config()

    NER_MAP = {}
    NER_DICT = {}

    mrp = {}
    with open(args.companion, mode='r', encoding='utf-8') as companion:
        for line in companion.readlines():
            mrp_json = json.loads(line)
            reformat_json = defaultdict(list)
            for nodes in mrp_json['nodes']:
                reformat_json['token'].append(nodes['label'])
                for proper, value in zip(nodes['properties'], nodes['values']):
                    reformat_json[proper].append(value)
            mrp[mrp_json['id']] = reformat_json

    print("Companion loaded")

    with open(args.output, mode='w', encoding='utf-8') as out:
        with open(args.path, encoding='utf-8') as f:
            for line in f:
                try:
                    sentence_json = json.loads(line)
                    id = sentence_json['id']
                    sentence_json.update(mrp[id])
                    out.write(json.dumps(sentence_json, ensure_ascii=False) + '\n')
                except Exception as e:
                    continue
