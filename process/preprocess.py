import argparse
import json
import stanza


def parse_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', type=str)
    parser.add_argument('--output', type=str)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_config()
    nlp = stanza.Pipeline('en', processors='tokenize,lemma')  # initialize English neural pipeline

    with open(args.output, mode='w', encoding='utf-8') as out:
        with open(args.path, encoding='utf-8') as f:
            for line in f.readlines():
                tokens = []
                lemmas = []
                # pos_tags = []
                # ner_tags = []

                sentence_json = json.loads(line)
                snt = sentence_json['input']
                doc = nlp(snt)

                print(sentence_json['id'])

                sentence = doc.sentences[0]

                for token in sentence.tokens:
                    tokens.append(token.text)
                    lemmas.append(token.words[0].lemma)
                    # ner_tags.append(token.ner)
                    # pos_tags.append(token.words[0].pos)

                sentence_json['token'] = tokens
                sentence_json['lemmas'] = lemmas
                out.write(json.dumps(sentence_json) + '\n')
