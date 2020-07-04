#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# == 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/train.py \
    --tok_vocab data/ucca/vocabs/tok_vocab \
    --tok_char_vocab data/ucca/vocabs/tok_char_vocab \
    --lem_vocab data/ucca/vocabs/lem_vocab \
    --lem_char_vocab data/ucca/vocabs/lem_char_vocab \
    --rel_vocab data/ucca/vocabs/rel_vocab \
    --upos_vocab data/ucca/vocabs/upos_vocab \
    --ner_vocab data/ucca/vocabs/xpos_vocab \
    --concept_vocab data/ucca/vocabs/concept_vocab \
    --concept_char_vocab data/ucca/vocabs/concept_char_vocab \
    --predictable_concept_vocab data/ucca/vocabs/predictable_concept_vocab \
    --train_data data/ucca/ucca.train.convert \
    --dev_data data/ucca/ucca.valid.convert \
    --bert_path ./bert-base-cased \
    --word_dim 300 \
    --word_char_dim 32 \
    --concept_char_dim 32 \
    --concept_dim 300 \
    --rel_dim 100 \
    --pos_dim 32 \
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
    --epochs 20000 \
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