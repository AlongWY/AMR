import json


def main():
    golds = open("ckpt/gold.mrp").readlines()
    gens = open("ckpt/ucca_source.mrp").readlines()

    for gold, gen in zip(golds, gens):
        gold = json.loads(gold)
        gen = json.loads(gen)

        gold_set = set()
        gold_snt = gold['input']
        for node in gold['nodes']:
            try:
                for anchor in node['anchors']:
                    gold_set.add(gold_snt[anchor['from']:anchor['to']])
            except:
                continue

        gen_set = set()
        gen_snt = gen['input']
        for node in gen['nodes']:
            try:
                for anchor in node['anchors']:
                    gen_set.add(gen_snt[anchor['from']:anchor['to']])
            except:
                continue

        res = gold_set.difference(gen_set)
        if len(res):
            print('gold-gen', res)


if __name__ == '__main__':
    main()
