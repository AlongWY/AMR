import argparse
import json, regex
import stanza


def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str)
    parser.add_argument('--output', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_config()
    nlp = stanza.Pipeline('en', processors='tokenize,lemma,pos,ner')  # initialize English neural pipeline

    NER_MAP = {}
    NER_DICT = {}

    regex_the = regex.compile(r"^the\s*", regex.IGNORECASE)

    with open(args.output, mode='w', encoding='utf-8') as out:
        with open(args.path, encoding='utf-8') as f:
            for line in f:
                tokens = []
                lemmas = []
                pos_tags = []
                ner_tags = []

                sentence_json = json.loads(line)
                snt = sentence_json['input']
                doc = nlp(snt)

                sentence = doc.sentences[0]

                for ner in sentence.ents:
                    text: str
                    ner_type: str
                    ner_type = ner.type
                    if ner_type == 'DATE':
                        continue
                    text = regex.sub(regex_the, '', ner.text)
                    text = regex.sub(r'\s*-\s*', '-', text)

                    ENT_REPLACE = None
                    NER_DICT.setdefault(ner_type, 0)
                    if text not in NER_MAP:
                        num = NER_DICT[ner_type] + 1
                        ENT_REPLACE = f"{ner_type}_{num}"
                        NER_MAP[text] = ENT_REPLACE
                        NER_DICT[ner_type] = num

                    bias = 0
                    for idx, token in enumerate(ner.tokens):
                        idx = idx - bias
                        if idx == 0 and regex_the.fullmatch(token.text) is not None:
                            setattr(token, 'ner', 'O')
                            bias = bias + 1
                            continue
                        if idx == 0:
                            setattr(token, 'ner', ner_type)
                            setattr(token, 'text', ENT_REPLACE)
                        else:
                            setattr(token, 'remove', True)

                for token in sentence.tokens:
                    assert len(token.words) == 1

                    if hasattr(token, 'remove'):
                        continue

                    tokens.append(token.text)
                    ner_tags.append(token.ner)
                    lemmas.append(token.words[0].lemma)
                    pos_tags.append(token.words[0].pos)

                for node in sentence_json['nodes']:
                    if node['label'] != 'name':
                        continue
                    if 'values' not in node:
                        continue
                    value_text = ' '.join(node['values'])
                    if value_text in NER_MAP:
                        node['properties'] = ['ops']
                        node['values'] = [NER_MAP[value_text]]
                        continue
                    else:
                        assert False

                sentence_json['token'] = tokens
                sentence_json['lemmas'] = lemmas
                sentence_json['pos'] = pos_tags
                sentence_json['ner'] = ner_tags
                out.write(json.dumps(sentence_json) + '\n')
