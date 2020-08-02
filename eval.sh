#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path amr_ckpt/epoch535_batch154999 \
    --test_data data/amr/amr.test.convert.input_clean.recategorize.nosense
else
  echo "$0 [CUDA DEVICES]"
fi