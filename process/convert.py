from amr_parser.bert_utils import BertEncoderTokenizer
from fast_smatch.amr import AMR
from fast_smatch.fast_smatch import get_amr_json
import penman


def main():
    pp = penman.AMRCodec()
    bert_tokenizer = BertEncoderTokenizer.from_pretrained('./bert-base-cased', do_lower_case=False)
    with open('data/amr.dev.json', encoding='utf-8') as f:
        with open('data/amr.dev.convert', mode='w', encoding='utf-8') as out:
            while True:
                amr_data = get_amr_json(bert_tokenizer, f)
                if amr_data == '' or amr_data is None:
                    break
                amr = AMR.parse_amr_json(amr_data)
                instance_triple, relation_triple = amr.get_triples2()

                concepts = []
                graph = []

                for instance, short, label in instance_triple:
                    concepts.append(label)
                    graph.append((short, instance, label))

                for relation, source, target in relation_triple:
                    graph.append((source, relation, target))

                graph = penman.Graph(graph)
                out.write('# ::conc ' + ' '.join(concepts) + '\n')
                out.write(pp.encode(graph) + '\n\n')


if __name__ == '__main__':
    main()
