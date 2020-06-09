import json, re
from argparse import ArgumentParser
from collections import defaultdict
from itertools import zip_longest

URL = pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F])|[\-])+')


def clean(word: str):
    word = word.replace('“', "\"") \
        .replace('”', "\"") \
        .replace('’', "'") \
        .replace('‘', "'") \
        .replace('1/2', "½") \
        .replace('1/3', "⅓")
    # word = re.sub(URL, '[URL]', word)
    word = re.sub(r'[–—-]+', '-', word)
    word = re.sub(r'[.…]+', '…', word)
    return word


def main(args):
    res = {}
    with open(args.input, encoding='utf-8') as f, open(args.output, mode='w', encoding='utf-8') as out:
        for line in f.readlines():
            mrp_json = json.loads(line)
            mrp_token = [clean(tok) for tok in mrp_json['tok']]
            src_token = [node['label'] for node in mrp_json['nodes']]
            src_tok = [clean(node) for node in src_token]

            if mrp_token == src_tok:
                continue

            src_tok_set = set(enumerate(src_tok))
            core_tok_Set = set(enumerate(mrp_token))

            difference = list(src_tok_set.difference(core_tok_Set))

            print(difference)

            to_clean = []
            for src_tok, ner_tok, ner in zip_longest(src_token, mrp_json['tok'], mrp_json['ner']):
                to_clean.append({
                    'src_tok': src_tok,
                    'ner_tok': ner_tok,
                    'ner': ner,
                })

            res[mrp_json['id']] = to_clean
        out.write(json.dumps(res, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
