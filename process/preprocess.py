import json
import stanza

if __name__ == '__main__':
    nlp = stanza.Pipeline('en')  # initialize English neural pipeline
    doc_example = nlp(
        "After its competitor invented the front loading washing machine, the CEO of the American IM company believed that each of its employees had the ability for innovation , and formulated strategic countermeasures for innovation in the industry.")  # run annotation over a sentence

    example = {
        'id': '20001001', 'flavor': 2, 'framework': 'amr', 'version': 1.0, 'time': '2020-04-25', 'source': 'wsj',
        'provenance': 'MRP 2019',
        'input': 'Pierre Vinken, 61 years old, will join the board as a nonexecutive director Nov. 29.',
        'tops': [0],
        'nodes': [
            {'id': 0, 'label': 'join-01'},
            {'id': 1, 'label': 'person'},
            {'id': 2, 'label': 'name', 'properties': ['op1', 'op2'], 'values': ['Pierre', 'Vinken']},
            {'id': 3, 'label': 'temporal-quantity', 'properties': ['quant'], 'values': ['61']},
            {'id': 4, 'label': 'year'},
            {'id': 5, 'label': 'board'},
            {'id': 6, 'label': 'have-org-role-91'},
            {'id': 7, 'label': 'director'},
            {'id': 8, 'label': 'executive', 'properties': ['polarity'], 'values': ['-']},
            {'id': 9, 'label': 'date-entity', 'properties': ['month', 'day'], 'values': ['11', '29']}
        ],
        'edges': [
            {'source': 0, 'target': 9, 'label': 'time'},
            {'source': 1, 'target': 2, 'label': 'name'},
            {'source': 1, 'target': 3, 'label': 'age'},
            {'source': 0, 'target': 1, 'label': 'ARG0'},
            {'source': 5, 'target': 6, 'label': 'ARG1-of', 'normal': 'ARG1'},
            {'source': 0, 'target': 5, 'label': 'ARG1'},
            {'source': 6, 'target': 7, 'label': 'ARG2'},
            {'source': 6, 'target': 1, 'label': 'ARG0'},
            {'source': 7, 'target': 8, 'label': 'mod', 'normal': 'domain'},
            {'source': 3, 'target': 4, 'label': 'unit'}
        ]
    }

    with open('data/mrp/2020/cf/training/amr.mrp', encoding='utf-8') as f:
        tokens = []
        lemmas = []
        pos_tags = []
        ner_tags = []
        for line in f.readlines():
            sentence_json = json.loads(line)
            snt = sentence_json['input']
            doc = nlp(snt)

            print(sentence_json['id'])

            sentence = doc.sentences[0]

            for token in sentence.tokens:
                tokens.append(token.text)
                lemmas.append(token.words[0].lemma)
                ner_tags.append(token.ner)

                pos_tags.append(token.words[0].pos)

            # pass
            break

    # print(doc)
    #
    # pass
