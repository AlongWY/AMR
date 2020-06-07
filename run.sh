#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# == 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/train.py \
    --tok_vocab data/tok_vocab \
    --tok_char_vocab data/tok_char_vocab \
    --lem_vocab data/lem_vocab \
    --lem_char_vocab data/lem_char_vocab \
    --rel_vocab data/rel_vocab \
    --concept_vocab data/concept_vocab \
    --concept_char_vocab data/concept_char_vocab \
    --predictable_concept_vocab data/predictable_concept_vocab \
    --train_data data/amr.train.json \
    --dev_data data/amr.dev.json \
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