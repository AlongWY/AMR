import torch, logging, time

from amr_parser.data import Vocab, DataLoader, DUM, END, CLS, NIL
from amr_parser.parser import Parser
from amr_parser.postprocess import PostProcessor
from amr_parser.extract import LexicalMap
from amr_parser.utils import move_to_device
from amr_parser.bert_utils import BertEncoderTokenizer, BertEncoder

import argparse, os, re

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('work.log'))


def parse_config():
    parser = argparse.ArgumentParser()

    parser.add_argument('--load_path', type=str, default='amr_ckpt/epoch535_batch154999')
    parser.add_argument('--test_data', type=str, default='data/amr/amr.test.convert.input_clean.recategorize.nosense')
    parser.add_argument('--test_batch_size', type=int, default=4444)
    parser.add_argument('--beam_size', type=int, default=8)
    parser.add_argument('--alpha', type=float, default=0.6)
    parser.add_argument('--max_time_step', type=int, default=100)
    parser.add_argument('--output_suffix', type=str, default='eval_test')
    parser.add_argument('--device', type=int, default=0)

    return parser.parse_args()


def show_progress(model, dev_data):
    model.eval()
    loss_acm = 0.
    for batch in dev_data:
        batch = move_to_device(batch, model.device)
        concept_loss, arc_loss, rel_loss = model(batch)
        loss = concept_loss + arc_loss + rel_loss
        loss_acm += loss.item()
    print('total loss', loss_acm)
    return loss_acm


def parse_batch(model, batch, beam_size, alpha, max_time_step):
    res = dict()
    concept_batch = []
    relation_batch = []
    beams = model.work(batch, beam_size, max_time_step)
    score_batch = []
    for beam in beams:
        best_hyp = beam.get_k_best(1, alpha)[0]
        predicted_concept = [token for token in best_hyp.seq[1:-1]]
        predicted_rel = []
        for i in range(len(predicted_concept)):
            if i == 0:
                continue
            arc = best_hyp.state_dict['arc_ll%d' % i].squeeze_().exp_()[1:]  # head_len
            rel = best_hyp.state_dict['rel_ll%d' % i].squeeze_().exp_()[1:, :]  # head_len x vocab
            for head_id, (arc_prob, rel_prob) in enumerate(zip(arc.tolist(), rel.tolist())):
                predicted_rel.append((i, head_id, arc_prob, rel_prob))
        concept_batch.append(predicted_concept)
        score_batch.append(best_hyp.score)
        relation_batch.append(predicted_rel)
    res['concept'] = concept_batch
    res['score'] = score_batch
    res['relation'] = relation_batch
    return res


def parse_data(model, pp, data, input_file, output_file, beam_size=8, alpha=0.6, max_time_step=100, logger=None):
    tot = 0
    with open(output_file, 'w', encoding='utf-8') as fo:
        for batch in data:
            batch = move_to_device(batch, model.device)
            res = parse_batch(model, batch, beam_size, alpha, max_time_step)
            for concept, relation, score in zip(res['concept'], res['relation'], res['score']):
                fo.write('# ::conc ' + ' '.join(concept) + '\n')
                fo.write('# ::score %.6f\n' % score)
                fo.write(pp.postprocess(concept, relation) + '\n\n')
                tot += 1
    # match(output_file, input_file)
    if logger is None:
        print('write down %d amrs' % tot)
    else:
        logger.info(print('write down %d amrs' % tot))


def load_ckpt_without_bert(model, test_model, device):
    ckpt = torch.load(test_model, map_location=device)['model']
    for k, v in model.state_dict().items():
        if k.startswith('bert_encoder'):
            ckpt[k] = v
    model.load_state_dict(ckpt)


if __name__ == "__main__":
    args = parse_config()
    test_models = []
    if torch.cuda.is_available():
        device = torch.device('cuda')
    else:
        device = torch.device('cpu')

    if os.path.isdir(args.load_path):
        for file in os.listdir(args.load_path):
            fname = os.path.join(args.load_path, file)
            if os.path.isfile(fname):
                test_models.append(fname)
        model_args = torch.load(fname, map_location=device)['args']
    else:
        test_models.append(args.load_path)
        model_args = torch.load(args.load_path, map_location=device)['args']

    vocabs = dict()
    vocabs['tok'] = Vocab(model_args.tok_vocab, 5, [CLS])
    vocabs['lem'] = Vocab(model_args.lem_vocab, 5, [CLS])
    vocabs['upos'] = Vocab(model_args.upos_vocab, 5, [CLS])
    vocabs['ner'] = Vocab(model_args.ner_vocab, 1, [CLS])
    vocabs['lem_char'] = Vocab(model_args.lem_vocab, 5, [CLS])
    vocabs['concept'] = Vocab(model_args.concept_vocab, 5, [DUM, END])
    vocabs['predictable_concept'] = Vocab(model_args.predictable_concept_vocab, 5, [DUM, END])

    vocabs['rel'] = Vocab(model_args.rel_vocab, 50, [NIL])

    vocabs['tok_char'] = Vocab(model_args.tok_char_vocab, 100, [CLS, END])
    vocabs['concept_char'] = Vocab(model_args.concept_char_vocab, 100, [CLS, END])
    lexical_mapping = LexicalMap()

    bert_tokenizer = BertEncoderTokenizer.from_pretrained(model_args.bert_path, do_lower_case=False)
    bert_encoder = BertEncoder.from_pretrained(model_args.bert_path)
    vocabs['bert_tokenizer'] = bert_tokenizer

    model = Parser(
        vocabs=vocabs,
        word_char_dim=model_args.word_char_dim,
        word_dim=model_args.word_dim,
        char2word_dim=model_args.char2word_dim,
        pos_dim=model_args.pos_dim,
        ner_dim=model_args.ner_dim,
        concept_char_dim=model_args.concept_char_dim,
        concept_dim=model_args.concept_dim,
        cnn_filters=model_args.cnn_filters,
        char2concept_dim=model_args.char2concept_dim,
        embed_dim=model_args.embed_dim,
        ff_embed_dim=model_args.ff_embed_dim,
        num_heads=model_args.num_heads,
        dropout=model_args.dropout,
        snt_layers=model_args.snt_layers,
        graph_layers=model_args.graph_layers,
        inference_layers=model_args.inference_layers,
        rel_dim=model_args.rel_dim,
        pretrained_file=model_args.pretrained_file,
        bert_encoder=bert_encoder,
        device=device
    )

    # test_data = DataLoader(vocabs, lexical_mapping, args.test_data, args.test_batch_size, for_train=True)
    another_test_data = DataLoader(
        vocabs,
        lexical_mapping,
        args.test_data,
        args.test_batch_size,
        for_train=False
    )
    for test_model in test_models:
        print(test_model)
        batch = int(re.search(r'batch([0-9])+', test_model)[0][5:])
        epoch = int(re.search(r'epoch([0-9])+', test_model)[0][5:])

        load_ckpt_without_bert(model, test_model, device)
        model = model.to(device)
        model.eval()
        # loss = show_progress(model, test_data)
        pp = PostProcessor(vocabs['rel'])
        logger.info('start parsing')
        start_time = time.time()
        parse_data(
            model, pp,
            another_test_data,
            args.test_data,
            test_model + args.output_suffix,
            args.beam_size,
            args.alpha,
            args.max_time_step
        )
        end_time = time.time()
        logger.info(f'done! time: {end_time - start_time}')
