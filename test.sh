#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path drg_deu_all_ckpt/epoch7708_batch34999 \
    --test_data data/drg_deu.input
else
  echo "$0 [CUDA DEVICES]"
fi