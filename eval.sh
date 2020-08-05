#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path drg_ckpt/epoch749_batch20999 \
    --test_data data/test.input
else
  echo "$0 [CUDA DEVICES]"
fi