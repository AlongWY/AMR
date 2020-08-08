#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path drg_deu_ckpt/epoch20499_batch81999 \
    --test_data data/drg_deu.input
else
  echo "$0 [CUDA DEVICES]"
fi