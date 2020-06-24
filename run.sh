#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# == 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/train.py \
    --tok_vocab data/vocabs/tok_vocab \
    --tok_char_vocab data/vocabs/tok_char_vocab \
    --lem_vocab data/vocabs/lem_vocab \
    --lem_char_vocab data/vocabs/lem_char_vocab \
    --rel_vocab data/vocabs/rel_vocab \
    --pos_vocab data/vocabs/upos_vocab \
    --ner_vocab data/vocabs/ner_vocab \
    --concept_vocab data/vocabs/concept_vocab \
    --concept_char_vocab data/vocabs/concept_char_vocab \
    --predictable_concept_vocab data/vocabs/predictable_concept_vocab \
    --train_data data/amr.train.convert.input_clean.recategorize \
    --dev_data data/amr.valid.convert.input_clean.recategorize \
    --bert_path ./bert-base-cased \
    --word_dim 300 \
    --word_char_dim 32 \
    --concept_char_dim 32 \
    --concept_dim 300 \
    --rel_dim 100 \
    --pos_dim 32 \
    --ner_dim 16 \
    --cnn_filter 3 256 \
    --char2word_dim 128 \
    --char2concept_dim 128 \
    --embed_dim 512 \
    --ff_embed_dim 1024 \
    --num_heads 8 \
    --snt_layers 4 \
    --graph_layers 2 \
    --inference_layers 4 \
    --dropout 0.2 \
    --unk_rate 0.33 \
    --epochs 100000 \
    --train_batch_size 6000 \
    --dev_batch_size 6000 \
    --lr_scale 1. \
    --warmup_steps 2000 \
    --print_every 100 \
    --eval_every 1000 \
    --batches_per_update 1 \
    --ckpt ckpt \
    --world_size 3 \
    --gpus 3
else
  echo "$0 [CUDA DEVICES]"
fi