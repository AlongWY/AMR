#!/bin/bash
# -*- coding: utf-8 -*_
# Author: Yunlong Feng <ylfeng@ir.hit.edu.cn>

if [ $# -eq 1 ]; then
  CUDA_VISIBLE_DEVICES=$1 PYTHONPATH=. python amr_parser/work.py \
    --load_path amr_zh_ckpt/epoch752_batch90999 \
    --test_data data/amr_zh.input
else
  echo "$0 [CUDA DEVICES]"
fi