# AMR Parsing via Graph-Sequence Iterative Inference

**AMR Parsing via Graph-Sequence Iterative Inference** [[preprint]](http://arxiv.org/abs/2004.05572) By Deng Cai and Wai Lam.

## Requirements

The code has been tested on **Python 3.6**.

All dependencies are listed in [requirements.txt](requirements.txt).

### Data Preparation

1. python -u -m amr_clean.preprocess.input_cleaner --amr_files ${train_data} ${dev_data} ${test_data}
2. python -u -m amr_clean.preprocess.recategorizer --dump_dir ${util_dir} --amr_files ${train_data}.input_clean ${dev_data}.input_clean
3. python -u -m amr_clean.preprocess.text_anonymizor --amr_file ${test_data}.input_clean --util_dir ${util_dir}
4. python -u -m amr_clean.preprocess.sense_remover --util_dir ${util_dir} --amr_files ${train_data}.input_clean.recategorize ${dev_data}.input_clean.recategorize ${test_data}.input_clean.recategorize

### Post Process

1. python3 -u -m amr_clean.postprocess.postprocess --amr_path ${test_data} --util_dir ${util_dir}