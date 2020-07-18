import re
import json
from argparse import ArgumentParser

re_attrs = re.compile(r'''([\w'-~]+)\.(\w+\.\d+)''')


def main(args):
    with open(args.input, encoding='utf-8') as f:
        with open(args.output, 'w', encoding='utf-8') as output:
            for line in f.readlines():
                data = json.loads(line)
                for node in data['nodes']:
                    instance = node.get('label', None)
                    if instance is None:
                        continue
                    instance = instance.strip('\"')
                    if re.match(re_attrs, instance):
                        node['label'] = re.sub(re_attrs, r'\1', instance)
                    else:
                        node['label'] = instance

                output.write(json.dumps(data) + '\n')


if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('--input', '-i', required=True)
    argparser.add_argument('--output', '-o', required=True)
    args = argparser.parse_args()

    main(args)
