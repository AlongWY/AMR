import os
from amr_clean.postprocess.wikification import Wikification
from amr_clean.node_utils import NodeUtilities as NU
from amr_clean.postprocess.expander import Expander
from amr_clean.postprocess.node_restore import NodeRestore


def postprocess(x):
    file_path, util_dir = x
    print(file_path, util_dir)
    node_utils = NU.from_json(util_dir, 0)

    nr = NodeRestore(node_utils)
    with open(file_path + '.frame', 'w', encoding='utf-8') as f:
        for amr in nr.restore_file(file_path):
            f.write(str(amr) + '\n\n')

    wikification = Wikification(util_dir=util_dir)
    wikification.load_utils()
    with open(file_path + '.frame.wiki', 'w', encoding='utf-8') as f:
        for amr in wikification.wikify_file(file_path + '.frame'):
            f.write(str(amr) + '\n\n')

    expander = Expander(util_dir=util_dir)
    with open(file_path + '.post', 'w', encoding='utf-8') as f:
        for amr in expander.expand_file(file_path + '.frame.wiki'):
            f.write(str(amr) + '\n\n')

    os.remove(file_path + '.frame')
    os.remove(file_path + '.frame.wiki')


if __name__ == '__main__':
    import argparse, os
    from multiprocessing import Pool

    parser = argparse.ArgumentParser('node_restore.py')
    parser.add_argument('--amr_path', default='amr_ckpt/amr.test.pred')
    parser.add_argument('--util_dir', default='data/amr/utils')
    parser.add_argument('--nprocessors', default=4, type=int)

    args = parser.parse_args()

    amr_files = []
    if os.path.isdir(args.amr_path):
        for file in os.listdir(args.amr_path):
            if not file.endswith('.pred'):
                continue
            fname = os.path.join(args.amr_path, file)
            if os.path.isfile(fname):
                amr_files.append((fname, args.util_dir))
    else:
        amr_files = [(args.amr_path, args.util_dir)]

    postprocess(amr_files[0])

    # pool = Pool(args.nprocessors)
    # pool.map(postprocess, amr_files)
