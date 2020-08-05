#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path amr_ckpt/epoch342_batch98999 \
    --test_data data/test.input.recategorize
else
  echo "$0 [CUDA DEVICES]"
fi